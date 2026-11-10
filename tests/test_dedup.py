from datetime import datetime, timezone

from src.dedup import find_duplicates, similarity


def words(prefix, n=20):
    """n distinct words: prefix0 prefix1 ..., so we control the exact similarity."""
    return " ".join(f"{prefix}{i}" for i in range(n))


def row(source_id, description, day=1, key="k"):
    return {
        "source": "ft",
        "source_id": source_id,
        "dedup_key": key,
        "description": description,
        "created_at": datetime(2026, 11, day, tzinfo=timezone.utc) if day else None,
    }


# --- similarity ---

def test_similarity_values():
    assert similarity("a b c", "a b c") == 1.0
    assert similarity("a b c", "a b d") == 0.5
    assert similarity("a b", "c d") == 0.0


def test_similarity_empty_is_zero():
    assert similarity("", "") == 0.0
    assert similarity(None, None) == 0.0


# --- threshold behavior ---

def test_identical_repost_is_flagged():
    rows = [row("A", words("w"), day=1), row("B", words("w"), day=2)]
    assert find_duplicates(rows) == {("ft", "B"): "A"}


def test_small_edit_is_flagged():
    # 1 word changed out of 20: 19 shared / 21 distinct = 0.905 >= 0.9
    edited = words("w", 19) + " other"
    rows = [row("A", words("w"), day=1), row("B", edited, day=2)]
    assert find_duplicates(rows) == {("ft", "B"): "A"}


def test_bigger_edit_is_not_flagged():
    # 2 words changed: 18 shared / 22 distinct = 0.818 < 0.9
    edited = words("w", 18) + " other1 other2"
    rows = [row("A", words("w"), day=1), row("B", edited, day=2)]
    assert find_duplicates(rows) == {}


# --- edge cases ---

def test_empty_descriptions_are_not_flagged():
    rows = [row("A", "", day=1), row("B", "", day=2), row("C", None, day=3)]
    assert find_duplicates(rows) == {}


def test_rows_without_key_are_ignored():
    rows = [row("A", words("w"), key=None), row("B", words("w"), day=2, key=None)]
    assert find_duplicates(rows) == {}


def test_different_keys_are_never_compared():
    rows = [row("A", words("w"), key="k1"), row("B", words("w"), day=2, key="k2")]
    assert find_duplicates(rows) == {}


# --- who is the canonical offer ---

def test_oldest_is_canonical_whatever_the_input_order():
    rows = [row("B", words("w"), day=2), row("A", words("w"), day=1)]
    assert find_duplicates(rows) == {("ft", "B"): "A"}


def test_missing_date_sorts_last():
    rows = [row("A", words("w"), day=None), row("B", words("w"), day=5)]
    assert find_duplicates(rows) == {("ft", "A"): "B"}


def test_same_date_uses_source_id_as_tie_breaker():
    rows = [row("B", words("w"), day=1), row("A", words("w"), day=1)]
    assert find_duplicates(rows) == {("ft", "B"): "A"}


# --- groups ---

def test_three_way_group_points_to_one_canonical():
    rows = [row(i, words("w"), day=d) for i, d in (("A", 1), ("B", 2), ("C", 3))]
    assert find_duplicates(rows) == {("ft", "B"): "A", ("ft", "C"): "A"}


def test_distinct_offers_sharing_a_key_keep_their_own_reposts():
    rows = [
        row("A", words("a"), day=1),
        row("B", words("b"), day=2),   # same key, different text: not a duplicate
        row("A2", words("a"), day=3),  # repost of A
        row("B2", words("b"), day=4),  # repost of B
    ]
    assert find_duplicates(rows) == {("ft", "A2"): "A", ("ft", "B2"): "B"}