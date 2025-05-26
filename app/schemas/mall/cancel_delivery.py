from pydantic import BaseModel

class CancelDeliveryRequest(BaseModel):
    invoiceNumber: str
