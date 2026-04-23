from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class PolicyConfig:
    """JSON policy file. Unknown keys are ignored for forward compatibility."""

    max_bytes: int = 50 * 1024**3  # 50 GiB default cap
    allowed_extensions: list[str] | None = None  # if set, extension must be in list (lowercase)
    forbidden_extensions: list[str] | None = None  # reject if suffix matches
    sha256_allowlist: list[str] | None = None  # if non-empty, file hash must be listed

    @classmethod
    def load(cls, path: Path) -> PolicyConfig:
        data = json.loads(path.read_text(encoding="utf-8"))
        default_max = 50 * 1024**3
        return cls(
            max_bytes=int(data.get("max_bytes", default_max)),
            allowed_extensions=data.get("allowed_extensions"),
            forbidden_extensions=data.get("forbidden_extensions"),
            sha256_allowlist=data.get("sha256_allowlist"),
        )

    def content_hash(self) -> str:
        """Stable hash of normalized policy for ledger."""
        blob = json.dumps(
            {
                "max_bytes": self.max_bytes,
                "allowed_extensions": self.allowed_extensions,
                "forbidden_extensions": self.forbidden_extensions,
                "sha256_allowlist": self.sha256_allowlist,
            },
            sort_keys=True,
        ).encode()
        return hashlib.sha256(blob).hexdigest()


def sha256_file(path: Path, chunk: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def evaluate_policy(artifact: Path, policy: PolicyConfig) -> list[str]:
    """Return list of human-readable violations (empty => pass)."""
    errors: list[str] = []
    if not artifact.exists():
        return [f"artifact does not exist: {artifact}"]
    if not artifact.is_file():
        return [f"artifact is not a regular file: {artifact}"]
    size = artifact.stat().st_size
    if size > policy.max_bytes:
        errors.append(f"size {size} exceeds max_bytes {policy.max_bytes}")
    suffix = artifact.suffix.lower()
    if policy.forbidden_extensions and suffix in {
        x.lower() for x in policy.forbidden_extensions
    }:
        errors.append(f"extension {suffix!r} is forbidden by policy")
    if policy.allowed_extensions is not None:
        allowed = {x.lower() for x in policy.allowed_extensions}
        if suffix not in allowed:
            errors.append(f"extension {suffix!r} not in allowed_extensions")
    digest = sha256_file(artifact)
    if policy.sha256_allowlist is not None and len(policy.sha256_allowlist) > 0:
        allow = {x.lower() for x in policy.sha256_allowlist}
        if digest.lower() not in allow:
            errors.append("sha256 not in sha256_allowlist")
    return errors
