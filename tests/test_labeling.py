from src.labeling import sample_offers


def make_offers(codes_and_counts):
    """Build fake offers: {'A1': 3, 'B2': 2} -> 3 offers for A1, 2 for B2."""
    offers = []
    for code, count in codes_and_counts.items():
        for i in range(count):
            offers.append({"source_id": f"{code}-{i}", "rome_code": code})
    return offers


POOL = make_offers({"A1": 10, "B2": 10, "C3": 10, "D4": 1})


def test_one_offer_per_code_is_always_included():
    result = sample_offers(POOL, n_extra=0)
    codes = [o["rome_code"] for o in result]
    assert sorted(codes) == ["A1", "B2", "C3", "D4"]


def test_total_size_is_codes_plus_extra():
    result = sample_offers(POOL, n_extra=5)
    assert len(result) == 4 + 5


def test_no_offer_is_picked_twice():
    result = sample_offers(POOL, n_extra=20)
    ids = [o["source_id"] for o in result]
    assert len(ids) == len(set(ids))


def test_same_seed_gives_same_sample():
    first = sample_offers(POOL, n_extra=5, seed=1)
    second = sample_offers(POOL, n_extra=5, seed=1)
    assert [o["source_id"] for o in first] == [o["source_id"] for o in second]


def test_different_seed_gives_different_sample():
    first = sample_offers(POOL, n_extra=5, seed=1)
    second = sample_offers(POOL, n_extra=5, seed=2)
    assert [o["source_id"] for o in first] != [o["source_id"] for o in second]


def test_extra_is_capped_when_pool_is_small():
    small = make_offers({"A1": 2, "B2": 1})
    result = sample_offers(small, n_extra=50)
    assert len(result) == 3  # every offer, no error