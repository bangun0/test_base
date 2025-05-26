from typing import Optional
from pydantic import BaseModel

class DeliveryAgencyStateUpdateDTO(BaseModel):
    holdCode: Optional[str] = None
    imgUrl: Optional[str] = None
    invoiceNumber: Optional[str] = None
    status: Optional[str] = None
