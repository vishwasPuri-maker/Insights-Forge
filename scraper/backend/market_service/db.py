"""Market microservice DB layer — its OWN Neon database, fully isolated from
the product database. Market/scraped data lives here and nowhere else, so the
product DB can never fill up with benchmark data."""

from __future__ import annotations

import os

from sqlalchemy import (
    Column,
    Date,
    DateTime,
    Float,
    Integer,
    String,
    UniqueConstraint,
    create_engine,
    func,
)
from sqlalchemy.orm import declarative_base, sessionmaker

# Neon URL: prefer the environment, else read scraper/backend/.env directly so
# the service "just works" from that folder without manual `export` (and without
# shell `&`-splitting the URL). We normalise to the psycopg3 driver and drop the
# channel_binding param (libpq-only, not understood by the DBAPI layer).
def _load_market_url() -> str:
    url = os.environ.get("MARKET_DATABASE_URL", "").strip()
    if url:
        return url
    # scraper/backend/.env is two levels up from this file.
    env_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"
    )
    try:
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("MARKET_DATABASE_URL="):
                    return line.split("=", 1)[1].strip().strip("'\"")
    except OSError:
        pass
    return ""


_RAW_URL = _load_market_url()


def _normalise(url: str) -> str:
    if not url:
        return url
    url = url.replace("&channel_binding=require", "").replace(
        "channel_binding=require&", ""
    )
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


engine = create_engine(_normalise(_RAW_URL), pool_pre_ping=True) if _RAW_URL else None
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False) if engine else None

Base = declarative_base()


class MarketRecord(Base):
    """One benchmark data point per (sector, metric, day). Daily-upsert keeps
    exactly one row per day per metric, so the table size is bounded."""

    __tablename__ = "market_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sector = Column(String(32), index=True, nullable=False)
    metric = Column(String(64), nullable=False, default="market_index")
    day = Column(Date, index=True, nullable=False)
    value = Column(Float, nullable=False)
    source = Column(String(120), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("sector", "metric", "day", name="uq_market_sector_metric_day"),
    )


def init_db() -> None:
    """Create tables on first run (no Alembic needed for a single-table service)."""
    if engine is None:
        raise RuntimeError("MARKET_DATABASE_URL is not set")
    Base.metadata.create_all(engine)
