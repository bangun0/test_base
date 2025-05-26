from pydantic import BaseModel

class ReturnDeliveryRequest(BaseModel):
    invoiceNumber: str
