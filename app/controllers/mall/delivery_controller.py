from fastapi import APIRouter, Header, Query, Path, HTTPException
from typing import Optional, List
from app.schemas.mall.cancel_delivery import CancelDeliveryRequest
from app.schemas.mall.delivery_list_register import MallApiDeliveryDTO
from app.schemas.mall.delivery_register import GoodsDTO
from app.services.mall import delivery_service

router = APIRouter(
    prefix="/api/mall",
    tags=["MALL Open Api - Delivery"],
)

@router.post("/cancelDelivery", response_model=str)
async def cancel_delivery_endpoint(
    request_data: CancelDeliveryRequest,
    Authorization: Optional[str] = Header(None)
):
    if not Authorization:
        raise HTTPException(status_code=400, detail="Authorization header required")
    try:
        return await delivery_service.cancel_delivery(request_data, Authorization)
    except Exception as e:
        # Log the exception e
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/delivery/{invoiceNumber}", response_model=str)
async def get_delivery_info_endpoint(
    invoiceNumber: str = Path(..., description="송장번호"),
    Authorization: Optional[str] = Header(None)
):
    if not Authorization:
        raise HTTPException(status_code=400, detail="Authorization header required")
    try:
        return await delivery_service.get_delivery_info(invoiceNumber, Authorization)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/deliveryList/{invoiceNumberList}", response_model=str)
async def get_delivery_list_info_endpoint(
    invoiceNumberList: str = Path(..., description="송장번호 리스트 (ex 018200405521,018200407527)"),
    Authorization: Optional[str] = Header(None)
):
    if not Authorization:
        raise HTTPException(status_code=400, detail="Authorization header required")
    try:
        return await delivery_service.get_delivery_list_info(invoiceNumberList, Authorization)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/deliveryListRegister", response_model=str)
async def register_delivery_list_endpoint(
    request_data: MallApiDeliveryDTO,
    Authorization: Optional[str] = Header(None)
):
    if not Authorization:
        raise HTTPException(status_code=400, detail="Authorization header required")
    try:
        return await delivery_service.register_delivery_list(request_data, Authorization)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/deliveryRegister", response_model=str)
async def register_delivery_endpoint(
    request_data: GoodsDTO,
    Authorization: Optional[str] = Header(None)
):
    if not Authorization:
        raise HTTPException(status_code=400, detail="Authorization header required")
    try:
        return await delivery_service.register_delivery(request_data, Authorization)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/possibleDelivery", response_model=str)
async def check_possible_delivery_endpoint(
    address: str = Query(..., description="주소"),
    postalCode: Optional[str] = Query(None, description="우편번호"),
    dawnDelivery: Optional[str] = Query(None, description="새벽배송여부"),
    Authorization: Optional[str] = Header(None)
):
    if not Authorization:
        raise HTTPException(status_code=400, detail="Authorization header required")
    try:
        return await delivery_service.check_possible_delivery(
            address=address,
            authorization=Authorization,
            postal_code=postalCode,
            dawn_delivery=dawnDelivery
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
