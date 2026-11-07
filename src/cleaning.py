import html
import re
import unicodedata


def clean_text(text):
    """Make a description plain, normalized text."""
    if not text:
        return text
    text = html.unescape(text)                 # &amp; -> &, &eacute; -> é
    text = re.sub(r"<[^>]+>", " ", text)       # drop HTML tags
    text = unicodedata.normalize("NFC", text)  # one canonical form for accents
    text = text.replace("\u00a0", " ")         # non-breaking space -> space
    text = re.sub(r"[ \t]+", " ", text)        # collapse spaces
    text = re.sub(r"\n\s*\n+", "\n\n", text)   # at most one blank line
    return text.strip()


def _norm(value):
    """Lowercase, no accents, no punctuation, single spaces."""
    value = unicodedata.normalize("NFKD", value or "").lower()
    value = "".join(c for c in value if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", " ", value).strip()


def make_dedup_key(title, company, location):
    return "|".join(_norm(x) for x in (title, company, location))