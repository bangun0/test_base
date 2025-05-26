from typing import List, Optional, Literal
from pydantic import BaseModel, Field

class GoodsNoDawnDTO(BaseModel):
    childrenMallId: Optional[str] = None
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

class MallApiDeliveryDTO(BaseModel):
    dawnDelivery: Optional[str] = None
    goodsList: List[GoodsNoDawnDTO]
