from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict, Any


class DeliveryBase(BaseModel):
    sender_name: str
    sender_phone: str
    sender_zipcode: str
    sender_address1: str
    sender_address2: Optional[str] = None
    receiver_name: str
    receiver_phone: str
    receiver_zipcode: str
    receiver_address1: str
    receiver_address2: Optional[str] = None
    product_name: str
    product_quantity: int
    payment_type: str
    collect_amount: Optional[int] = 0
    delivery_memo: Optional[str] = None
    delivery_date: Optional[str] = None


class DeliveryCreate(DeliveryBase):
    pass


class DeliveryListCreate(BaseModel):
    deliveries: List[DeliveryBase]


class DeliveryResponse(DeliveryBase):
    id: int
    invoice_number: str
    status: str
    is_flex: bool
    external_response: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DeliveryLookupResponse(BaseModel):
    invoice_number: str
    status: str
    tracking_info: Optional[List[Dict[str, Any]]] = None
    delivery_info: Optional[Dict[str, Any]] = None


class DeliveryListLookupRequest(BaseModel):
    invoice_numbers: List[str]


class DeliveryCancelRequest(BaseModel):
    invoice_number: str
    cancel_reason: str


class DeliveryReturnRequest(BaseModel):
    invoice_number: str
    return_reason: str
    return_address: Optional[str] = None


class PossibleDeliveryRequest(BaseModel):
    zipcode: str
    address: str


class PossibleDeliveryResponse(BaseModel):
    is_possible: bool
    estimated_delivery_date: Optional[str] = None
    delivery_fee: Optional[int] = None


class DeliveryFlexTransferRequest(BaseModel):
    invoice_number: str
    reason: Optional[str] = None


class DeliveryStatusUpdateRequest(BaseModel):
    invoice_number: str
    status: str
    location: Optional[str] = None
    memo: Optional[str] = None