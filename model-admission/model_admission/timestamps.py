"""Timestamp helpers for admit-model JSON reports."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone


def utc_now_iso_z() -> str:
    dt = datetime.now(timezone.utc).replace(microsecond=0)
    s = dt.isoformat()
    return s.replace("+00:00", "Z")


def ist_now_iso() -> str:
    ist = timezone(timedelta(hours=5, minutes=30), name="IST")
    return datetime.now(ist).replace(microsecond=0).isoformat()
