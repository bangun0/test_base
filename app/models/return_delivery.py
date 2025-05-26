from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON
from sqlalchemy.sql import func

from app.config.database import Base


class ReturnDelivery(Base):
    __tablename__ = "return_deliveries"

    id = Column(Integer, primary_key=True, index=True)
    return_invoice_number = Column(String, unique=True, index=True)
    original_invoice_number = Column(String, index=True)
    sender_name = Column(String)
    sender_phone = Column(String)
    sender_zipcode = Column(String)
    sender_address1 = Column(String)
    sender_address2 = Column(String)
    receiver_name = Column(String)
    receiver_phone = Column(String)
    receiver_zipcode = Column(String)
    receiver_address1 = Column(String)
    receiver_address2 = Column(String)
    product_name = Column(String)
    product_quantity = Column(Integer)
    return_reason = Column(String)
    return_memo = Column(Text)
    status = Column(String, default="REGISTERED")
    return_date = Column(String)
    external_response = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ReturnTracking(Base):
    __tablename__ = "return_trackings"

    id = Column(Integer, primary_key=True, index=True)
    return_invoice_number = Column(String, index=True)
    status = Column(String)
    status_message = Column(String)
    tracking_date = Column(DateTime)
    location = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())