"""Delete ONLY the temporary demo data. Never touches real organizations' rows.

A row is "demo" if it is flagged `is_demo = true` OR it belongs to a demo
organization (`organizations.is_demo = true`). The org-scoping catches rows
created through the API during verification (e.g. a user added via POST /users,
or a report from /reports/compile) which default to is_demo = false but still
live under a demo org. Real orgs are never demo, so their rows are never touched.

No full-table deletes. Run: python clear_demo.py
"""
from sqlalchemy import delete, func, or_, select

from app.database import SessionLocal
from app.models import (
    Dataset,
    DecisionCard,
    KpiThreshold,
    Organization,
    Record,
    Report,
    User,
    UserSession,
)


def clear() -> dict[str, int]:
    db = SessionLocal()
    deleted: dict[str, int] = {}
    try:
        demo_org_ids = select(Organization.id).where(Organization.is_demo.is_(True))

        def demo_filter(model):
            return or_(model.is_demo.is_(True), model.organization_id.in_(demo_org_ids))

        # Sessions have no is_demo/org column here — scope via their demo users.
        demo_user_ids = select(User.id).where(demo_filter(User))
        deleted["user_sessions"] = db.execute(
            delete(UserSession).where(UserSession.user_id.in_(demo_user_ids))
        ).rowcount

        # Children before parents (foreign keys).
        for name, model in [
            ("records", Record),
            ("decision_cards", DecisionCard),
            ("reports", Report),
            ("kpi_thresholds", KpiThreshold),
            ("datasets", Dataset),
            ("users", User),
        ]:
            deleted[name] = db.execute(delete(model).where(demo_filter(model))).rowcount

        deleted["organizations"] = db.execute(
            delete(Organization).where(Organization.is_demo.is_(True))
        ).rowcount
        db.commit()

        # Verify nothing marked is_demo remains anywhere.
        remaining = {}
        for name, model in [
            ("organizations", Organization),
            ("users", User),
            ("datasets", Dataset),
            ("records", Record),
            ("decision_cards", DecisionCard),
            ("reports", Report),
            ("kpi_thresholds", KpiThreshold),
        ]:
            remaining[name] = db.scalar(
                select(func.count()).select_from(model).where(model.is_demo.is_(True))
            )

        print("Deleted demo rows:", deleted)
        print("Remaining is_demo=true rows:", remaining)
        total = sum(remaining.values())
        if total == 0:
            print("OK: database is clean — no demo data left.")
        else:
            raise SystemExit(f"WARNING: {total} demo rows still present!")
        return deleted
    finally:
        db.close()


if __name__ == "__main__":
    clear()
