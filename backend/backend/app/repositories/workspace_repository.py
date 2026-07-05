import uuid
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.workspace import Workspace


class WorkspaceRepository:
    """
    Handles database operations for Workspace models.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_workspace_by_id(
        self, workspace_id: uuid.UUID, organization_id: uuid.UUID
    ) -> Workspace | None:
        """
        Retrieves a workspace by ID, enforcing organization tenant isolation.
        """
        stmt = select(Workspace).where(
            Workspace.id == workspace_id,
            Workspace.organization_id == organization_id,
            Workspace.is_deleted.is_(False),
        )
        return self.db.execute(stmt).scalar_one_or_none()
