import uuid
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.threshold import Threshold


class ThresholdRepository:
    """
    Handles database operations for Threshold models.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_thresholds_by_workspace(
        self, workspace_id: uuid.UUID, organization_id: uuid.UUID
    ) -> list[Threshold]:
        """
        Retrieves warning/critical thresholds within a specific workspace, enforcing tenancy checks.
        """
        stmt = select(Threshold).where(
            Threshold.workspace_id == workspace_id,
            Threshold.organization_id == organization_id,
            Threshold.is_deleted.is_(False),
        )
        return list(self.db.execute(stmt).scalars().all())
