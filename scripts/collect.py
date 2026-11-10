import csv
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import text

from src import config
from src.db import get_engine, upsert_offers
from src.ft_client import TokenManager
from src.ft_mapping import ft_to_row
from src.ft_search import OffersSearch
from src.raw_store import save_raw
from src.request_budget import RequestBudget
from src.retention import purge_offers, purge_raw
from src.dedup import apply_duplicates

log = logging.getLogger("collect")
COUNTS = Path("data/counts_rome_national.csv")


def codes_to_collect():
    """ROME codes with at least one offer, from the latest count of each."""
    latest = {}
    with COUNTS.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            latest[row["code"]] = int(row["total"])  # later rows override earlier
    return [code for code, total in latest.items() if total > 0]


def main():
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s"
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)

    engine = get_engine()
    budget = RequestBudget()
    search = OffersSearch(
        TokenManager(
            config.require("FRANCE_TRAVAIL_CLIENT_ID"),
            config.require("FRANCE_TRAVAIL_CLIENT_SECRET"),
        ),
        budget=budget,
    )

    with engine.begin() as conn:
        purge_offers(conn)
    purge_raw()

    seen = 0
    for code in sys.argv[1:] or codes_to_collect():
        count = 0
        for start, offers in search.iter_pages({"codeROME": code}):
            save_raw(offers, f"rome_{code}", start)
            now = datetime.now(timezone.utc)
            rows = [ft_to_row(o, now) for o in offers]
            with engine.begin() as conn:
                count += upsert_offers(conn, rows)
        log.info("%s: %d offers", code, count)
        seen += count

    with engine.begin() as conn:
        flagged = apply_duplicates(conn)
    log.info("dedup: %d offers flagged as duplicates", flagged)    

    with engine.connect() as conn:
        total = conn.execute(text("select count(*) from offers")).scalar()
    log.info(
        "done: %d offers seen, %d in table, %d requests in the last 7 days",
        seen, total, budget.used(),
    )


if __name__ == "__main__":
    main()