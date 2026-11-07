import json
import logging
from datetime import datetime, timezone
from pathlib import Path

log = logging.getLogger(__name__)

RAW_DIR = Path("data/raw")


def save_raw(offers, label, start):
    """Write one page of raw offers to data/raw/<date>/<label>_<start>.json."""
    now = datetime.now(timezone.utc)
    folder = RAW_DIR / now.strftime("%Y-%m-%d")
    folder.mkdir(parents=True, exist_ok=True)

    safe_label = "".join(c if c.isalnum() or c in "-_" else "_" for c in label)
    path = folder / f"{safe_label}_{start:04d}.json"

    payload = {
        "collected_at": now.isoformat(),
        "label": label,
        "start": start,
        "offers": offers,
    }
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8") # ensure_ascii=False for proper UTF-8 encoding of French characters (é, è, à, etc.)
    log.info("saved %d offers to %s", len(offers), path)
    return path