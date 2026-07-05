from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Numeric, String, Text, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.audit import AuditMixin
from app.models.base import BaseModel
from app.models.enums import (
    AIRecommendationPriority,
    AIRecommendationType,
    DecisionStatus,
)

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.dataset import Dataset
    from app.models.analysis_result import AnalysisResult


class AIRecommendation(BaseModel, AuditMixin):
    """
    Represents an AI-generated recommendation.
    """

    __tablename__ = "ai_recommendations"

    # ------------------------------------------------------------------
    # Foreign Keys
    # ------------------------------------------------------------------

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id"),
        nullable=False,
        index=True,
    )

    # Relaxed to nullable so decision-cards can exist without a source
    # dataset/analysis (see contract decision-cards -> ai_recommendations).
    dataset_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("datasets.id"),
        nullable=True,
        index=True,
    )

    analytics_result_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("analysis_results.id"),
        nullable=True,
        index=True,
    )

    # Workspace scoping for decision-cards (resolves the card's sector).
    workspace_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id"),
        nullable=True,
        index=True,
    )

    # ------------------------------------------------------------------
    # Recommendation Information
    # ------------------------------------------------------------------

    recommendation_type: Mapped[AIRecommendationType] = mapped_column(
        Enum(
            AIRecommendationType,
            name="ai_recommendation_type_enum",
            values_callable=lambda enum: [e.value for e in enum],
        ),
        nullable=False,
    )

    # Decision-card title (contract DecisionCardOut.title).
    title: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    recommendation: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    confidence_score: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2),
        nullable=True,
    )

    # Decision-card lifecycle: pending -> approved/rejected.
    decision_status: Mapped[DecisionStatus] = mapped_column(
        Enum(
            DecisionStatus,
            name="decision_status_enum",
            values_callable=lambda enum: [e.value for e in enum],
        ),
        default=DecisionStatus.PENDING,
        server_default=DecisionStatus.PENDING.value,
        nullable=False,
    )

    resolved_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )

    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    priority: Mapped[AIRecommendationPriority] = mapped_column(
        Enum(
            AIRecommendationPriority,
            name="ai_recommendation_priority_enum",
            values_callable=lambda enum: [e.value for e in enum],
        ),
        nullable=False,
    )

    is_applied: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default="false",
        nullable=False,
    )

    metadata_json: Mapped[dict | None] = mapped_column(
        JSONB().with_variant(JSON, "sqlite"),
        nullable=True,
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="ai_recommendations",
        lazy="selectin",
    )

    dataset: Mapped["Dataset"] = relationship(
        "Dataset",
        back_populates="ai_recommendations",
        lazy="selectin",
    )

    analysis_result: Mapped["AnalysisResult"] = relationship(
        "AnalysisResult",
        back_populates="ai_recommendations",
        lazy="selectin",
    )
