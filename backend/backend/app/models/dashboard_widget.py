from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.audit import AuditMixin
from app.models.base import BaseModel
from app.models.enums import (
    ChartType,
    WidgetStatus,
    WidgetType,
)

if TYPE_CHECKING:
    from app.models.dashboard import Dashboard


class DashboardWidget(BaseModel, AuditMixin):
    """
    Represents a widget placed on a dashboard.
    """

    __tablename__ = "dashboard_widgets"

    # ------------------------------------------------------------------
    # Foreign Keys
    # ------------------------------------------------------------------

    dashboard_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("dashboards.id"),
        nullable=False,
        index=True,
    )

    # ------------------------------------------------------------------
    # Widget Information
    # ------------------------------------------------------------------

    widget_type: Mapped[WidgetType] = mapped_column(
        Enum(
            WidgetType,
            name="widget_type_enum",
            values_callable=lambda enum: [e.value for e in enum],
        ),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    chart_type: Mapped[ChartType] = mapped_column(
        Enum(
            ChartType,
            name="chart_type_enum",
            values_callable=lambda enum: [e.value for e in enum],
        ),
        nullable=False,
    )

    data_source: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    position: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
    )

    settings: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    status: Mapped[WidgetStatus] = mapped_column(
        Enum(
            WidgetStatus,
            name="widget_status_enum",
            values_callable=lambda enum: [e.value for e in enum],
        ),
        default=WidgetStatus.ACTIVE,
        server_default=WidgetStatus.ACTIVE.value,
        nullable=False,
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    dashboard: Mapped["Dashboard"] = relationship(
        "Dashboard",
        back_populates="widgets",
        lazy="selectin",
    )
