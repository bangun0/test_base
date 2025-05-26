from typing import Optional, List, Literal
from pydantic import BaseModel

class PostalCodeSaveDTO(BaseModel):
    buildingCode: Optional[str] = None
    buildingName: Optional[str] = None
    legalDongCode: Optional[str] = None
    roadCode: Optional[str] = None
    roadName: Optional[str] = None
    postNumber: str
    sido: str
    gugun: str
    possibleArea: Literal["Y", "N"] # Based on example and description
    deliveryGroup: Optional[str] = None
    adminDong: Optional[str] = None
    legalDong: Optional[str] = None

class PostalCodeListDTO(BaseModel):
    dawnDelivery: Optional[Literal["Y", "N"]] = "N" # Based on example and description
    postNumberSaveList: List[PostalCodeSaveDTO]
