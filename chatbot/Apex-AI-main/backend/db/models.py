from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class RetailTransaction(Base):
    __tablename__ = 'retail_transactions'
    
    transaction_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    store_id = Column(String(64), nullable=False)
    sku_id = Column(String(64), nullable=False)
    quantity_sold = Column(Integer, nullable=False)
    unit_retail_price = Column(Float, nullable=False)
    cost_of_goods_sold = Column(Float, nullable=False)
    recorded_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # RLS (Row-Level Security) is applied at the database level outside of SQLAlchemy via DDL:
    # ALTER TABLE retail_transactions ENABLE ROW LEVEL SECURITY;
