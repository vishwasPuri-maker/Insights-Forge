"""Report routes: POST /reports/compile and GET /reports/{id}.

Compilation runs asynchronously via FastAPI BackgroundTasks (no Celery). The
POST returns immediately with a `pending` report id; a background task marks it
`processing` then `ready` and sets a `download_url`. The frontend polls
GET /reports/{id} for status + the link.

No heavy data processing/ML here — the background task just assembles a report
artifact reference. Every query is org-scoped under RLS + explicit filtering.
"""
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.jwt_handler import TokenData, get_current_user
from app.database import SessionLocal, get_db, set_organization_context
from app.models import Report
from app.schemas import ReportCompileRequest, ReportOut

router = APIRouter(prefix="/reports", tags=["reports"])


def _compile_report(report_id: str, organization_id: str) -> None:
    """Background job: mark the report ready and attach a download link.

    Runs after the response is sent. Uses its own DB session (the request session
    is already closed by then).
    """
    db = SessionLocal()
    try:
        set_organization_context(db, organization_id)
        report = db.get(Report, uuid.UUID(report_id))
        if report is None:
            return
        report.status = "processing"
        db.commit()
        # (Real artifact assembly would happen here.) Record where to fetch it.
        report.status = "ready"
        report.download_url = f"/reports/{report_id}/download"
        db.commit()
    finally:
        db.close()


@router.post("/compile", response_model=ReportOut, status_code=status.HTTP_202_ACCEPTED)
def compile_report(
    body: ReportCompileRequest,
    background: BackgroundTasks,
    current: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Report:
    set_organization_context(db, current.organization_id)
    report = Report(
        organization_id=uuid.UUID(current.organization_id),
        sector=current.sector,
        report_type=body.report_type,
        params=body.params,
        status="pending",
        created_by=uuid.UUID(current.user_id),
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    background.add_task(_compile_report, str(report.id), current.organization_id)
    return report


@router.get("/{report_id}", response_model=ReportOut)
def get_report(
    report_id: uuid.UUID,
    current: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Report:
    set_organization_context(db, current.organization_id)
    report = db.scalar(
        select(Report).where(
            Report.id == report_id,
            Report.organization_id == uuid.UUID(current.organization_id),
        )
    )
    if report is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "not_found", "message": "report not found"},
        )
    return report
