"""Market data service logic: upsert, retention, timeseries read, and a demo
data generator (stands in for the real scraper until a live source is wired)."""

from __future__ import annotations

import math
import random
from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert

from market_service.db import MarketRecord, SessionLocal

RETENTION_POINTS = 400  # keep the most recent N points per (sector, metric)


def _prune(db, sector: str) -> None:
    """Keep only the most recent RETENTION_POINTS rows per (sector, metric).
    Point-count (not date) based, so daily series stay bounded AND sparse
    historical series (e.g. yearly education index back to 1990) are preserved."""
    metrics = [
        m[0]
        for m in db.query(MarketRecord.metric)
        .filter(MarketRecord.sector == sector)
        .distinct()
        .all()
    ]
    for metric in metrics:
        keep_ids = [
            r[0]
            for r in db.query(MarketRecord.id)
            .filter(MarketRecord.sector == sector, MarketRecord.metric == metric)
            .order_by(MarketRecord.day.desc())
            .limit(RETENTION_POINTS)
            .all()
        ]
        if keep_ids:
            db.query(MarketRecord).filter(
                MarketRecord.sector == sector,
                MarketRecord.metric == metric,
                MarketRecord.id.notin_(keep_ids),
            ).delete(synchronize_session=False)


def upsert_points(sector: str, points: list[dict], source: str) -> int:
    """points: [{day: date, value: float, metric?: str}]. Daily-upsert — one row
    per (sector, metric, day). Returns number of rows written."""
    if SessionLocal is None:
        raise RuntimeError("MARKET_DATABASE_URL is not set")
    db = SessionLocal()
    try:
        n = 0
        for p in points:
            metric = p.get("metric", "market_index")
            stmt = (
                pg_insert(MarketRecord)
                .values(
                    sector=sector,
                    metric=metric,
                    day=p["day"],
                    value=float(p["value"]),
                    source=source,
                )
                .on_conflict_do_update(
                    constraint="uq_market_sector_metric_day",
                    set_={"value": float(p["value"]), "source": source},
                )
            )
            db.execute(stmt)
            n += 1
        _prune(db, sector)
        db.commit()
        return n
    finally:
        db.close()


def get_timeseries(sector: str, metric: str = "market_index") -> dict:
    """Returns {sector, labels, series} — same shape the product/frontend expect."""
    if SessionLocal is None:
        return {"sector": sector, "labels": [], "series": []}
    db = SessionLocal()
    try:
        rows = db.execute(
            select(MarketRecord.day, MarketRecord.value)
            .where(MarketRecord.sector == sector, MarketRecord.metric == metric)
            .order_by(MarketRecord.day)
        ).all()
        labels = [str(d) for d, _ in rows]
        values = [float(v) for _, v in rows]
        series = [{"name": "Market", "values": values}] if values else []
        return {"sector": sector, "labels": labels, "series": series}
    finally:
        db.close()


def refresh_from_source(sector: str) -> int:
    """Scrape the sector's live free source and upsert the points. Returns the
    number of rows written (0 if the source was unreachable/empty — the caller
    treats that as a graceful no-op)."""
    from market_service import adapters

    points = adapters.fetch(sector)
    if not points:
        return 0
    return upsert_points(sector, points, source=f"scraper:{sector}")


def generate_demo(sector: str, days: int = 120) -> int:
    """Deprecated fallback (synthetic walk). Kept for local testing only."""
    random.seed(hash(sector) & 0xFFFF)
    start = date.today() - timedelta(days=days)
    base = 100.0
    points = []
    for i in range(days):
        base *= 1 + random.uniform(-0.012, 0.016)
        seasonal = 8 * math.sin(i / 18)
        points.append({"day": start + timedelta(days=i), "value": round(base + seasonal, 2)})
    return upsert_points(sector, points, source="demo-generator")
