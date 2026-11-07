import logging
import time

import httpx

log = logging.getLogger(__name__)

SEARCH_URL = "https://api.francetravail.io/partenaire/offresdemploi/v2/offres/search"
MAX_END = 1149  # the API refuses ranges beyond ~1,150 results


class OffersSearch:
    def __init__(self, token_manager, min_interval=0.4, max_retries=5, timeout=30.0):
        self.tokens = token_manager
        self.min_interval = min_interval  # 0.4 s = 2.5 req/s, under the declared 3/s
        self.max_retries = max_retries
        self.client = httpx.Client(timeout=timeout)
        self._last_call = 0.0

    def _throttle(self):
        wait = self.min_interval - (time.monotonic() - self._last_call)
        if wait > 0:
            time.sleep(wait)
        self._last_call = time.monotonic()

    def fetch_page(self, params, start, end):
        """One request, with throttling and retries. Returns (offers, total)."""
        query = {**params, "range": f"{start}-{end}"}
        for attempt in range(self.max_retries):
            self._throttle()
            headers = {"Authorization": f"Bearer {self.tokens.get()}"}
            try:
                r = self.client.get(SEARCH_URL, params=query, headers=headers)
            except httpx.TransportError as exc:
                log.warning("network error (%s), attempt %d", exc, attempt + 1)
                time.sleep(2 ** attempt)
                continue

            if r.status_code == 204:  # no result
                return [], 0
            if r.status_code in (200, 206):
                total = int(r.headers["Content-Range"].rsplit("/", 1)[-1])
                return r.json().get("resultats", []), total
            if r.status_code == 429 or r.status_code >= 500:
                delay = float(r.headers.get("Retry-After", 2 ** attempt))
                log.warning("HTTP %d, waiting %.1fs", r.status_code, delay)
                time.sleep(delay)
                continue
            r.raise_for_status()  # other 4xx: our mistake, do not retry
        raise RuntimeError(f"search failed after {self.max_retries} attempts")

    def iter_pages(self, params, page_size=150):
        """Yield one list of offers per page, until the results or the window run out."""
        start = 0
        while start <= MAX_END:
            end = min(start + page_size - 1, MAX_END)
            offers, total = self.fetch_page(params, start, end)
            if not offers:
                return
            yield start, offers
            start = end + 1
            if start >= total:
                return