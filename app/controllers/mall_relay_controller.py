from fastapi import APIRouter, Request, Response, HTTPException, Header, Query
from pydantic import BaseModel
from typing import Any, Dict, Optional
import httpx

EXTERNAL_API_BASE_URL = "https://admin.todaypickup.com"

router = APIRouter(prefix="/api/mall", tags=["MALL Open Api"])

# Define Pydantic models for request bodies
# Since the exact structure isn't given, allow any fields for now.
class MallApiDeliveryDTO(BaseModel):
    pass # Replace with actual fields if schema is available

class GoodsDTO(BaseModel):
    pass # Replace with actual fields if schema is available

class GoodsReturnRequestDTO(BaseModel):
    pass # Replace with actual fields if schema is available

class MallApiReturnDTO(BaseModel):
    pass # Replace with actual fields if schema is available

class GoodsNoDawnDTO(BaseModel):
    pass # Replace with actual fields if schema is available


@router.post("/cancelDelivery")
async def cancel_delivery(
    request: Request,
    authorization: str = Header(...),
):
    async with httpx.AsyncClient() as client:
        try:
            request_body = await request.json()
            external_url = f"{EXTERNAL_API_BASE_URL}/api/mall/cancelDelivery"
            headers = {"Authorization": authorization, "Content-Type": "application/json"}
            response = await client.post(external_url, json=request_body, headers=headers)
            return Response(content=response.content, status_code=response.status_code, media_type=response.headers.get("content-type"))
        except httpx.RequestError as exc:
            raise HTTPException(status_code=500, detail=f"Error connecting to external API: {exc}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@router.get("/delivery/{invoiceNumber}")
async def find_by_invoice(
    invoiceNumber: str,
    authorization: str = Header(...)
):
    async with httpx.AsyncClient() as client:
        try:
            external_url = f"{EXTERNAL_API_BASE_URL}/api/mall/delivery/{invoiceNumber}"
            headers = {"Authorization": authorization, "Accept": "application/json"}
            response = await client.get(external_url, headers=headers)
            return Response(content=response.content, status_code=response.status_code, media_type=response.headers.get("content-type"))
        except httpx.RequestError as exc:
            raise HTTPException(status_code=500, detail=f"Error connecting to external API: {exc}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@router.get("/deliveryList/{invoiceNumberList}")
async def find_by_invoice_list(
    invoiceNumberList: str,
    authorization: str = Header(...)
):
    async with httpx.AsyncClient() as client:
        try:
            external_url = f"{EXTERNAL_API_BASE_URL}/api/mall/deliveryList/{invoiceNumberList}"
            headers = {"Authorization": authorization, "Accept": "application/json"}
            response = await client.get(external_url, headers=headers)
            return Response(content=response.content, status_code=response.status_code, media_type=response.headers.get("content-type"))
        except httpx.RequestError as exc:
            raise HTTPException(status_code=500, detail=f"Error connecting to external API: {exc}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@router.post("/deliveryListRegister", operation_id="deliveryListRegisterUsingPOST", summary="다건 배송 등록")
async def delivery_list_register(
    mall_delivery_dto: MallApiDeliveryDTO,
    authorization: str = Header(...),
):
    async with httpx.AsyncClient() as client:
        try:
            external_url = f"{EXTERNAL_API_BASE_URL}/api/mall/deliveryListRegister"
            headers = {"Authorization": authorization, "Content-Type": "application/json"}
            response = await client.post(external_url, json=mall_delivery_dto.model_dump(by_alias=True), headers=headers)
            return Response(content=response.content, status_code=response.status_code, media_type=response.headers.get("content-type"))
        except httpx.RequestError as exc:
            raise HTTPException(status_code=500, detail=f"Error connecting to external API: {exc}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@router.post("/deliveryRegister", operation_id="deliveryRegisterUsingPOST", summary="단건 배송 등록")
async def delivery_register(
    goods_dto: GoodsDTO,
    authorization: str = Header(...),
):
    async with httpx.AsyncClient() as client:
        try:
            external_url = f"{EXTERNAL_API_BASE_URL}/api/mall/deliveryRegister"
            headers = {"Authorization": authorization, "Content-Type": "application/json"}
            response = await client.post(external_url, json=goods_dto.model_dump(by_alias=True), headers=headers)
            return Response(content=response.content, status_code=response.status_code, media_type=response.headers.get("content-type"))
        except httpx.RequestError as exc:
            raise HTTPException(status_code=500, detail=f"Error connecting to external API: {exc}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@router.get("/possibleDelivery", operation_id="possibleDeliveryUsingGET", summary="배송가능여부")
async def possible_delivery(
    authorization: str = Header(...),
    address: str = Query(..., description="주소"),
    postalCode: Optional[str] = Query(None, description="우편번호"),
    dawnDelivery: Optional[str] = Query(None, description="새벽배송여부")
):
    async with httpx.AsyncClient() as client:
        try:
            external_url = f"{EXTERNAL_API_BASE_URL}/api/mall/possibleDelivery"
            headers = {"Authorization": authorization, "Accept": "application/json"}
            params = {"address": address}
            if postalCode:
                params["postalCode"] = postalCode
            if dawnDelivery:
                params["dawnDelivery"] = dawnDelivery
            
            response = await client.get(external_url, headers=headers, params=params)
            return Response(content=response.content, status_code=response.status_code, media_type=response.headers.get("content-type"))
        except httpx.RequestError as exc:
            raise HTTPException(status_code=500, detail=f"Error connecting to external API: {exc}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@router.post("/returnDelivery", operation_id="returnDeliveryUsingPOST", summary="반품 요청")
async def return_delivery(
    goods_return_request_dto: GoodsReturnRequestDTO,
    authorization: str = Header(...),
):
    async with httpx.AsyncClient() as client:
        try:
            external_url = f"{EXTERNAL_API_BASE_URL}/api/mall/returnDelivery"
            headers = {"Authorization": authorization, "Content-Type": "application/json"}
            response = await client.post(external_url, json=goods_return_request_dto.model_dump(by_alias=True), headers=headers)
            return Response(content=response.content, status_code=response.status_code, media_type=response.headers.get("content-type"))
        except httpx.RequestError as exc:
            raise HTTPException(status_code=500, detail=f"Error connecting to external API: {exc}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@router.post("/returnListRegister", operation_id="returnListRegisterUsingPOST", summary="다건 수거 등록")
async def return_list_register(
    mall_return_dto: MallApiReturnDTO, # Schema name is MallApiReturnDTO as per task
    authorization: str = Header(...),
):
    async with httpx.AsyncClient() as client:
        try:
            external_url = f"{EXTERNAL_API_BASE_URL}/api/mall/returnListRegister"
            headers = {"Authorization": authorization, "Content-Type": "application/json"}
            response = await client.post(external_url, json=mall_return_dto.model_dump(by_alias=True), headers=headers)
            return Response(content=response.content, status_code=response.status_code, media_type=response.headers.get("content-type"))
        except httpx.RequestError as exc:
            raise HTTPException(status_code=500, detail=f"Error connecting to external API: {exc}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@router.post("/returnRegister", operation_id="returnRegisterUsingPOST", summary="단건 수거 등록")
async def return_register(
    goods_no_dawn_dto: GoodsNoDawnDTO, # Schema name is GoodsNoDawnDTO as per task
    authorization: str = Header(...),
):
    async with httpx.AsyncClient() as client:
        try:
            external_url = f"{EXTERNAL_API_BASE_URL}/api/mall/returnRegister"
            headers = {"Authorization": authorization, "Content-Type": "application/json"}
            response = await client.post(external_url, json=goods_no_dawn_dto.model_dump(by_alias=True), headers=headers)
            return Response(content=response.content, status_code=response.status_code, media_type=response.headers.get("content-type"))
        except httpx.RequestError as exc:
            raise HTTPException(status_code=500, detail=f"Error connecting to external API: {exc}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

# It's good practice to include the router in the main app, 
# but for this subtask, I'll assume that's handled elsewhere.
# For example, in main.py:
# from app.controllers import mall_relay_controller
# app.include_router(mall_relay_controller.router)
