import pandas as pd
from sqlalchemy import text

from src.db import get_engine

engine = get_engine()
df = pd.read_sql(text("SELECT source_id, title, description FROM offers"), engine)

# Each pattern is a symptom of an incomplete cleaning step
PATTERNS = {
    "html tag": r"<[a-zA-Z/][^>]*>",
    "html entity": r"&(?:[a-zA-Z]+|#\d+);",
    "mojibake (UTF-8 read as Latin-1)": "Ã[\u0080-\u00bf]|â€|Â[\u00a0-\u00bf]",
    "replacement char": "\ufffd",
    "non-breaking / zero-width space": "[\u00a0\u200b\u200c\ufeff]",
    "4+ consecutive newlines": r"\n{4,}",
    "leading/trailing whitespace": r"^\s|\s$",
}

for col in ("description", "title"):
    print(f"\n##### {col}")
    s = df[col].fillna("")
    for name, pat in PATTERNS.items():
        mask = s.str.contains(pat, regex=True)
        print(f"{name:35s} {mask.sum():5d} rows")
        if mask.any() and col == "description":
            ex = s[mask].iloc[0]
            m = pd.Series([ex]).str.extract(f"(.{{0,30}}(?:{pat}).{{0,30}})", expand=False).iloc[0]
            print(f"    e.g. {df.loc[mask, 'source_id'].iloc[0]}: {m!r}")