"""Sector analytics schemas — frozen by contract.

ScorecardOut, TimeseriesOut and GeoFeatureCollection are shaped for direct
frontend consumption (KPI tiles, chart labels+series, GeoJSON).
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class ScorecardCard(BaseModel):
    key: str
    label: str
    value: float | int | str | None = None
    unit: str | None = None


class ScorecardOut(BaseModel):
    sector: str
    cards: list[ScorecardCard]


class TimeseriesSeries(BaseModel):
    name: str
    values: list[float]


class TimeseriesOut(BaseModel):
    sector: str
    labels: list[str]
    series: list[TimeseriesSeries]


class GeoFeature(BaseModel):
    type: str = "Feature"
    geometry: dict[str, Any]
    properties: dict[str, Any]


class GeoFeatureCollection(BaseModel):
    type: str = "FeatureCollection"
    sector: str
    features: list[GeoFeature]
