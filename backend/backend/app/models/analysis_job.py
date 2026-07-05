from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.audit import AuditMixin
from app.models.base import BaseModel
from app.models.enums import AnalysisJobStatus, AnalysisJobType

if TYPE_CHECKING:
    from app.models.dataset import Dataset
    from app.models.user import User
    from app.models.analysis_result import AnalysisResult


class AnalysisJob(BaseModel, AuditMixin):
    """
    Represents an analytics job executed on a dataset.
    """

    __tablename__ = "analysis_jobs"

    dataset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("datasets.id"),
        nullable=False,
        index=True,
    )

    initiated_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    job_type: Mapped[AnalysisJobType] = mapped_column(
        Enum(
            AnalysisJobType,
            name="analysis_job_type_enum",
            values_callable=lambda enum: [e.value for e in enum],
        ),
        nullable=False,
    )

    status: Mapped[AnalysisJobStatus] = mapped_column(
        Enum(
            AnalysisJobStatus,
            name="analysis_job_status_enum",
            values_callable=lambda enum: [e.value for e in enum],
        ),
        default=AnalysisJobStatus.PENDING,
        server_default=AnalysisJobStatus.PENDING.value,
        nullable=False,
    )

    progress: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default="0",
        nullable=False,
    )

    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    dataset: Mapped["Dataset"] = relationship(
        "Dataset",
        back_populates="analysis_jobs",
        lazy="selectin",
    )

    initiated_user: Mapped["User"] = relationship(
        "User",
        back_populates="analysis_jobs",
        foreign_keys=[initiated_by],
        lazy="selectin",
    )

    results: Mapped[list["AnalysisResult"]] = relationship(
        "AnalysisResult",
        back_populates="job",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
