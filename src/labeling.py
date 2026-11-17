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


def validate_labels(entries):
    """Return a list of problems found in the labeled entries (empty = valid)."""
    problems = []
    seen_ids = set()

    for entry in entries:
        sid = entry.get("source_id", "<no id>")

        if sid in seen_ids:
            problems.append(f"{sid}: duplicated offer")
        seen_ids.add(sid)

        skills = entry.get("skills")
        if not isinstance(skills, list):
            problems.append(f"{sid}: 'skills' is not a list")
            continue

        for skill in skills:
            if not isinstance(skill, str) or not skill.strip():
                problems.append(f"{sid}: empty or non-text skill {skill!r}")
            elif skill != skill.strip().lower():
                problems.append(f"{sid}: not lowercase or has edge spaces: {skill!r}")

        if len(skills) != len(set(skills)):
            problems.append(f"{sid}: duplicated skills in the same offer")

    return problems