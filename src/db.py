import os
from datetime import datetime

from dotenv import load_dotenv
from sqlalchemy import DateTime, String, Text, create_engine
from sqlalchemy.dialects.postgresql import JSONB, insert
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

load_dotenv()


class Base(DeclarativeBase):
    pass


class Offer(Base):
    __tablename__ = "offers"

    source: Mapped[str] = mapped_column(String(30), primary_key=True)
    source_id: Mapped[str] = mapped_column(String(60), primary_key=True)
    title: Mapped[str | None] = mapped_column(Text)
    company: Mapped[str | None] = mapped_column(Text)
    location: Mapped[str | None] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(Text)
    url: Mapped[str | None] = mapped_column(Text)
    contract_type: Mapped[str | None] = mapped_column(String(30))
    rome_code: Mapped[str | None] = mapped_column(String(10))
    rome_label: Mapped[str | None] = mapped_column(Text)
    experience: Mapped[str | None] = mapped_column(Text)
    source_skills: Mapped[list | None] = mapped_column(JSONB)
    language: Mapped[str | None] = mapped_column(String(5))
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    collected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


def get_engine():
    return create_engine(os.environ["DATABASE_URL"])


def upsert_offers(conn, rows):
    """Insert rows (list of dicts); on a key conflict, update the other columns.""" 
    if not rows:
        return 0
    stmt = insert(Offer).values(rows)
    keys = {"source", "source_id"}
    stmt = stmt.on_conflict_do_update(
        index_elements=["source", "source_id"],
        set_={c: stmt.excluded[c] for c in rows[0] if c not in keys},
    )
    conn.execute(stmt)
    return len(rows)