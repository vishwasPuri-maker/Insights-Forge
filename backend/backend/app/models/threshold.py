from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class Threshold(BaseModel):
    """Workspace-scoped metric threshold (warning/critical) for a sector KPI."""

    __tablename__ = "thresholds"

    __table_args__ = (
        UniqueConstraint(
            "workspace_id",
            "metric_key",
            name="uq_thresholds_workspace_metric",
        ),
    )

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

    metric_key: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    label: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    warning_value: Mapped[float | None] = mapped_column(
        Numeric,
        nullable=True,
    )

    critical_value: Mapped[float | None] = mapped_column(
        Numeric,
        nullable=True,
    )
