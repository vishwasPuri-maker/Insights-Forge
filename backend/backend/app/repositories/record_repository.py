import uuid
from sqlalchemy import select
from sqlalchemy.orm import Session, lazyload
from app.models.record import Record


class RecordRepository:
    """
    Handles database operations for Record models.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_records_by_workspace(
        self, workspace_id: uuid.UUID, organization_id: uuid.UUID, limit: int = 100
    ) -> list[Record]:
        """
        Retrieves records within a specific workspace and organization for context gathering.
        """
        stmt = (
            select(Record)
            .where(
                Record.workspace_id == workspace_id,
                Record.organization_id == organization_id,
                Record.is_deleted.is_(False),
            )
            .options(lazyload("*"))
            .limit(limit)
        )
        return list(self.db.execute(stmt).scalars().all())
