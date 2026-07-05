"""Database engine/session and per-request organization context.

Multi-tenant isolation is enforced by PostgreSQL Row-Level Security keyed on
`organization_id`. Before running any org-scoped query we issue
`SET LOCAL app.current_organization_id = '<uuid>'` inside the transaction so RLS
policies can compare against it. Never rely on application-side filtering alone.
"""
from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency yielding a DB session, closed after the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def set_organization_context(db: Session, organization_id: str) -> None:
    """Scope the current transaction to one organization so RLS applies.

    Uses a bound parameter to avoid SQL injection via the organization id.
    """
    # Use set_config(..., is_local => true) rather than `SET LOCAL <name> = :p`:
    # Postgres' SET statement does not accept bound parameters, but set_config()
    # is a function and binds safely (no SQL injection via the organization id).
    db.execute(
        text("SELECT set_config('app.current_organization_id', :organization_id, true)"),
        {"organization_id": str(organization_id)},
    )
