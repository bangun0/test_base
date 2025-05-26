from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict, Any


class AgencyBase(BaseModel):
    agency_id: str
    agency_name: str


class AgencyCreate(AgencyBase):
    agency_token: str


class AgencyResponse(AgencyBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AuthTokenRequest(BaseModel):
    agency_id: str
    token: str


class AuthTokenResponse(BaseModel):
    is_valid: bool
    agency_info: Optional[Dict[str, Any]] = None


class TokenGenerateRequest(BaseModel):
    agency_id: str
    credentials: Dict[str, str]


class TokenGenerateResponse(BaseModel):
    token: str
    expires_at: Optional[datetime] = None


class DeliveryAssignmentRequest(BaseModel):
    invoice_number: str
    delivery_date: str
    agency_id: str


class DeliveryCompletionRequest(BaseModel):
    invoice_number: str
    completion_status: str
    completion_date: Optional[str] = None
    delivery_memo: Optional[str] = None


class DeliveryFlexTransferRequest(BaseModel):
    invoice_number: str
    reason: Optional[str] = None


class DeliveryListRequest(BaseModel):
    delivery_date: str
    agency_id: str


class DeliveryLookupRequest(BaseModel):
    invoice_numbers: List[str]


class PostalCodeBase(BaseModel):
    postal_code: str
    region_name: str
    is_deliverable: bool = True


class PostalCodeCreate(PostalCodeBase):
    agency_id: str


class PostalCodeResponse(PostalCodeBase):
    id: int
    agency_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PostalCodeSaveRequest(BaseModel):
    agency_id: str
    postal_codes: List[PostalCodeBase]


class DeliveryAssignmentResponse(BaseModel):
    id: int
    agency_id: str
    invoice_number: str
    delivery_date: str
    assignment_status: str
    completion_status: Optional[str] = None
    completion_date: Optional[datetime] = None
    delivery_memo: Optional[str] = None
    external_response: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True