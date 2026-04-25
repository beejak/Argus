"""Small timestamp helpers for machine-readable reports.

We stamp reports with both:
- UTC RFC3339 with ``Z`` suffix (second precision)
- IST (Asia/Kolkata, UTC+05:30) ISO-8601 with ``+05:30`` suffix (second precision)

This matches the HTML exporter's IST header while keeping UTC easy for correlation.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone


def utc_now_iso_z() -> str:
    dt = datetime.now(timezone.utc).replace(microsecond=0)
    # ``isoformat()`` yields ``+00:00``; normalize to ``Z`` for stable grep / tooling.
    s = dt.isoformat()
    return s.replace("+00:00", "Z")


def ist_now_iso() -> str:
    ist = timezone(timedelta(hours=5, minutes=30), name="IST")
    return datetime.now(ist).replace(microsecond=0).isoformat()
