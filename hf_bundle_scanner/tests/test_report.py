from __future__ import annotations

from hf_bundle_scanner.report import compute_aggregate_exit, merge_aggregate_exit


def test_compute_aggregate_exit_priority() -> None:
    assert compute_aggregate_exit([0, 1, 0]) == 1
    assert compute_aggregate_exit([0, 2, 1]) == 2
    assert compute_aggregate_exit([4, 1]) == 4
    assert compute_aggregate_exit([]) == 0


def test_merge_aggregate_exit_config_escalates() -> None:
    assert merge_aggregate_exit(0, True) == 1
    assert merge_aggregate_exit(2, True) == 2
