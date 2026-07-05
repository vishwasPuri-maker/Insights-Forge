import uuid
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.ai_recommendation import AIRecommendation
from app.models.enums import AIRecommendationPriority, AIRecommendationType


class DecisionCardRepository:
    """
    Handles database operations for Decision Cards (AIRecommendation models).
    Keeps database operations extremely thin, focus on data access.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_decision_cards_by_workspace(
        self, workspace_id: uuid.UUID, organization_id: uuid.UUID, limit: int = 100
    ) -> list[AIRecommendation]:
        """
        Retrieves decision cards within a specific workspace, enforcing tenancy checks.
        """
        stmt = (
            select(AIRecommendation)
            .where(
                AIRecommendation.workspace_id == workspace_id,
                AIRecommendation.organization_id == organization_id,
                AIRecommendation.is_deleted.is_(False),
            )
            .limit(limit)
        )
        return list(self.db.execute(stmt).scalars().all())

    def create(
        self,
        organization_id: uuid.UUID,
        workspace_id: uuid.UUID,
        title: str,
        recommendation: str,
        confidence_score: float,
        priority: AIRecommendationPriority,
        recommendation_type: AIRecommendationType,
        metadata_json: dict,
        dataset_id: uuid.UUID | None = None,
    ) -> AIRecommendation:
        """
        Persists a new decision card into the database.
        """
        card = AIRecommendation(
            organization_id=organization_id,
            workspace_id=workspace_id,
            title=title,
            recommendation=recommendation,
            confidence_score=confidence_score,
            priority=priority,
            recommendation_type=recommendation_type,
            metadata_json=metadata_json,
            dataset_id=dataset_id,
        )
        self.db.add(card)
        return card

    def get(
        self,
        card_id: uuid.UUID,
        workspace_id: uuid.UUID,
    ) -> AIRecommendation | None:
        """
        Retrieves a single active decision card, scoped by workspace.
        """
        stmt = select(AIRecommendation).where(
            AIRecommendation.id == card_id,
            AIRecommendation.workspace_id == workspace_id,
            AIRecommendation.is_deleted.is_(False),
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def archive(self, card: AIRecommendation) -> None:
        """
        Soft-deletes a decision card.
        """
        card.is_deleted = True
        self.db.add(card)
