"""
Pydantic models (Data Transfer Objects) for the TodayPickup API.

This module defines the data structures used for requests and responses
when interacting with the TodayPickup external API. Each class represents
a DTO and uses Pydantic for data validation and serialization.
Field descriptions are provided to clarify the purpose of each attribute,
especially as they map to the external API's expected fields.
"""
from typing import List, Optional
from pydantic import BaseModel, Field

class AuthAgencyDTO(BaseModel):
    """
    Data Transfer Object for agency authentication details.
    Used when obtaining an authentication token for agency APIs.
    """
    accessKey: Optional[str] = Field(default=None, description="API 접근 키")
    nonce: Optional[str] = Field(default=None, description="인증을 위한 임의의 문자열")
    timestamp: Optional[str] = Field(default=None, description="요청 타임스탬프")

class DeliveryAgencyUpdateConsignDTO(BaseModel):
    """
    DTO for updating delivery consignment information via agency API.
    Allows updating external order ID and status for a given invoice number.
    """
    extOrderId: Optional[str] = Field(default=None, description="외부 주문 ID")
    invoiceNumber: Optional[str] = Field(default=None, description="송장번호")
    status: Optional[str] = Field(default=None, description="상태")

class DeliveryInvoiceNumberDTO(BaseModel):
    """DTO for operations requiring a single invoice number."""
    invoiceNumber: Optional[str] = Field(default=None, description="송장번호")

class DeliveryAgencyFlexListUpdateDTO(BaseModel):
    """DTO for updating a list of invoice numbers for flex delivery via agency API."""
    invoiceNumberList: Optional[List[str]] = Field(default=None, description="송장번호 목록")

class DeliveryAgencyStateUpdateDTO(BaseModel):
    """
    DTO for updating the state of a delivery via agency API.
    Includes fields for status, hold codes, and image URLs.
    """
    holdCode: Optional[str] = Field(default=None, description="보류 코드")
    imgUrl: Optional[str] = Field(default=None, description="이미지 URL")
    invoiceNumber: Optional[str] = Field(default=None, description="송장번호")
    status: Optional[str] = Field(default=None, description="상태")

class PostalCodeSaveDTO(BaseModel):
    """DTO for saving postal code information, used within PostalCodeListDTO."""
    buildingCode: Optional[str] = Field(default=None, description="건물관리번호")
    buildingName: Optional[str] = Field(default=None, description="시군구용건물명")
    legalDongCode: Optional[str] = Field(default=None, description="법정동코드")
    roadCode: Optional[str] = Field(default=None, description="도로명코드")
    roadName: Optional[str] = Field(default=None, description="도로명")
    postNumber: str = Field(description="우편번호")
    sido: str = Field(description="도(서울,인천,경기...)", example="서울")
    gugun: str = Field(description="시/구(종로구,고양시,과천시...)", example="종로구")
    possibleArea: str = Field(description="배송가능여부(배송가능 Y, 불가능 N)", example="Y")
    deliveryGroup: Optional[str] = Field(default=None, description="배송그룹(업체에서 사용하는 코드-송장 출력용도)")
    adminDong: Optional[str] = Field(default=None, description="행정동")
    legalDong: Optional[str] = Field(default=None, description="법정동")

class PostalCodeListDTO(BaseModel):
    """DTO for submitting a list of postal codes for area serviceability checks by agency."""
    dawnDelivery: Optional[str] = Field(default="N", description="새벽배송여부(기본값 N, 새벽배송일경우 Y)", example="N")
    postNumberSaveList: List[PostalCodeSaveDTO] = Field(description="배송가능구역 우편번호 목록")

class GoodsReturnRequestDTO(BaseModel):
    """DTO for requesting a goods return, typically using an invoice number."""
    invoiceNumber: str = Field(description="송장번호")

class GoodsNoDawnDTO(BaseModel):
    """
    DTO representing goods information, typically for non-dawn deliveries.
    Used in various mall API operations for registering deliveries or returns.
    """
    childrenMallId: Optional[str] = Field(default=None, description="상점 아이디(관리 하는 상점 아이디)")
    deliveryAddress: str = Field(description="수취인주소")
    deliveryAddressEng: Optional[str] = Field(default=None, description="수취인주소영문")
    deliveryMessage: Optional[str] = Field(default=None, description="배송 메시지")
    deliveryName: str = Field(description="수취인명")
    deliveryPhone: str = Field(description="수취인 휴대폰")
    deliveryPostal: Optional[str] = Field(default=None, description="수취인 우편번호")
    deliveryTel: Optional[str] = Field(default=None, description="수취인 전화번호")
    goodsName: Optional[str] = Field(default=None, description="상품명")
    invoiceNumber: Optional[str] = Field(default=None, description="송장 번호 (송장번호 개별 생성시 입력필요, 12자리여야 합니다)", max_length=12)
    invoicePrintYn: Optional[str] = Field(default="N", description="송장 출력 여부 (Y,N(기본값))", example="N")
    mallName: str = Field(description="쇼핑몰_명")
    optionName: Optional[str] = Field(default=None, description="옵션_명")
    orderNumber: Optional[str] = Field(default=None, description="주문번호")
    quantity: Optional[int] = Field(default=None, description="수량", format="int32")
    reserveDt: Optional[str] = Field(default=None, description="예약날짜 [YYYY-MM-DD] ")

class MallApiDeliveryDTO(BaseModel):
    """DTO for registering a list of goods for delivery via the mall API."""
    dawnDelivery: Optional[str] = Field(default=None, description="새벽배송여부")
    goodsList: List[GoodsNoDawnDTO] = Field(description="상품_리스트")

class GoodsDTO(BaseModel):
    """
    DTO representing detailed goods information for mall API operations.
    Similar to GoodsNoDawnDTO but can be used in contexts where dawn delivery status might be explicit.
    """
    childrenMallId: Optional[str] = Field(default=None, description="상점 아이디(관리 하는 상점 아이디)")
    dawnDelivery: Optional[str] = Field(default=None, description="새벽배송여부")
    deliveryAddress: str = Field(description="수취인주소")
    deliveryAddressEng: Optional[str] = Field(default=None, description="수취인주소영문")
    deliveryMessage: Optional[str] = Field(default=None, description="배송 메시지")
    deliveryName: str = Field(description="수취인명")
    deliveryPhone: str = Field(description="수취인 휴대폰")
    deliveryPostal: Optional[str] = Field(default=None, description="수취인 우편번호")
    deliveryTel: Optional[str] = Field(default=None, description="수취인 전화번호")
    goodsName: Optional[str] = Field(default=None, description="상품명")
    invoiceNumber: Optional[str] = Field(default=None, description="송장 번호 (송장번호 개별 생성시 입력필요, 12자리여야 합니다)", max_length=12)
    invoicePrintYn: Optional[str] = Field(default="N", description="송장 출력 여부 (Y,N(기본값))", example="N")
    mallName: str = Field(description="쇼핑몰_명")
    optionName: Optional[str] = Field(default=None, description="옵션_명")
    orderNumber: Optional[str] = Field(default=None, description="주문번호")
    quantity: Optional[int] = Field(default=None, description="수량", format="int32")
    reserveDt: Optional[str] = Field(default=None, description="예약날짜 [YYYY-MM-DD] ")

class MallApiReturnDTO(BaseModel):
    """DTO for registering a list of goods for return via the mall API."""
    goodsList: List[GoodsNoDawnDTO] = Field(description="상품_리스트")
