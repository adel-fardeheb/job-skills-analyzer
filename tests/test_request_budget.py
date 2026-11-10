from datetime import datetime, timedelta, timezone

import pytest

from src.request_budget import BudgetExceeded, RequestBudget

NOW = datetime(2026, 11, 7, tzinfo=timezone.utc)


def test_cap_blocks_extra_requests(tmp_path):
    b = RequestBudget(tmp_path / "log.jsonl", cap=2)
    b.record(NOW)
    b.record(NOW)
    with pytest.raises(BudgetExceeded):
        b.record(NOW)


def test_old_requests_are_not_counted(tmp_path):
    b = RequestBudget(tmp_path / "log.jsonl", cap=2)
    old = NOW - timedelta(days=8)
    b.record(old)
    b.record(old)
    assert b.used(NOW) == 0
    b.record(NOW)  # allowed again