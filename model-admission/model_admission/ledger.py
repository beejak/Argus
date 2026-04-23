from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def append_ledger(
    path: Path | None,
    record: dict[str, Any],
) -> None:
    if path is None:
        p = os.environ.get("MODEL_ADMISSION_LEDGER")
        if not p:
            return
        path = Path(p)
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(
        {
            "ts": datetime.now(timezone.utc).isoformat(),
            **record,
        },
        separators=(",", ":"),
    )
    with path.open("a", encoding="utf-8") as f:
        f.write(line + "\n")
