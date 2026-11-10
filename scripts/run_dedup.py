import logging

from src.db import get_engine
from src.dedup import apply_duplicates

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

engine = get_engine()
with engine.begin() as conn:  # commits on success, rolls back on error
    n = apply_duplicates(conn)

log.info("dedup done: %d offers flagged as duplicates", n)