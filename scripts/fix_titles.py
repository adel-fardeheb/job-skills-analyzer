from sqlalchemy import text

from src.db import get_engine

engine = get_engine()

# Same condition for the count and the update: title has whitespace at an edge
WHERE = "title ~ '^\\s|\\s$'"

with engine.begin() as conn:
    before = conn.execute(text(f"SELECT count(*) FROM offers WHERE {WHERE}")).scalar()
    conn.execute(text(
        f"UPDATE offers "
        f"SET title = NULLIF(regexp_replace(title, '^\\s+|\\s+$', '', 'g'), '') "
        f"WHERE {WHERE}"
    ))
    after = conn.execute(text(f"SELECT count(*) FROM offers WHERE {WHERE}")).scalar()

print(f"titles with edge whitespace: {before} -> {after}")