"""Seed the dedicated Market Data organization.

Creates (idempotently):
- Organization "InsightForge Market Data"
- One verified admin user market@insightforge.local (password printed once,
  or MARKET_SEED_PASSWORD env var if set)
- One workspace per sector (retail / service / education / agriculture)

The printed MARKET_ORGANIZATION_ID goes into .env together with
MARKET_DATA_ENABLED=true; the scraper's .env uses the printed credentials so
its uploads land in these workspaces — never in a customer's.

Run: ./venv/bin/python seed_market_org.py
"""

import os
import secrets

import app.db.base  # noqa: F401 -- registers all ORM models/mappers
from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.enums import Sector, UserStatus
from app.models.organization import Organization
from app.models.role import Role
from app.models.user import User
from app.models.user_role import UserRole
from app.models.workspace import Workspace
from app.models.workspace_member import WorkspaceMember

MARKET_ORG_NAME = "InsightForge Market Data"
MARKET_ORG_SLUG = "insightforge-market-data"
MARKET_EMAIL = "market@insightforge.local"


def seed_market_org() -> None:
    db = SessionLocal()
    try:
        org = (
            db.query(Organization)
            .filter(Organization.slug == MARKET_ORG_SLUG)
            .first()
        )
        password: str | None = None
        if org is None:
            org = Organization(
                name=MARKET_ORG_NAME, slug=MARKET_ORG_SLUG, industry="market-data"
            )
            db.add(org)
            db.flush()
            print(f"Created organization: {MARKET_ORG_NAME}")
        else:
            print(f"Organization already exists: {MARKET_ORG_NAME}")

        roles = {
            r.name: r
            for r in db.query(Role).filter(Role.organization_id == org.id).all()
        }
        for name in ["admin", "manager", "user"]:
            if name not in roles:
                roles[name] = Role(organization_id=org.id, name=name)
                db.add(roles[name])
        db.flush()

        user = db.query(User).filter(User.email == MARKET_EMAIL).first()
        if user is None:
            password = os.environ.get("MARKET_SEED_PASSWORD") or secrets.token_urlsafe(18)
            user = User(
                organization_id=org.id,
                first_name="Market",
                last_name="Data",
                email=MARKET_EMAIL,
                password_hash=hash_password(password),
                is_verified=True,
                status=UserStatus.ACTIVE,
            )
            db.add(user)
            db.flush()
            db.add(UserRole(user_id=user.id, role_id=roles["admin"].id))
            print(f"Created market user: {MARKET_EMAIL}")
        else:
            user.is_verified = True
            user.status = UserStatus.ACTIVE
            print(f"Market user already exists: {MARKET_EMAIL}")

        existing_sectors = {
            ws.sector
            for ws in db.query(Workspace)
            .filter(Workspace.organization_id == org.id)
            .all()
        }
        for sector in Sector:
            if sector in existing_sectors:
                print(f"Workspace already exists: {sector.value}")
                continue
            ws = Workspace(
                organization_id=org.id,
                name=f"Market — {sector.value.title()}",
                industry_type=sector.value,
                sector=sector,
                created_by=user.id,
            )
            db.add(ws)
            db.flush()
            db.add(
                WorkspaceMember(
                    workspace_id=ws.id, user_id=user.id, member_role="admin"
                )
            )
            print(f"Created workspace: Market — {sector.value}")

        db.commit()

        print("\n=== Put these in backend/backend/.env ===")
        print("MARKET_DATA_ENABLED=true")
        print(f"MARKET_ORGANIZATION_ID={org.id}")
        print("\n=== Scraper credentials (scraper/backend/.env) ===")
        print(f"SCRAPER_USER_EMAIL={MARKET_EMAIL}")
        if password:
            print(f"SCRAPER_USER_PASSWORD={password}")
        else:
            print("SCRAPER_USER_PASSWORD=<unchanged — set MARKET_SEED_PASSWORD and delete the user to rotate>")
    finally:
        db.close()


if __name__ == "__main__":
    seed_market_org()
