from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.audit import AuditMixin
from app.models.base import BaseModel
from app.models.enums import (
    ReportStatus,
    ReportType,
)

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.workspace import Workspace
    from app.models.report_export import ReportExport


class Report(BaseModel, AuditMixin):
    """
    Represents a generated report configuration.
    """

    __tablename__ = "reports"

    # ------------------------------------------------------------------
    # Foreign Keys
    # ------------------------------------------------------------------

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id"),
        nullable=False,
        index=True,
    )

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id"),
        nullable=False,
        index=True,
    )

    # ------------------------------------------------------------------
    # Report Information
    # ------------------------------------------------------------------

    report_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    report_type: Mapped[ReportType] = mapped_column(
        Enum(
            ReportType,
            name="report_type_enum",
            values_callable=lambda enum: [e.value for e in enum],
        ),
        nullable=False,
    )

    report_config: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
    )

    status: Mapped[ReportStatus] = mapped_column(
        Enum(
            ReportStatus,
            name="report_status_enum",
            values_callable=lambda enum: [e.value for e in enum],
        ),
        default=ReportStatus.ACTIVE,
        server_default=ReportStatus.ACTIVE.value,
        nullable=False,
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="reports",
        lazy="selectin",
    )

    workspace: Mapped["Workspace"] = relationship(
        "Workspace",
        back_populates="reports",
        lazy="selectin",
    )

    exports: Mapped[list["ReportExport"]] = relationship(
        "ReportExport",
        back_populates="report",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
