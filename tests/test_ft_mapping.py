from datetime import datetime, timezone

from src.ft_mapping import ft_to_row

NOW = datetime(2026, 11, 7, tzinfo=timezone.utc)


def test_full_offer():
    offer = {
        "id": "ABC123",
        "intitule": "Data scientist",
        "entreprise": {"nom": "Acme"},
        "dateCreation": "2026-11-01T08:30:00.000Z",
    }
    row = ft_to_row(offer, NOW)
    assert row["source_id"] == "ABC123"
    assert row["company"] == "Acme"
    assert row["created_at"].year == 2026
    assert row["collected_at"] == NOW


def test_missing_nested_blocks():
    row = ft_to_row({"id": "X"}, NOW)
    assert row["company"] is None and row["url"] is None
    assert row["created_at"] is None

def test_title_is_stripped():
    row = ft_to_row({"id": "1", "intitule": "  Développeur Python (H/F) \n"}, NOW)
    assert row["title"] == "Développeur Python (H/F)"


def test_blank_or_missing_title_becomes_none():
    assert ft_to_row({"id": "1", "intitule": "   "}, NOW)["title"] is None
    assert ft_to_row({"id": "2"}, NOW)["title"] is None