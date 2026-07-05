from __future__ import annotations

import uuid
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.audit import AuditMixin
from app.models.base import BaseModel
from app.models.enums import (
    ForecastAlgorithm,
    ForecastModelStatus,
)

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.dataset import Dataset
    from app.models.forecast_result import ForecastResult


class ForecastModel(BaseModel, AuditMixin):
    """
    Represents a trained forecasting model.
    """

    __tablename__ = "forecast_models"

    # ------------------------------------------------------------------
    # Foreign Keys
    # ------------------------------------------------------------------

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id"),
        nullable=False,
        index=True,
    )

    dataset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("datasets.id"),
        nullable=False,
        index=True,
    )

    # ------------------------------------------------------------------
    # Model Information
    # ------------------------------------------------------------------

    model_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    algorithm: Mapped[ForecastAlgorithm] = mapped_column(
        Enum(
            ForecastAlgorithm,
            name="forecast_algorithm_enum",
            values_callable=lambda enum: [e.value for e in enum],
        ),
        nullable=False,
    )

    target_column: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    parameters: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    accuracy: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2),
        nullable=True,
    )

    status: Mapped[ForecastModelStatus] = mapped_column(
        Enum(
            ForecastModelStatus,
            name="forecast_model_status_enum",
            values_callable=lambda enum: [e.value for e in enum],
        ),
        default=ForecastModelStatus.ACTIVE,
        server_default=ForecastModelStatus.ACTIVE.value,
        nullable=False,
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="forecast_models",
        lazy="selectin",
    )

    dataset: Mapped["Dataset"] = relationship(
        "Dataset",
        back_populates="forecast_models",
        lazy="selectin",
    )

    results: Mapped[list["ForecastResult"]] = relationship(
        "ForecastResult",
        back_populates="forecast_model",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
