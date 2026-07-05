from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.audit import AuditMixin
from app.models.base import BaseModel
from app.models.enums import (
    DatasetProcessingStatus,
    DatasetStatus,
)

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.workspace import Workspace
    from app.models.user import User
    from app.models.dataset_version import DatasetVersion
    from app.models.dataset_column import DatasetColumn
    from app.models.dataset_upload import DatasetUpload
    from app.models.analysis_job import AnalysisJob
    from app.models.analysis_result import AnalysisResult
    from app.models.ai_recommendation import AIRecommendation
    from app.models.forecast_model import ForecastModel


class Dataset(BaseModel, AuditMixin):
    """
    Represents a dataset uploaded into the platform.
    """

    __tablename__ = "datasets"

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

    uploaded_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    # ------------------------------------------------------------------
    # Dataset Information
    # ------------------------------------------------------------------

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    file_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    file_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    storage_path: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    checksum: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    storage_provider: Mapped[str] = mapped_column(
        String(50),
        default="Neon Storage",
        server_default="Neon Storage",
        nullable=False,
    )

    file_size: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )

    total_rows: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default="0",
        nullable=False,
    )

    total_columns: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default="0",
        nullable=False,
    )

    processing_status: Mapped[DatasetProcessingStatus] = mapped_column(
        Enum(
            DatasetProcessingStatus,
            name="dataset_processing_status_enum",
            values_callable=lambda enum: [e.value for e in enum],
        ),
        default=DatasetProcessingStatus.PENDING,
        server_default=DatasetProcessingStatus.PENDING.value,
        nullable=False,
    )

    status: Mapped[DatasetStatus] = mapped_column(
        Enum(
            DatasetStatus,
            name="dataset_status_enum",
            values_callable=lambda enum: [e.value for e in enum],
        ),
        default=DatasetStatus.ACTIVE,
        server_default=DatasetStatus.ACTIVE.value,
        nullable=False,
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="datasets",
        lazy="selectin",
    )

    workspace: Mapped["Workspace"] = relationship(
        "Workspace",
        back_populates="datasets",
        lazy="selectin",
    )

    uploader: Mapped["User"] = relationship(
        "User",
        back_populates="datasets",
        foreign_keys=[uploaded_by],
        lazy="selectin",
    )

    versions: Mapped[list["DatasetVersion"]] = relationship(
        "DatasetVersion",
        back_populates="dataset",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    columns: Mapped[list["DatasetColumn"]] = relationship(
        "DatasetColumn",
        back_populates="dataset",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    uploads: Mapped[list["DatasetUpload"]] = relationship(
        "DatasetUpload",
        back_populates="dataset",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    analysis_jobs: Mapped[list["AnalysisJob"]] = relationship(
        "AnalysisJob",
        back_populates="dataset",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    analysis_results: Mapped[list["AnalysisResult"]] = relationship(
        "AnalysisResult",
        back_populates="dataset",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    ai_recommendations: Mapped[list["AIRecommendation"]] = relationship(
        "AIRecommendation",
        back_populates="dataset",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    forecast_models: Mapped[list["ForecastModel"]] = relationship(
        "ForecastModel",
        back_populates="dataset",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
