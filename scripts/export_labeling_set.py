import json
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.db import Offer, get_engine
from src.labeling import sample_offers

OUTPUT = Path("data/labels/labeled_set.json")
SEED = 42
N_EXTRA = 5


def main():
    if OUTPUT.exists():
        raise SystemExit(f"{OUTPUT} already exists, not overwriting your labels.")

    with Session(get_engine()) as session:
        rows = session.scalars(
            select(Offer).where(Offer.is_duplicate.is_(False))
        ).all()
        offers = [
            {
                "source": o.source,
                "source_id": o.source_id,
                "rome_code": o.rome_code,
                "title": o.title,
                "url": o.url,
                "description": o.description,
            }
            for o in rows
        ]

    sample = sample_offers(offers, n_extra=N_EXTRA, seed=SEED)
    for offer in sample:
        offer["skills"] = []

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(sample, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    codes = {o["rome_code"] for o in sample}
    print(f"{len(sample)} offers written to {OUTPUT} ({len(codes)} distinct ROME codes)")


if __name__ == "__main__":
    main()