from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict, Any


class ReturnDeliveryBase(BaseModel):
    original_invoice_number: str
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
    return_reason: str
    return_memo: Optional[str] = None
    return_date: Optional[str] = None


class ReturnDeliveryCreate(ReturnDeliveryBase):
    pass


class ReturnDeliveryListCreate(BaseModel):
    returns: List[ReturnDeliveryBase]


class ReturnDeliveryResponse(ReturnDeliveryBase):
    id: int
    return_invoice_number: str
    status: str
    external_response: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ReturnLookupResponse(BaseModel):
    return_invoice_number: str
    original_invoice_number: str
    status: str
    tracking_info: Optional[List[Dict[str, Any]]] = None
    return_info: Optional[Dict[str, Any]] = None


class ReturnListLookupRequest(BaseModel):
    return_invoice_numbers: List[str]