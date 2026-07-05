import uuid
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.user import User


class UserRepository:
    """
    Handles database operations for User models.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_user_by_id(
        self, user_id: uuid.UUID, organization_id: uuid.UUID
    ) -> User | None:
        """
        Retrieves a user by ID, enforcing organization tenant isolation.
        """
        stmt = select(User).where(
            User.id == user_id,
            User.organization_id == organization_id,
            User.is_deleted.is_(False),
        )
        return self.db.execute(stmt).scalar_one_or_none()
