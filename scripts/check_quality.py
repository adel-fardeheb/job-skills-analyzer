import pandas as pd
from sqlalchemy import text

from src.db import get_engine

engine = get_engine()

# 1. Whole table in a DataFrame (6k rows is small, so this is fine in memory)
df = pd.read_sql(text("SELECT * FROM offers"), engine)
print(f"Total rows: {len(df)}")

# 2. Offers per ROME code vs the count study
counts = pd.read_csv("data/counts_rome_national.csv")
counts = counts[counts["date"] == counts["date"].max()]  # latest study only

in_db = df.groupby("rome_code").size().rename("in_db")
cmp = counts.set_index("code")[["label", "total"]].join(in_db, how="outer")
cmp["diff"] = cmp["in_db"].fillna(0) - cmp["total"].fillna(0)

print(cmp.sort_values("diff").to_string())
print("Sum of diffs:", cmp["diff"].sum())

# 3. Empty fields: share of null or blank values per column
blank = df.replace(r"^\s*$", pd.NA, regex=True).isna().mean().mul(100).round(1)
print("\n% empty per column:")
print(blank.sort_values(ascending=False).to_string())

# 4. Description length
df["desc_len"] = df["description"].fillna("").str.len()
print("\nDescription length (characters):")
print(df["desc_len"].describe().round(0).to_string())
print("Descriptions under 200 characters:", (df["desc_len"] < 200).sum())

# 5. Duplicate dedup_key groups
dup = df[df.duplicated("dedup_key", keep=False)]
print(f"\nRows in a duplicate group: {len(dup)} ({dup['dedup_key'].nunique()} groups)")
print("Group sizes:")
print(dup.groupby("dedup_key").size().value_counts().sort_index().to_string())

# Duplicates among offers WITH a company vs WITHOUT
dup_no_company = dup["company"].isna().sum()
print("Rows in a duplicate group with no company:", dup_no_company)

# A few examples
cols = ["dedup_key", "title", "company", "location", "rome_code", "source_id"]
print(dup.sort_values("dedup_key")[cols].head(12).to_string())

# 6. Descriptions at the 5000-character ceiling
print("\nDescriptions of exactly 5000 characters:", (df["desc_len"] == 5000).sum())

import re

def words(text):
    return set(re.findall(r"\w+", (text or "").lower()))

def jaccard(a, b):
    wa, wb = words(a), words(b)
    return len(wa & wb) / len(wa | wb) if (wa | wb) else 1.0

# 7. Compare each duplicate with the first row of its group
rows = []
for key, g in dup.groupby("dedup_key"):
    g = g.sort_values(["created_at", "source_id"])
    ref = g.iloc[0]
    for _, r in g.iloc[1:].iterrows():
        rows.append({
            "dedup_key": key,
            "source_id": r["source_id"],
            "has_company": pd.notna(r["company"]),
            "ref_id": ref["source_id"],
            "exact": r["description"] == ref["description"],
            "jaccard": jaccard(ref["description"], r["description"]),
        })
sim = pd.DataFrame(rows)

print(f"\nCompared rows: {len(sim)}")
print("Identical descriptions:", sim["exact"].sum())
bins = pd.cut(sim["jaccard"], [0, 0.5, 0.8, 0.95, 1.0], include_lowest=True)
print(pd.crosstab(bins, sim["has_company"]).to_string())
print(sim.sort_values("jaccard").head(5).to_string())

# 8. Eyeball 3 pairs from the ambiguous band (0.5 < jaccard <= 0.8)
band = sim[(sim["jaccard"] > 0.5) & (sim["jaccard"] <= 0.8)]
by_id = df.set_index("source_id")

for _, p in band.sample(3, random_state=0).iterrows():
    a, b = by_id.loc[p["ref_id"]], by_id.loc[p["source_id"]]
    print(f"\n=== {p['dedup_key']} | jaccard={p['jaccard']:.2f}")
    print(f"A ({p['ref_id']}): {a['description'][:500]!r}")
    print(f"B ({p['source_id']}): {b['description'][:500]!r}")