import app.db.base
from app.db.session import SessionLocal
from app.models.dataset import Dataset
from app.models.record import Record

db = SessionLocal()
try:
    datasets = db.query(Dataset).all()
    print(f"Total Datasets: {len(datasets)}")
    for d in datasets:
        print(f"- {d.name} ({d.processing_status}) with {d.total_rows} rows")
    records = db.query(Record).all()
    print(f"Total Records: {len(records)}")
finally:
    db.close()
