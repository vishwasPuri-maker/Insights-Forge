import uuid
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.dataset import Dataset


class DatasetRepository:
    """
    Handles database operations for Dataset models.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_datasets_by_workspace(
        self, workspace_id: uuid.UUID, organization_id: uuid.UUID
    ) -> list[Dataset]:
        """
        Retrieves all datasets within a specific workspace, enforcing tenancy checks.
        """
        stmt = select(Dataset).where(
            Dataset.workspace_id == workspace_id,
            Dataset.organization_id == organization_id,
            Dataset.is_deleted.is_(False),
        )
        return list(self.db.execute(stmt).scalars().all())

    def get_dataset_by_id(
        self,
        dataset_id: uuid.UUID,
        workspace_id: uuid.UUID,
        organization_id: uuid.UUID,
    ) -> Dataset | None:
        """
        Retrieves a single dataset by ID, enforcing workspace and organization boundaries.
        """
        stmt = select(Dataset).where(
            Dataset.id == dataset_id,
            Dataset.workspace_id == workspace_id,
            Dataset.organization_id == organization_id,
            Dataset.is_deleted.is_(False),
        )
        return self.db.execute(stmt).scalar_one_or_none()
