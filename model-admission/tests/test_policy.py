from pathlib import Path

from model_admission.policy import PolicyConfig, evaluate_policy, sha256_file


def test_sha256_file(tmp_path: Path) -> None:
    p = tmp_path / "f.bin"
    p.write_bytes(b"hello")
    assert sha256_file(p) == "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"


def test_policy_forbidden_extension(tmp_path: Path) -> None:
    pol = PolicyConfig(
        max_bytes=1000,
        forbidden_extensions=[".pkl"],
    )
    bad = tmp_path / "m.pkl"
    bad.write_bytes(b"x")
    assert evaluate_policy(bad, pol)


def test_policy_allowlist(tmp_path: Path) -> None:
    pol = PolicyConfig(allowed_extensions=[".safetensors"])
    ok = tmp_path / "m.safetensors"
    ok.write_bytes(b"x")
    assert not evaluate_policy(ok, pol)
    bad = tmp_path / "m.pt"
    bad.write_bytes(b"x")
    assert evaluate_policy(bad, pol)


def test_policy_sha256_allowlist(tmp_path: Path) -> None:
    p = tmp_path / "m.bin"
    p.write_bytes(b"abc")
    h = sha256_file(p)
    pol = PolicyConfig(sha256_allowlist=[h])
    assert not evaluate_policy(p, pol)
    pol2 = PolicyConfig(sha256_allowlist=["deadbeef"])
    assert evaluate_policy(p, pol2)


def test_policy_load_roundtrip(tmp_path: Path) -> None:
    path = tmp_path / "p.json"
    path.write_text(
        '{"max_bytes": 100, "forbidden_extensions": [".pkl"]}',
        encoding="utf-8",
    )
    pol = PolicyConfig.load(path)
    assert pol.max_bytes == 100
