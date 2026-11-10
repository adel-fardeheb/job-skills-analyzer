import pandas as pd
from sqlalchemy import text

from src.db import get_engine

engine = get_engine()
df = pd.read_sql(text("SELECT * FROM offers"), engine)

dups = df[df["is_duplicate"]]
canon = df.set_index("source_id")

print("Flagged:", len(dups), "| not flagged:", (~df["is_duplicate"]).sum())

# 1. Every duplicate must point to an existing offer
missing = ~dups["duplicate_of"].isin(df["source_id"])
print("Pointing to a missing offer:", missing.sum())

# 2. No chains: the canonical offer must not itself be flagged
chained = canon.loc[dups["duplicate_of"], "is_duplicate"].sum()
print("Pointing to another duplicate (chains):", chained)

# 3. Canonical and duplicate must share the same dedup_key
same_key = (canon.loc[dups["duplicate_of"], "dedup_key"].values == dups["dedup_key"].values)
print("Different dedup_key from their canonical:", (~same_key).sum())

# 4. Canonical must be the older offer
older = canon.loc[dups["duplicate_of"], "created_at"].values <= dups["created_at"].values
print("Canonical newer than its duplicate:", (~older).sum())

# 5. Three flagged pairs to read
for _, d in dups.sample(3, random_state=1).iterrows():
    c = canon.loc[d["duplicate_of"]]
    print(f"\n=== {d['title']} | {d['company']} | {d['location']}")
    print(f"canonical {d['duplicate_of']} ({c['created_at']:%Y-%m-%d}): {c['description'][:250]!r}")
    print(f"duplicate {d['source_id']} ({d['created_at']:%Y-%m-%d}): {d['description'][:250]!r}")