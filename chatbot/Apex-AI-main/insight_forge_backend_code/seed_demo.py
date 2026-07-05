"""Insert TEMPORARY demo data across all four sectors, marked is_demo = true.

Every row this script creates has is_demo = true so it is always identifiable and
can be removed by clear_demo.py without ever touching real rows.

Creates one demo organization with one demo user per sector (retail, service,
education, agriculture), plus a demo dataset, several demo records (spread over
recent days so /timeseries has a curve), and demo decision cards — all is_demo.

Run:   python seed_demo.py
Clean: python clear_demo.py   (deletes ONLY is_demo = true rows)

NOTE: demo/seed data only. This is not cleaning/ML — just sample rows so the
/sectors/{sector}/* endpoints have something to return during development.
"""
from datetime import datetime, timedelta, timezone

from app.auth.security import hash_password
from app.database import SessionLocal
from app.models import (
    Dataset,
    DecisionCard,
    KpiThreshold,
    Organization,
    Record,
    User,
)

# Shared, well-known demo constants (also used by the verification step).
DEMO_ORG_NAME = "DEMO Org (temporary)"
DEMO_PASSWORD = "demo-pass-123"
SECTORS = ["retail", "service", "education", "agriculture"]


def demo_email(sector: str) -> str:
    # Use a normal domain — email-validator rejects reserved TLDs like .local.
    return f"demo-{sector}@demo-decisiq.com"


# A couple of representative rows per sector (generic JSONB `data`).
# Each row also carries lat/lng so the /geo endpoint has points to return.
_SAMPLE_ROWS = {
    "retail": [
        {"product": "T-Shirt", "sales": 120, "region": "North", "lat": 28.61, "lng": 77.21},
        {"product": "Jeans", "sales": 80, "region": "South", "lat": 12.97, "lng": 77.59},
        {"product": "Cap", "sales": 45, "region": "East", "lat": 22.57, "lng": 88.36},
    ],
    "service": [
        {"ticket": "TCK-1", "priority": "high", "resolution_hours": 4, "lat": 19.07, "lng": 72.87},
        {"ticket": "TCK-2", "priority": "low", "resolution_hours": 12, "lat": 13.08, "lng": 80.27},
        {"ticket": "TCK-3", "priority": "medium", "resolution_hours": 7, "lat": 17.38, "lng": 78.48},
    ],
    "education": [
        {"student": "S-1", "course": "Math", "score": 88, "lat": 26.91, "lng": 75.78},
        {"student": "S-2", "course": "Science", "score": 76, "lat": 23.02, "lng": 72.57},
        {"student": "S-3", "course": "History", "score": 91, "lat": 21.17, "lng": 72.83},
    ],
    "agriculture": [
        {"field": "F-1", "crop": "Wheat", "yield_kg": 3200, "lat": 30.73, "lng": 76.78},
        {"field": "F-2", "crop": "Rice", "yield_kg": 4100, "lat": 25.59, "lng": 85.13},
        {"field": "F-3", "crop": "Corn", "yield_kg": 2750, "lat": 26.85, "lng": 80.95},
    ],
}

# One demo KPI threshold per sector.
_THRESHOLDS = {
    "retail": ("sales", "Sales per product"),
    "service": ("resolution_hours", "Ticket resolution time"),
    "education": ("score", "Average score"),
    "agriculture": ("yield_kg", "Crop yield"),
}

_DECISIONS = {
    "retail": "Restock T-Shirt (North)",
    "service": "Add staff for high-priority tickets",
    "education": "Extra tutoring for Science",
    "agriculture": "Irrigate field F-3",
}


def seed() -> None:
    db = SessionLocal()
    try:
        now = datetime.now(timezone.utc)
        org = Organization(name=DEMO_ORG_NAME, is_demo=True)
        db.add(org)
        db.flush()

        for sector in SECTORS:
            user = User(
                organization_id=org.id,
                email=demo_email(sector),
                password_hash=hash_password(DEMO_PASSWORD),
                role="admin",
                sector=sector,
                is_demo=True,
            )
            db.add(user)
            db.flush()

            dataset = Dataset(
                organization_id=org.id,
                uploaded_by=user.id,
                sector=sector,
                original_filename=f"demo_{sector}.csv",
                s3_key=f"demo/{sector}.csv",
                content_type="text/csv",
                size_bytes=2048,
                status="ready",
                health_score=90.0,
                is_demo=True,
            )
            db.add(dataset)
            db.flush()

            # Records spread across the last 3 days so /timeseries has a curve.
            for i, row in enumerate(_SAMPLE_ROWS[sector]):
                db.add(
                    Record(
                        organization_id=org.id,
                        dataset_id=dataset.id,
                        sector=sector,
                        data=row,
                        recorded_at=now - timedelta(days=i),
                        is_demo=True,
                    )
                )

            db.add(
                DecisionCard(
                    organization_id=org.id,
                    sector=sector,
                    title=_DECISIONS[sector],
                    recommendation="Demo prescriptive action (temporary).",
                    confidence_score=0.87,
                    status="pending",
                    is_demo=True,
                )
            )

            metric_key, label = _THRESHOLDS[sector]
            db.add(
                KpiThreshold(
                    organization_id=org.id,
                    sector=sector,
                    metric_key=metric_key,
                    label=label,
                    warning_value=50.0,
                    critical_value=20.0,
                    is_demo=True,
                )
            )

        db.commit()
        print(f"Seeded demo data: 1 org, {len(SECTORS)} users/datasets/decision-cards/thresholds, "
              f"{sum(len(v) for v in _SAMPLE_ROWS.values())} records (with geo coords) — all is_demo=true.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
