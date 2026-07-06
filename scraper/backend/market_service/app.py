"""Market Data Microservice — a standalone FastAPI with its OWN Neon database.

Serves benchmark/market timeseries to the product backend over HTTP and lets a
scrape/refresh be triggered on demand. Runs as a separate process from the
product API (true microservice; DB isolation).

Run:
  MARKET_DATABASE_URL=postgresql://... \
    ./venv/bin/python -m uvicorn market_service.app:app --port 8100
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from market_service import service
from market_service.db import init_db

app = FastAPI(title="InsightForge Market Data Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # internal service; product calls it server-side
    allow_methods=["*"],
    allow_headers=["*"],
)

_VALID_SECTORS = {"retail", "service", "education", "agriculture"}


@app.on_event("startup")
def _startup() -> None:
    try:
        init_db()
    except Exception as e:  # pragma: no cover - surfaced in logs
        print(f"[market-service] init_db skipped: {e}")


class TimeseriesOut(BaseModel):
    sector: str
    labels: list[str]
    series: list[dict]


class RefreshOut(BaseModel):
    sector: str
    written: int
    status: str


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "market-data"}


@app.get("/market/{sector}/timeseries", response_model=TimeseriesOut)
def market_timeseries(sector: str) -> TimeseriesOut:
    if sector not in _VALID_SECTORS:
        return TimeseriesOut(sector=sector, labels=[], series=[])
    return TimeseriesOut(**service.get_timeseries(sector))


@app.post("/market/{sector}/refresh", response_model=RefreshOut)
def market_refresh(sector: str) -> RefreshOut:
    """Trigger a live market-data scrape for the sector from its free public
    source (Yahoo/TradingEconomics/commodityonline/Wikipedia), upsert into the
    market DB, and report how many rows were written."""
    if sector not in _VALID_SECTORS:
        return RefreshOut(sector=sector, written=0, status="invalid_sector")
    written = service.refresh_from_source(sector)
    return RefreshOut(
        sector=sector, written=written, status="ok" if written else "no_data"
    )
