from __future__ import annotations

from hf_bundle_scanner.report import compute_aggregate_exit, merge_aggregate_exit


def test_compute_aggregate_exit_priority() -> None:
    assert compute_aggregate_exit([0, 1, 0]) == 1
    assert compute_aggregate_exit([0, 2, 1]) == 2
    assert compute_aggregate_exit([4, 1]) == 4
    assert compute_aggregate_exit([]) == 0


def test_compute_aggregate_exit_all_clean() -> None:
    assert compute_aggregate_exit([0, 0, 0]) == 0


def test_compute_aggregate_exit_usage_error_dominates_driver_error() -> None:
    assert compute_aggregate_exit([2, 4]) == 4


def test_compute_aggregate_exit_usage_error_dominates_policy() -> None:
    assert compute_aggregate_exit([0, 1, 4]) == 4


def test_merge_aggregate_exit_config_escalates() -> None:
    assert merge_aggregate_exit(0, True) == 1
    assert merge_aggregate_exit(2, True) == 2


def test_merge_aggregate_exit_no_config_risk_unchanged() -> None:
    assert merge_aggregate_exit(0, False) == 0
    assert merge_aggregate_exit(1, False) == 1


def test_merge_aggregate_exit_usage_error_never_downgraded() -> None:
    assert merge_aggregate_exit(4, True) == 4
    assert merge_aggregate_exit(4, False) == 4
