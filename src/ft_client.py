"""France Travail API client: OAuth2 token handling."""
import logging
import time

import httpx

from src import config

log = logging.getLogger(__name__)


class TokenManager:
    """Fetches an OAuth2 token and renews it shortly before it expires."""

    def __init__(self, client_id: str, client_secret: str, margin: int = 60):
        self._client_id = client_id
        self._client_secret = client_secret
        self._margin = margin  # renew this many seconds early
        self._token = None
        self._expires_at = 0.0

    def get(self) -> str:
        """Return a valid token, requesting a new one only when needed."""
        if self._token is None or time.monotonic() >= self._expires_at:
            self._refresh()
        return self._token

    def _refresh(self) -> None:
        response = httpx.post(
            config.TOKEN_URL,
            params={"realm": "/partenaire"},
            data={
                "grant_type": "client_credentials",
                "client_id": self._client_id,
                "client_secret": self._client_secret,
                "scope": config.SCOPE,
            },
            timeout=30,
        )
        response.raise_for_status()  # raises an error on HTTP 4xx/5xx
        payload = response.json()
        self._token = payload["access_token"]
        self._expires_at = time.monotonic() + payload["expires_in"] - self._margin
        log.info("Token refreshed, valid for %s seconds", payload["expires_in"])
