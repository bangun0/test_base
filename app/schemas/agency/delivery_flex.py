from typing import Optional
from pydantic import BaseModel

class DeliveryInvoiceNumberDTO(BaseModel):
    invoiceNumber: Optional[str] = None
