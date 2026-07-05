"""Pydantic request/response models."""
import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

# v1 supports exactly these four sectors. A user is fixed to one sector.
Sector = Literal["retail", "service", "education", "agriculture"]
ALLOWED_SECTORS: frozenset[str] = frozenset({"retail", "service", "education", "agriculture"})


class SignupRequest(BaseModel):
    organization_name: str = Field(min_length=1, max_length=255)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    sector: Sector


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: str
    organization_id: str
    email: EmailStr
    role: str
    sector: str


class IngestionResponse(BaseModel):
    dataset_id: str
    sector: str
    status: str
    size_bytes: int | None = None


class DatasetOut(BaseModel):
    """Dataset lifecycle view: status + health score for the frontend to poll."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    sector: str
    original_filename: str
    status: str
    health_score: float | None = None
    size_bytes: int | None = None
    content_type: str | None = None
    uploaded_by: uuid.UUID
    created_at: datetime


# --- Sector dashboards ---


class ScorecardCard(BaseModel):
    """One KPI tile on a sector scorecard."""

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
    """Frontend-ready chart shape: labels + one or more named series."""

    sector: str
    labels: list[str]
    series: list[TimeseriesSeries]


class RecordOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    dataset_id: uuid.UUID
    sector: str
    data: dict
    recorded_at: datetime | None = None
    created_at: datetime


class RecordsPage(BaseModel):
    """Paginated list of cleaned records."""

    sector: str
    total: int
    limit: int
    offset: int
    items: list[RecordOut]


# --- Decision cards ---


class DecisionCardOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    sector: str
    title: str
    recommendation: str | None = None
    confidence_score: float | None = None
    status: str
    resolved_by: uuid.UUID | None = None
    resolved_at: datetime | None = None
    created_at: datetime


# --- Geo (map) ---


class GeoFeature(BaseModel):
    type: Literal["Feature"] = "Feature"
    geometry: dict  # {"type": "Point", "coordinates": [lng, lat]}
    properties: dict


class GeoFeatureCollection(BaseModel):
    """GeoJSON FeatureCollection the frontend map can consume directly."""

    type: Literal["FeatureCollection"] = "FeatureCollection"
    sector: str
    features: list[GeoFeature]


# --- What-if simulator ---


class SimulateMetric(BaseModel):
    key: str = Field(min_length=1, max_length=64)
    current: float
    change_pct: float = 0.0


class SimulateRequest(BaseModel):
    metrics: list[SimulateMetric] = Field(min_length=1)


class SimulateProjection(BaseModel):
    key: str
    current: float
    projected: float
    change_pct: float


class SimulateResponse(BaseModel):
    sector: str
    projections: list[SimulateProjection]
    total_current: float
    total_projected: float


# --- Reports ---


class ReportCompileRequest(BaseModel):
    report_type: str = Field(min_length=1, max_length=64)
    params: dict | None = None


class ReportOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    sector: str
    report_type: str
    status: str
    download_url: str | None = None
    created_at: datetime


# --- KPI thresholds ---


class ThresholdOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    sector: str
    metric_key: str
    label: str
    warning_value: float | None = None
    critical_value: float | None = None


class ThresholdUpdate(BaseModel):
    warning_value: float | None = None
    critical_value: float | None = None


# --- User management ---


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    role: Literal["user", "manager", "admin"] = "user"
    sector: Sector


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    email: EmailStr
    role: str
    sector: str
    created_at: datetime
