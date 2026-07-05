from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict, Union

class DynamicBaseModel(BaseModel):
    class Config:
        extra = 'allow'

class Body_stream_upload_api_v1_ingestion_stream_post(DynamicBaseModel):
    sector: str
    file: str

class DatasetOut(DynamicBaseModel):
    id: str
    sector: str
    original_filename: str
    status: str
    health_score: Optional[Any] = None
    size_bytes: Optional[Any] = None
    content_type: Optional[Any] = None
    uploaded_by: str
    created_at: str

class DecisionCardOut(DynamicBaseModel):
    id: str
    sector: str
    title: str
    recommendation: Optional[Any] = None
    confidence_score: Optional[Any] = None
    status: str
    resolved_by: Optional[Any] = None
    resolved_at: Optional[Any] = None
    created_at: str

class GeoFeature(DynamicBaseModel):
    type: Optional[str] = None
    geometry: Dict[str, Any]
    properties: Dict[str, Any]

class GeoFeatureCollection(DynamicBaseModel):
    type: Optional[str] = None
    sector: str
    features: List[Any]

class HTTPValidationError(DynamicBaseModel):
    detail: Optional[List[Any]] = None

class IngestionResponse(DynamicBaseModel):
    dataset_id: str
    sector: str
    status: str
    size_bytes: Optional[Any] = None

class LoginRequest(DynamicBaseModel):
    email: str
    password: str

class RecordOut(DynamicBaseModel):
    id: str
    dataset_id: str
    sector: str
    data: Dict[str, Any]
    recorded_at: Optional[Any] = None
    created_at: str

class RecordsPage(DynamicBaseModel):
    sector: str
    total: int
    limit: int
    offset: int
    items: List[Any]

class RefreshRequest(DynamicBaseModel):
    refresh_token: str

class ReportCompileRequest(DynamicBaseModel):
    report_type: str
    params: Optional[Any] = None

class ReportOut(DynamicBaseModel):
    id: str
    sector: str
    report_type: str
    status: str
    download_url: Optional[Any] = None
    created_at: str

class ScorecardCard(DynamicBaseModel):
    key: str
    label: str
    value: Optional[Any] = None
    unit: Optional[Any] = None

class ScorecardOut(DynamicBaseModel):
    sector: str
    cards: List[Any]

class SignupRequest(DynamicBaseModel):
    organization_name: str
    email: str
    password: str
    sector: str

class SimulateMetric(DynamicBaseModel):
    key: str
    current: float
    change_pct: Optional[float] = None

class SimulateProjection(DynamicBaseModel):
    key: str
    current: float
    projected: float
    change_pct: float

class SimulateRequest(DynamicBaseModel):
    metrics: List[Any]

class SimulateResponse(DynamicBaseModel):
    sector: str
    projections: List[Any]
    total_current: float
    total_projected: float

class ThresholdOut(DynamicBaseModel):
    id: str
    sector: str
    metric_key: str
    label: str
    warning_value: Optional[Any] = None
    critical_value: Optional[Any] = None

class ThresholdUpdate(DynamicBaseModel):
    warning_value: Optional[Any] = None
    critical_value: Optional[Any] = None

class TimeseriesOut(DynamicBaseModel):
    sector: str
    labels: List[Any]
    series: List[Any]

class TimeseriesSeries(DynamicBaseModel):
    name: str
    values: List[Any]

class TokenResponse(DynamicBaseModel):
    access_token: str
    refresh_token: str
    token_type: Optional[str] = None

class UserCreate(DynamicBaseModel):
    email: str
    password: str
    role: Optional[str] = None
    sector: str

class UserOut(DynamicBaseModel):
    id: str
    organization_id: str
    email: str
    role: str
    sector: str
    created_at: str

class ValidationError(DynamicBaseModel):
    loc: List[Any]
    msg: str
    type: str
    input: Optional[Any] = None
    ctx: Optional[Dict[str, Any]] = None
