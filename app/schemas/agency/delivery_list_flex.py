from typing import Optional, List
from pydantic import BaseModel

class DeliveryAgencyFlexListUpdateDTO(BaseModel):
    invoiceNumberList: Optional[List[str]] = None
