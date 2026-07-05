from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel, ConfigDict
import uuid

from db.database import get_db
from db.models import Datasets, DatasetStatusEnum, DatasetProcessingStatusEnum

router = APIRouter()

class DatasetResponse(BaseModel):
    id: uuid.UUID
    name: str
    file_name: str
    file_type: str
    status: str
    
    model_config = ConfigDict(from_attributes=True)

@router.get("/", response_model=List[DatasetResponse])
def list_datasets(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Fetch a list of datasets from the database.
    """
    datasets = db.query(Datasets).filter(Datasets.is_deleted == False).offset(skip).limit(limit).all()
    # Convert enum to string for the response
    for dataset in datasets:
        dataset.status = dataset.status.value
    return datasets

@router.get("/{dataset_id}", response_model=DatasetResponse)
def get_dataset(dataset_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    Fetch a specific dataset by ID.
    """
    dataset = db.query(Datasets).filter(Datasets.id == dataset_id, Datasets.is_deleted == False).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    dataset.status = dataset.status.value
    return dataset
