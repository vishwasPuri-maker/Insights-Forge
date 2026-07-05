"""Sector dashboard routes: scorecard, timeseries, records, records/{id}.

One set of endpoints serves all four sectors; `{sector}` is a path parameter.
A user is fixed to one sector (carried in the JWT), so the caller may only read
their own sector — any mismatch is a 403. Every query runs under the
organization's RLS context and is also filtered by organization_id explicitly.

This layer only READS cleaned rows the external worker wrote into `records`; it
never cleans or computes ML — just shapes the rows into frontend-ready JSON.
"""
import uuid

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy import Date, cast, func, select
from sqlalchemy.orm import Session

from app.auth.jwt_handler import TokenData, get_current_user
from app.database import get_db, set_organization_context
from app.models import Dataset, DecisionCard, Record
from app.schemas import (
    ALLOWED_SECTORS,
    GeoFeature,
    GeoFeatureCollection,
    RecordOut,
    RecordsPage,
    ScorecardCard,
    ScorecardOut,
    TimeseriesOut,
    TimeseriesSeries,
)

router = APIRouter(prefix="/sectors", tags=["sectors"])


def _guard_sector(sector: str, current: TokenData) -> None:
    """Validate the path sector and that the caller is allowed to read it."""
    if sector not in ALLOWED_SECTORS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "unknown_sector", "message": f"no such sector: {sector}"},
        )
    if sector != current.sector:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "sector_forbidden", "message": "not your sector"},
        )


SectorPath = Path(..., description="one of retail | service | education | agriculture")


@router.get("/{sector}/scorecard", response_model=ScorecardOut)
def scorecard(
    sector: str = SectorPath,
    current: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ScorecardOut:
    _guard_sector(sector, current)
    set_organization_context(db, current.organization_id)
    org_id = uuid.UUID(current.organization_id)

    record_count = db.scalar(
        select(func.count(Record.id)).where(
            Record.organization_id == org_id, Record.sector == sector
        )
    )
    datasets_total = db.scalar(
        select(func.count(Dataset.id)).where(
            Dataset.organization_id == org_id, Dataset.sector == sector
        )
    )
    datasets_ready = db.scalar(
        select(func.count(Dataset.id)).where(
            Dataset.organization_id == org_id,
            Dataset.sector == sector,
            Dataset.status == "ready",
        )
    )
    avg_health = db.scalar(
        select(func.avg(Dataset.health_score)).where(
            Dataset.organization_id == org_id,
            Dataset.sector == sector,
            Dataset.health_score.is_not(None),
        )
    )
    pending_decisions = db.scalar(
        select(func.count(DecisionCard.id)).where(
            DecisionCard.organization_id == org_id,
            DecisionCard.sector == sector,
            DecisionCard.status == "pending",
        )
    )

    cards = [
        ScorecardCard(key="records", label="Cleaned Records", value=record_count or 0),
        ScorecardCard(key="datasets", label="Datasets", value=datasets_total or 0),
        ScorecardCard(key="datasets_ready", label="Datasets Ready", value=datasets_ready or 0),
        ScorecardCard(
            key="avg_health",
            label="Avg Data Health",
            value=round(float(avg_health), 2) if avg_health is not None else None,
            unit="%",
        ),
        ScorecardCard(
            key="pending_decisions", label="Pending Decisions", value=pending_decisions or 0
        ),
    ]
    return ScorecardOut(sector=sector, cards=cards)


@router.get("/{sector}/timeseries", response_model=TimeseriesOut)
def timeseries(
    sector: str = SectorPath,
    current: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TimeseriesOut:
    """Records per day for the sector (frontend-ready {labels, series})."""
    _guard_sector(sector, current)
    set_organization_context(db, current.organization_id)
    org_id = uuid.UUID(current.organization_id)

    # Bucket by the record's own date if present, else when we stored it.
    day = cast(func.coalesce(Record.recorded_at, Record.created_at), Date)
    rows = db.execute(
        select(day.label("day"), func.count(Record.id).label("n"))
        .where(Record.organization_id == org_id, Record.sector == sector)
        .group_by(day)
        .order_by(day)
    ).all()

    labels = [r.day.isoformat() for r in rows]
    values = [float(r.n) for r in rows]
    return TimeseriesOut(
        sector=sector,
        labels=labels,
        series=[TimeseriesSeries(name="records", values=values)],
    )


@router.get("/{sector}/records", response_model=RecordsPage)
def list_records(
    sector: str = SectorPath,
    current: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
) -> RecordsPage:
    _guard_sector(sector, current)
    set_organization_context(db, current.organization_id)
    org_id = uuid.UUID(current.organization_id)

    base = (Record.organization_id == org_id, Record.sector == sector)
    total = db.scalar(select(func.count(Record.id)).where(*base)) or 0
    items = list(
        db.scalars(
            select(Record)
            .where(*base)
            .order_by(Record.created_at.desc())
            .limit(limit)
            .offset(offset)
        ).all()
    )
    return RecordsPage(
        sector=sector,
        total=total,
        limit=limit,
        offset=offset,
        items=[RecordOut.model_validate(r) for r in items],
    )


def _coord(data: dict, *names: str) -> float | None:
    for n in names:
        v = data.get(n)
        if isinstance(v, (int, float)):
            return float(v)
    return None


@router.get("/{sector}/geo", response_model=GeoFeatureCollection)
def geo(
    sector: str = SectorPath,
    current: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = Query(1000, ge=1, le=5000),
) -> GeoFeatureCollection:
    """GeoJSON FeatureCollection built from records that carry coordinates.

    A record contributes a point if its `data` JSONB has lat/lng (accepts
    `lat`/`latitude` and `lng`/`lon`/`longitude`). Records without coords are
    skipped — no geocoding/ML here, just reshaping existing values.
    """
    _guard_sector(sector, current)
    set_organization_context(db, current.organization_id)
    rows = db.scalars(
        select(Record)
        .where(
            Record.organization_id == uuid.UUID(current.organization_id),
            Record.sector == sector,
        )
        .order_by(Record.created_at.desc())
        .limit(limit)
    ).all()

    features: list[GeoFeature] = []
    for r in rows:
        lat = _coord(r.data, "lat", "latitude")
        lng = _coord(r.data, "lng", "lon", "longitude")
        if lat is None or lng is None:
            continue
        props = {k: v for k, v in r.data.items()
                 if k not in {"lat", "latitude", "lng", "lon", "longitude"}}
        props["record_id"] = str(r.id)
        features.append(
            GeoFeature(geometry={"type": "Point", "coordinates": [lng, lat]}, properties=props)
        )
    return GeoFeatureCollection(sector=sector, features=features)


@router.get("/{sector}/records/{record_id}", response_model=RecordOut)
def get_record(
    record_id: uuid.UUID,
    sector: str = SectorPath,
    current: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Record:
    _guard_sector(sector, current)
    set_organization_context(db, current.organization_id)
    record = db.scalar(
        select(Record).where(
            Record.id == record_id,
            Record.organization_id == uuid.UUID(current.organization_id),
            Record.sector == sector,
        )
    )
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "not_found", "message": "record not found"},
        )
    return record
