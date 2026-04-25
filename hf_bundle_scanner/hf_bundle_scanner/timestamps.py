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


def report_timestamps_from_utc(dt: datetime) -> tuple[str, str]:
    """Return ``(utc_z, ist_iso)`` for the same instant (second precision, no microseconds)."""
    utc = dt.astimezone(timezone.utc).replace(microsecond=0)
    ist = timezone(timedelta(hours=5, minutes=30), name="IST")
    ist_dt = utc.astimezone(ist).replace(microsecond=0)
    utc_s = utc.isoformat().replace("+00:00", "Z")
    return utc_s, ist_dt.isoformat()


def now_report_timestamps() -> tuple[str, str]:
    """UTC ``Z`` + IST ``+05:30`` for *now*, derived from a single UTC clock reading."""
    return report_timestamps_from_utc(datetime.now(timezone.utc))
