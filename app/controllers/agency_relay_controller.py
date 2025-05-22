from fastapi import APIRouter, Response, HTTPException, Header, Path
from pydantic import BaseModel
from typing import Any, Dict, Optional
import httpx

EXTERNAL_API_BASE_URL = "https://admin.todaypickup.com"

router = APIRouter(prefix="/api/agency", tags=["AGENCY Open Api"])

# Pydantic Models
class AuthAgencyDTO(BaseModel):
    pass 

class DeliveryAgencyUpdateConsignDTO(BaseModel):
    pass 

class DeliveryInvoiceNumberDTO(BaseModel):
    pass 

class DeliveryAgencyFlexListUpdateDTO(BaseModel):
    pass 

class DeliveryAgencyStateUpdateDTO(BaseModel):
    # Define fields if known, or allow arbitrary key-value pairs
    # Example: invoice_number: str
    # Example: status_code: str 
    pass # Replace with actual fields if schema is available

class PostalCodeListDTO(BaseModel):
    # Define fields if known, or allow arbitrary key-value pairs
    # Example: List[str]
    pass # Replace with actual fields if schema is available


@router.post("/auth", operation_id="checkAuthUsingPOST", summary="토큰 유효성 검사")
async def check_auth(
    authorization: str = Header(...),
    agencyId: str = Header(...), 
):
    async with httpx.AsyncClient() as client:
        try:
            external_url = f"{EXTERNAL_API_BASE_URL}/api/agency/auth"
            headers = {
                "Authorization": authorization,
                "agencyId": agencyId, 
                "Content-Type": "application/json",
                "Accept": "application/json" 
            }
            response = await client.post(external_url, json={}, headers=headers)
            return Response(content=response.content, status_code=response.status_code, media_type=response.headers.get("content-type"))
        except httpx.RequestError as exc:
            raise HTTPException(status_code=500, detail=f"Error connecting to external API: {exc}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@router.post("/auth/token", operation_id="authTokenUsingPOST", summary="토큰 생성")
async def auth_token(
    auth_agency_dto: AuthAgencyDTO,
    authorization: str = Header(...),
    agencyId: str = Header(...), 
):
    async with httpx.AsyncClient() as client:
        try:
            external_url = f"{EXTERNAL_API_BASE_URL}/api/agency/auth/token"
            headers = {
                "Authorization": authorization,
                "agencyId": agencyId,
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            response = await client.post(external_url, json=auth_agency_dto.model_dump(by_alias=True), headers=headers)
            return Response(content=response.content, status_code=response.status_code, media_type=response.headers.get("content-type"))
        except httpx.RequestError as exc:
            raise HTTPException(status_code=500, detail=f"Error connecting to external API: {exc}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@router.put("/delivery", operation_id="updateDeliveryExtOrderIdUsingPUT", summary="배정완료")
async def update_delivery_ext_order_id(
    delivery_agency_update_consign_dto: DeliveryAgencyUpdateConsignDTO,
    authorization: str = Header(...),
    agencyId: str = Header(...),
):
    async with httpx.AsyncClient() as client:
        try:
            external_url = f"{EXTERNAL_API_BASE_URL}/api/agency/delivery"
            headers = {
                "Authorization": authorization,
                "agencyId": agencyId,
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            response = await client.put(external_url, json=delivery_agency_update_consign_dto.model_dump(by_alias=True), headers=headers)
            return Response(content=response.content, status_code=response.status_code, media_type=response.headers.get("content-type"))
        except httpx.RequestError as exc:
            raise HTTPException(status_code=500, detail=f"Error connecting to external API: {exc}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@router.put("/delivery/flex", operation_id="returnDeliveryFlexUsingPUT", summary="플렉스 이관")
async def return_delivery_flex(
    delivery_invoice_number_dto: DeliveryInvoiceNumberDTO,
    authorization: str = Header(...),
    agencyId: str = Header(...),
):
    async with httpx.AsyncClient() as client:
        try:
            external_url = f"{EXTERNAL_API_BASE_URL}/api/agency/delivery/flex"
            headers = {
                "Authorization": authorization,
                "agencyId": agencyId,
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            response = await client.put(external_url, json=delivery_invoice_number_dto.model_dump(by_alias=True), headers=headers)
            return Response(content=response.content, status_code=response.status_code, media_type=response.headers.get("content-type"))
        except httpx.RequestError as exc:
            raise HTTPException(status_code=500, detail=f"Error connecting to external API: {exc}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@router.put("/delivery/list/flex", operation_id="returnDeliveryListFlexUsingPUT", summary="플렉스 다건 이관")
async def return_delivery_list_flex(
    delivery_agency_flex_list_update_dto: DeliveryAgencyFlexListUpdateDTO,
    authorization: str = Header(...),
    agencyId: str = Header(...),
):
    async with httpx.AsyncClient() as client:
        try:
            external_url = f"{EXTERNAL_API_BASE_URL}/api/agency/delivery/list/flex"
            headers = {
                "Authorization": authorization,
                "agencyId": agencyId,
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            response = await client.put(external_url, json=delivery_agency_flex_list_update_dto.model_dump(by_alias=True), headers=headers)
            return Response(content=response.content, status_code=response.status_code, media_type=response.headers.get("content-type"))
        except httpx.RequestError as exc:
            raise HTTPException(status_code=500, detail=f"Error connecting to external API: {exc}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@router.post("/delivery/list/{deliveryDt}", operation_id="findDeliveryListUsingPOST", summary="배송정보 조회")
async def find_delivery_list(
    deliveryDt: str = Path(..., title="Delivery Date", description="배송 날짜"),
    authorization: str = Header(...),
    agencyId: str = Header(...),
):
    async with httpx.AsyncClient() as client:
        try:
            external_url = f"{EXTERNAL_API_BASE_URL}/api/agency/delivery/list/{deliveryDt}"
            headers = {
                "Authorization": authorization,
                "agencyId": agencyId,
                "Content-Type": "application/json", 
                "Accept": "application/json"
            }
            response = await client.post(external_url, json={}, headers=headers)
            return Response(content=response.content, status_code=response.status_code, media_type=response.headers.get("content-type"))
        except httpx.RequestError as exc:
            raise HTTPException(status_code=500, detail=f"Error connecting to external API: {exc}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@router.put("/delivery/state", operation_id="updateDeliveryStateUsingPUT", summary="배송상태 수정")
async def update_delivery_state(
    delivery_agency_state_update_dto: DeliveryAgencyStateUpdateDTO,
    authorization: str = Header(...),
    agencyId: str = Header(...),
):
    async with httpx.AsyncClient() as client:
        try:
            external_url = f"{EXTERNAL_API_BASE_URL}/api/agency/delivery/state"
            headers = {
                "Authorization": authorization,
                "agencyId": agencyId,
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            response = await client.put(external_url, json=delivery_agency_state_update_dto.model_dump(by_alias=True), headers=headers)
            return Response(content=response.content, status_code=response.status_code, media_type=response.headers.get("content-type"))
        except httpx.RequestError as exc:
            raise HTTPException(status_code=500, detail=f"Error connecting to external API: {exc}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@router.post("/delivery/{invoiceNumberList}", operation_id="findDeliveryUsingPOST", summary="운송장 배송조회")
async def find_delivery(
    invoiceNumberList: str = Path(..., title="Invoice Number List", description="운송장 번호 목록"),
    authorization: str = Header(...),
    agencyId: str = Header(...),
):
    async with httpx.AsyncClient() as client:
        try:
            external_url = f"{EXTERNAL_API_BASE_URL}/api/agency/delivery/{invoiceNumberList}"
            headers = {
                "Authorization": authorization,
                "agencyId": agencyId,
                "Content-Type": "application/json", # Consumes application/json
                "Accept": "*/*"  # Produces */*
            }
            response = await client.post(external_url, json={}, headers=headers) # Sending empty JSON body
            # Forward the original content-type from the external API
            return Response(content=response.content, status_code=response.status_code, media_type=response.headers.get("content-type"))
        except httpx.RequestError as exc:
            raise HTTPException(status_code=500, detail=f"Error connecting to external API: {exc}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@router.post("/postal/save", operation_id="postNumberSaveUsingPOST", summary="배송가능 구역 입력")
async def post_number_save(
    postal_code_list_dto: PostalCodeListDTO,
    authorization: str = Header(...),
    agencyId: str = Header(...),
):
    async with httpx.AsyncClient() as client:
        try:
            external_url = f"{EXTERNAL_API_BASE_URL}/api/agency/postal/save"
            headers = {
                "Authorization": authorization,
                "agencyId": agencyId,
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            response = await client.post(external_url, json=postal_code_list_dto.model_dump(by_alias=True), headers=headers)
            return Response(content=response.content, status_code=response.status_code, media_type=response.headers.get("content-type"))
        except httpx.RequestError as exc:
            raise HTTPException(status_code=500, detail=f"Error connecting to external API: {exc}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

# For main app integration (example, not part of this file):
# from app.controllers import agency_relay_controller
# app.include_router(agency_relay_controller.router)
