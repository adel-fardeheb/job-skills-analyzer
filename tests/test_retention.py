from datetime import datetime, timezone

from src.db import get_engine, upsert_offers
from src.retention import purge_offers, purge_raw

NOW = datetime(2026, 11, 7, tzinfo=timezone.utc)


def test_purge_raw_removes_only_old_dated_folders(tmp_path):
    (tmp_path / "2026-01-01").mkdir()   # older than 6 months
    (tmp_path / "2026-10-01").mkdir()   # recent
    (tmp_path / "notes").mkdir()        # not a date: must stay
    assert purge_raw(tmp_path, now=NOW) == 1
    assert sorted(p.name for p in tmp_path.iterdir()) == ["2026-10-01", "notes"]


def test_purge_offers_deletes_old_rows_then_rolls_back():
    old = datetime(2025, 1, 1, tzinfo=timezone.utc)
    rows = [
        {"source": "test", "source_id": "old", "collected_at": old},
        {"source": "test", "source_id": "new", "collected_at": NOW},
    ]
    with get_engine().connect() as conn:
        trans = conn.begin()
        try:
            upsert_offers(conn, rows)
            purge_offers(conn, now=NOW)
            left = conn.exec_driver_sql(
                "select source_id from offers where source = 'test'"
            ).scalars().all()
            assert left == ["new"]
        finally:
            trans.rollback()  # the test leaves nothing in the real table