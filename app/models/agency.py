from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON
from sqlalchemy.sql import func

from app.config.database import Base


class Agency(Base):
    __tablename__ = "agencies"

    id = Column(Integer, primary_key=True, index=True)
    agency_id = Column(String, unique=True, index=True)
    agency_name = Column(String)
    agency_token = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class PostalCode(Base):
    __tablename__ = "postal_codes"

    id = Column(Integer, primary_key=True, index=True)
    agency_id = Column(String, index=True)
    postal_code = Column(String, index=True)
    region_name = Column(String)
    is_deliverable = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class DeliveryAssignment(Base):
    __tablename__ = "delivery_assignments"

    id = Column(Integer, primary_key=True, index=True)
    agency_id = Column(String, index=True)
    invoice_number = Column(String, index=True)
    delivery_date = Column(String)
    assignment_status = Column(String, default="ASSIGNED")
    completion_status = Column(String)
    completion_date = Column(DateTime)
    delivery_memo = Column(Text)
    external_response = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())