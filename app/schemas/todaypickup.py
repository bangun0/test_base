from pydantic import BaseModel
from typing import List, Optional

class AuthAgencyDTO(BaseModel):
    accessKey: Optional[str] = None
    nonce: Optional[str] = None
    timestamp: Optional[str] = None

class DeliveryInvoiceNumberDTO(BaseModel):
    invoiceNumber: Optional[str] = None

class DeliveryAgencyUpdateConsignDTO(BaseModel):
    extOrderId: Optional[str] = None
    invoiceNumber: Optional[str] = None
    status: Optional[str] = None

class DeliveryAgencyStateUpdateDTO(BaseModel):
    holdCode: Optional[str] = None
    imgUrl: Optional[str] = None
    invoiceNumber: Optional[str] = None
    status: Optional[str] = None

class DeliveryAgencyFlexListUpdateDTO(BaseModel):
    invoiceNumberList: Optional[List[str]] = None

class GoodsReturnRequestDTO(BaseModel):
    invoiceNumber: str

class GoodsNoDawnDTO(BaseModel):
    deliveryAddress: str
    deliveryName: str
    deliveryPhone: str
    mallName: str
    childrenMallId: Optional[str] = None
    deliveryAddressEng: Optional[str] = None
    deliveryMessage: Optional[str] = None
    deliveryPostal: Optional[str] = None
    deliveryTel: Optional[str] = None
    goodsName: Optional[str] = None
    invoiceNumber: Optional[str] = None
    invoicePrintYn: Optional[str] = None
    optionName: Optional[str] = None
    orderNumber: Optional[str] = None
    quantity: Optional[int] = None
    reserveDt: Optional[str] = None

class MallApiDeliveryDTO(BaseModel):
    goodsList: List[GoodsNoDawnDTO]
    dawnDelivery: Optional[str] = None

class MallApiReturnDTO(BaseModel):
    goodsList: List[GoodsNoDawnDTO]

class PostalCodeSaveDTO(BaseModel):
    gugun: str
    possibleArea: str
    postNumber: str
    sido: str
    buildingCode: Optional[str] = None
    buildingName: Optional[str] = None
    legalDongCode: Optional[str] = None
    roadCode: Optional[str] = None
    roadName: Optional[str] = None
    deliveryGroup: Optional[str] = None
    adminDong: Optional[str] = None
    legalDong: Optional[str] = None

class PostalCodeListDTO(BaseModel):
    postNumberSaveList: List[PostalCodeSaveDTO]
    dawnDelivery: Optional[str] = "N"
