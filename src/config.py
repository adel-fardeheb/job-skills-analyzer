import os

from dotenv import load_dotenv

load_dotenv()  # copies the variables of the .env file into os.environ


def require(name: str) -> str:
    """Return an environment variable, or fail early with a clear message."""
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing environment variable: {name}")
    return value


# France Travail API
TOKEN_URL = "https://entreprise.francetravail.fr/connexion/oauth2/access_token"
API_BASE = "https://api.francetravail.io/partenaire/offresdemploi/v2"
SCOPE = "api_offresdemploiv2 o2dsoffre"

# Limits matching the usage declared to France Travail
MAX_REQUESTS_PER_RUN = 500
MAX_REQUESTS_PER_SECOND = 3
RETENTION_DAYS = 180  # about 6 months
