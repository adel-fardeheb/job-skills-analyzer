import logging
import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path

from sqlalchemy import delete

from src.db import Offer

log = logging.getLogger(__name__)

RETENTION_DAYS = 183  # about 6 months


def cutoff(now=None, days=RETENTION_DAYS):
    return (now or datetime.now(timezone.utc)) - timedelta(days=days)


def purge_offers(conn, now=None):
    """Delete offers not (re)collected since the cutoff. Returns the count."""
    result = conn.execute(delete(Offer).where(Offer.collected_at < cutoff(now)))
    log.info("purged %d offers", result.rowcount)
    return result.rowcount


def purge_raw(raw_dir=Path("data/raw"), now=None):
    """Delete dated raw folders (YYYY-MM-DD) older than the cutoff."""
    if not raw_dir.exists():
        return 0
    limit = cutoff(now).date()
    removed = 0
    for folder in raw_dir.iterdir():
        try:
            day = datetime.strptime(folder.name, "%Y-%m-%d").date()
        except ValueError:
            continue  # not a dated folder: never touch it
        if folder.is_dir() and day < limit:
            shutil.rmtree(folder)
            removed += 1
    log.info("purged %d raw folders", removed)
    return removed