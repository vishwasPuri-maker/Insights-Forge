from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel
from app.models.enums import VisualizationType

if TYPE_CHECKING:
    from app.models.analysis_job import AnalysisJob
    from app.models.dataset import Dataset
    from app.models.ai_recommendation import AIRecommendation


class AnalysisResult(BaseModel):
    """
    Stores analysis output generated from an analysis job.
    """

    __tablename__ = "analysis_results"

    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("analysis_jobs.id"),
        nullable=False,
        index=True,
    )

    dataset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("datasets.id"),
        nullable=False,
        index=True,
    )

    metric_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    metric_value: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
    )

    visualization_type: Mapped[VisualizationType | None] = mapped_column(
        Enum(
            VisualizationType,
            name="visualization_type_enum",
            values_callable=lambda enum: [e.value for e in enum],
        ),
        nullable=True,
    )

    job: Mapped["AnalysisJob"] = relationship(
        "AnalysisJob",
        back_populates="results",
        lazy="selectin",
    )

    dataset: Mapped["Dataset"] = relationship(
        "Dataset",
        back_populates="analysis_results",
        lazy="selectin",
    )

    ai_recommendations: Mapped[list["AIRecommendation"]] = relationship(
        "AIRecommendation",
        back_populates="analysis_result",
        lazy="selectin",
    )
