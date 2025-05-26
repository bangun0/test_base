from typing import Optional, Literal
from pydantic import BaseModel, Field

class GoodsDTO(BaseModel):
    childrenMallId: Optional[str] = None
    dawnDelivery: Optional[str] = None
    deliveryAddress: str
    deliveryAddressEng: Optional[str] = None
    deliveryMessage: Optional[str] = None
    deliveryName: str
    deliveryPhone: str
    deliveryPostal: Optional[str] = None
    deliveryTel: Optional[str] = None
    goodsName: Optional[str] = None
    invoiceNumber: Optional[str] = Field(None, max_length=12)
    invoicePrintYn: Optional[Literal["Y", "N"]] = "N"
    mallName: str
    optionName: Optional[str] = None
    orderNumber: Optional[str] = None
    quantity: Optional[int] = None
    reserveDt: Optional[str] = None # Should ideally be date type
