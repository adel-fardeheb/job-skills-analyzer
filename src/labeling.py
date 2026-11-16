import random
from collections import defaultdict


def sample_offers(offers, n_extra=5, seed=42):
    """Pick one offer per ROME code, then n_extra more at random.

    offers: list of dicts with at least 'source_id' and 'rome_code'.
    Returns a list of dicts, reproducible for a given seed.
    """
    rng = random.Random(seed)

    by_code = defaultdict(list)
    for offer in offers:
        by_code[offer["rome_code"]].append(offer)

    chosen = []
    chosen_ids = set()

    for code in sorted(by_code):
        pick = rng.choice(by_code[code])
        chosen.append(pick)
        chosen_ids.add(pick["source_id"])

    remaining = [o for o in offers if o["source_id"] not in chosen_ids]
    n_extra = min(n_extra, len(remaining))
    chosen.extend(rng.sample(remaining, n_extra))

    return chosen