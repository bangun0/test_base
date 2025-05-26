from fastapi import APIRouter, Header, HTTPException
from typing import Optional
from app.schemas.mall.return_delivery import ReturnDeliveryRequest
from app.schemas.mall.return_list_register import MallApiReturnDTO
# Correcting the import for ReturnRegisterRequest, it should be GoodsNoDawnDTO as per service and schema
from app.schemas.mall.delivery_list_register import GoodsNoDawnDTO
from app.services.mall import return_service

router = APIRouter(
    prefix="/api/mall",
    tags=["MALL Open Api - Return"],
)

@router.post("/returnDelivery", response_model=str)
async def request_return_delivery_endpoint(
    request_data: ReturnDeliveryRequest,
    Authorization: Optional[str] = Header(None)
):
    if not Authorization:
        raise HTTPException(status_code=400, detail="Authorization header required")
    try:
        return await return_service.request_return_delivery(request_data, Authorization)
    except Exception as e:
        # Log the exception e
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/returnListRegister", response_model=str)
async def register_return_list_endpoint(
    request_data: MallApiReturnDTO,
    Authorization: Optional[str] = Header(None)
):
    if not Authorization:
        raise HTTPException(status_code=400, detail="Authorization header required")
    try:
        return await return_service.register_return_list(request_data, Authorization)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/returnRegister", response_model=str)
async def register_return_endpoint(
    request_data: GoodsNoDawnDTO, # Based on service layer and API docs for this endpoint
    Authorization: Optional[str] = Header(None)
):
    if not Authorization:
        raise HTTPException(status_code=400, detail="Authorization header required")
    try:
        return await return_service.register_return(request_data, Authorization)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
