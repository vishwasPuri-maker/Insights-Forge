"""Report endpoints — compile (async-style stub) + fetch.

The frozen contract's ``report_type`` is a free string and it expects a
``download_url``; the official ``reports`` model uses a fixed enum and has no
url column, so the contract-facing values live in ``report_config``.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session, lazyload

from app.api.deps import CurrentUser, get_current_user
from app.core.errors import AppError
from app.db.session import get_db
from app.models.enums import ReportStatus, ReportType
from app.models.report import Report
from app.schemas.report import ReportCompileRequest, ReportOut

router = APIRouter(prefix="/reports", tags=["Reports"])


def to_out(report: Report, sector: str) -> ReportOut:
    cfg = report.report_config or {}
    return ReportOut(
        id=report.id,
        sector=sector,
        report_type=cfg.get("report_type", report.report_type.value),
        status=cfg.get("status", "ready"),
        download_url=cfg.get("download_url"),
        created_at=report.created_at,
    )


@router.post("/compile", response_model=ReportOut, status_code=status.HTTP_202_ACCEPTED)
def compile_report(
    payload: ReportCompileRequest,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ReportOut:
    report = Report(
        organization_id=current.organization_id,
        workspace_id=current.workspace_id,
        report_name=payload.report_type,
        report_type=ReportType.CUSTOM,
        status=ReportStatus.ACTIVE,
        report_config={
            "report_type": payload.report_type,
            "status": "ready",
            "params": payload.params or {},
        },
        created_by=current.id,
    )
    db.add(report)
    db.flush()
    report.report_config = {
        **report.report_config,
        "download_url": f"/downloads/reports/{report.id}.pdf",
    }
    db.commit()
    return to_out(report, current.sector)


@router.get("/{report_id}", response_model=ReportOut)
def get_report(
    report_id: uuid.UUID,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ReportOut:
    report = db.get(Report, report_id, options=[lazyload("*")])
    if (
        report is None
        or report.is_deleted
        or report.workspace_id != current.workspace_id
    ):
        raise AppError(404, "not_found", "Report not found")
    return to_out(report, current.sector)
