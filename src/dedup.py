import re
from datetime import datetime, timezone
from sqlalchemy import bindparam, select, update, func

from src.db import Offer

THRESHOLD = 0.9


def _words(text):
    return frozenset(re.findall(r"\w+", (text or "").lower()))


def _jaccard(wa, wb):
    union = wa | wb
    return len(wa & wb) / len(union) if union else 0.0


def similarity(a, b):
    """Jaccard similarity of two texts: shared words / all distinct words."""
    return _jaccard(_words(a), _words(b))


def find_duplicates(rows, threshold=THRESHOLD):
    """rows: dicts with source, source_id, dedup_key, description, created_at.
    Returns {(source, source_id): canonical_source_id} for flagged rows only."""
    groups = {}
    for r in rows:
        if r["dedup_key"]:
            groups.setdefault(r["dedup_key"], []).append(r)

    far_future = datetime.max.replace(tzinfo=timezone.utc)
    flagged = {}
    for group in groups.values():
        if len(group) < 2:
            continue
        group.sort(key=lambda r: (r["created_at"] or far_future, r["source_id"]))
        canonicals = []  # list of (row, word_set)
        for r in group:
            words = _words(r["description"])  # computed once per row
            match = next(
                (c for c, cw in canonicals if _jaccard(cw, words) >= threshold),
                None,
            )
            if match:
                flagged[(r["source"], r["source_id"])] = match["source_id"]
            else:
                canonicals.append((r, words))
    return flagged


def apply_duplicates(conn, threshold=THRESHOLD):
    """Recompute duplicate flags in the database. Returns the number flagged."""
    # Only load rows whose dedup_key is shared by at least 2 offers
    shared_keys = (
        select(Offer.dedup_key)
        .where(Offer.dedup_key.is_not(None))
        .group_by(Offer.dedup_key)
        .having(func.count() > 1)
    )
    cols = [Offer.source, Offer.source_id, Offer.dedup_key,
            Offer.description, Offer.created_at]
    rows = [dict(r._mapping) for r in conn.execute(
        select(*cols).where(Offer.dedup_key.in_(shared_keys))
    )]

    flagged = find_duplicates(rows, threshold)

    # Reset everything, then apply the new flags (same transaction)
    conn.execute(update(Offer).values(is_duplicate=False, duplicate_of=None))
    if flagged:
        stmt = (
            update(Offer)
            .where(Offer.source == bindparam("b_source"),
                   Offer.source_id == bindparam("b_id"))
            .values(is_duplicate=True, duplicate_of=bindparam("b_canon"))
        )
        conn.execute(stmt, [
            {"b_source": s, "b_id": i, "b_canon": c}
            for (s, i), c in flagged.items()
        ])
    return len(flagged)