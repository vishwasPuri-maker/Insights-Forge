"""Per-sector market-data scrapers. Each adapter returns a list of
``{"day": date, "value": float}`` points that the service upserts into the
market DB. All sources are free / public; no API keys.

Swappable by design: the service calls ``fetch(sector)`` and stores the result
— DB, retention, API and the product proxy never change.
"""

from __future__ import annotations

import io
import logging
from datetime import date, datetime, timedelta

import pandas as pd
import requests

logger = logging.getLogger("market-adapters")

_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0 Safari/537.36"
)
_HEADERS = {"User-Agent": _UA}
_TIMEOUT = 20


def _get_html(url: str) -> str:
    r = requests.get(url, headers=_HEADERS, timeout=_TIMEOUT)
    r.raise_for_status()
    return r.text


# --------------------------------------------------------------------------
# Retail — Yahoo Finance market index (^MKTX) via yfinance (handles auth).
# --------------------------------------------------------------------------
def fetch_retail() -> list[dict]:
    import yfinance as yf

    # XRT = SPDR S&P Retail ETF — the retail-sector market benchmark.
    # (^MKTX is delisted; XRT is the correct free proxy for "retail market".)
    hist = yf.Ticker("XRT").history(period="6mo", interval="1d")
    if hist is None or hist.empty:
        hist = yf.Ticker("^GSPC").history(period="6mo", interval="1d")
    if hist is None or hist.empty:
        return []
    points = []
    for idx, row in hist.iterrows():
        d = idx.date() if hasattr(idx, "date") else idx
        close = row.get("Close")
        if close is None or pd.isna(close):
            continue
        points.append({"day": d, "value": round(float(close), 2)})
    return points


# --------------------------------------------------------------------------
# Service — Trading Economics services-PMI country table (server-rendered).
# A snapshot table (one value per country) → we key it by today, plus keep the
# global average as the series point so it trends over successive refreshes.
# --------------------------------------------------------------------------
def fetch_service() -> list[dict]:
    html = _get_html("https://tradingeconomics.com/country-list/services-pmi")
    tables = pd.read_html(io.StringIO(html))
    # The populated table has generic integer columns; country is col 0 and the
    # "Last" PMI value is col 1. Take the global average PMI as today's point.
    for t in tables:
        if t.shape[0] >= 5 and t.shape[1] >= 2:
            vals = pd.to_numeric(t.iloc[:, 1], errors="coerce").dropna()
            if len(vals) >= 5:
                return [{"day": date.today(), "value": round(float(vals.mean()), 2)}]
    return []


# --------------------------------------------------------------------------
# Agriculture — commodityonline mandi prices (server-rendered HTML table).
# --------------------------------------------------------------------------
def fetch_agriculture() -> list[dict]:
    html = _get_html("https://www.commodityonline.com/mandiprices")
    try:
        tables = pd.read_html(io.StringIO(html))
    except ValueError:
        return []
    # Prices look like "Rs 3750 / Quintal" — pull digits from the "Avg price"
    # column and average across commodities as today's mandi index.
    for t in tables:
        cols = {str(c).strip().lower(): c for c in t.columns}
        price_col = cols.get("avg price") or cols.get("modal price") or cols.get("max price")
        if price_col is None:
            continue
        nums = (
            t[price_col]
            .astype(str)
            .str.replace(r"[^\d.]", "", regex=True)
            .replace("", None)
        )
        vals = pd.to_numeric(nums, errors="coerce").dropna()
        if len(vals) >= 3:
            return [{"day": date.today(), "value": round(float(vals.mean()), 2)}]
    return []


# --------------------------------------------------------------------------
# Education — Wikipedia Education Index (server-rendered wikitable, 190 rows,
# yearly columns). We emit the global mean index per available year.
# --------------------------------------------------------------------------
def fetch_education() -> list[dict]:
    html = _get_html("https://en.wikipedia.org/wiki/Education_Index")
    tables = pd.read_html(io.StringIO(html), match="Country")
    if not tables:
        return []
    t = tables[0]
    points = []
    for col in t.columns:
        year = str(col).strip()
        if not year.isdigit() or not (1990 <= int(year) <= 2100):
            continue
        vals = pd.to_numeric(t[col], errors="coerce").dropna()
        if len(vals) >= 5:
            # Use Jan 1 of that year as the point's day.
            points.append(
                {"day": date(int(year), 1, 1), "value": round(float(vals.mean()), 4)}
            )
    points.sort(key=lambda p: p["day"])
    return points


ADAPTERS = {
    "retail": fetch_retail,
    "service": fetch_service,
    "agriculture": fetch_agriculture,
    "education": fetch_education,
}


def fetch(sector: str) -> list[dict]:
    fn = ADAPTERS.get(sector)
    if fn is None:
        return []
    try:
        return fn()
    except Exception as e:  # network / parse failures shouldn't crash refresh
        logger.warning("adapter %s failed: %s", sector, e)
        return []
