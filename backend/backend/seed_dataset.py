import app.db.base
import uuid
from datetime import datetime, timezone
from app.db.session import SessionLocal
from app.models.dataset import Dataset
from app.models.record import Record
from app.models.enums import DatasetProcessingStatus, DatasetStatus

def seed_dataset():
    db = SessionLocal()
    try:
        # Seeding parameters matching the created TestOrg workspace
        org_id = uuid.UUID('f960cc5d-7faf-4f6f-ad51-dd7cd2fc63e0')
        workspace_id = uuid.UUID('b3dff9f1-688e-4e2c-aea8-cb57c3ebeb52')
        user_id = uuid.UUID('901f84d9-1f43-41d8-b215-aeeb8c81e6eb')

        print("Seeding sales dataset...")
        dataset = Dataset(
            organization_id=org_id,
            workspace_id=workspace_id,
            uploaded_by=user_id,
            name="sales.csv",
            file_name="sales.csv",
            file_type="text/csv",
            storage_path="",
            file_size=200,
            total_rows=10,
            total_columns=3,
            processing_status=DatasetProcessingStatus.COMPLETED,
            status=DatasetStatus.ACTIVE,
            created_by=user_id
        )
        db.add(dataset)
        db.flush()

        sales_data = [
            {"product": "Alpha", "revenue": 500, "region": "North"},
            {"product": "Beta", "revenue": 600, "region": "South"},
            {"product": "Gamma", "revenue": 550, "region": "East"},
            {"product": "Delta", "revenue": 700, "region": "West"},
            {"product": "Epsilon", "revenue": 400, "region": "North"},
            {"product": "Zeta", "revenue": 650, "region": "South"},
            {"product": "Eta", "revenue": 450, "region": "East"},
            {"product": "Theta", "revenue": 800, "region": "West"},
            {"product": "Iota", "revenue": 350, "region": "North"},
            {"product": "Kappa", "revenue": 500, "region": "South"},
        ]

        now = datetime.now(timezone.utc)
        for row in sales_data:
            db.add(
                Record(
                    organization_id=org_id,
                    workspace_id=workspace_id,
                    dataset_id=dataset.id,
                    data=row,
                    recorded_at=now
                )
            )
        
        db.commit()
        print(f"Sales dataset seeded successfully (dataset_id={dataset.id}).")
    except Exception as e:
        db.rollback()
        print(f"Error seeding dataset: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_dataset()
