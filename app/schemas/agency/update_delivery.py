from typing import Optional
from pydantic import BaseModel

class DeliveryAgencyUpdateConsignDTO(BaseModel):
    extOrderId: Optional[str] = None
    invoiceNumber: Optional[str] = None
    status: Optional[str] = None
