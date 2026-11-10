import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path

log = logging.getLogger(__name__)

LOG_FILE = Path("data/request_log.jsonl")
WEEKLY_CAP = 470
WINDOW_DAYS = 7


class BudgetExceeded(RuntimeError):
    pass


class RequestBudget:
    def __init__(self, path=LOG_FILE, cap=WEEKLY_CAP, window_days=WINDOW_DAYS):
        self.path = Path(path)
        self.cap = cap
        self.window = timedelta(days=window_days)

    def used(self, now=None):
        """Number of requests logged in the last window."""
        if not self.path.exists():
            return 0
        limit = (now or datetime.now(timezone.utc)) - self.window
        with self.path.open(encoding="utf-8") as f:
            return sum(
                1 for line in f
                if line.strip() and datetime.fromisoformat(line.strip()) >= limit
            )

    def record(self, now=None):
        """Log one request, or raise if the cap is reached."""
        now = now or datetime.now(timezone.utc)
        used = self.used(now)
        if used >= self.cap:
            raise BudgetExceeded(f"{used} requests in the last 7 days (cap {self.cap})")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as f:
            f.write(now.isoformat() + "\n")