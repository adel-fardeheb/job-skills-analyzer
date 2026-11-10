from sqlalchemy import text

from src.db import get_engine

engine = get_engine()

with engine.begin() as conn:
    conn.execute(text(
        "ALTER TABLE offers "
        "ADD COLUMN IF NOT EXISTS is_duplicate BOOLEAN NOT NULL DEFAULT FALSE"
    ))
    conn.execute(text(
        "ALTER TABLE offers ADD COLUMN IF NOT EXISTS duplicate_of TEXT"
    ))

print("columns ready")