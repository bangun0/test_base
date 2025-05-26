import httpx
from typing import List, Optional
from app.schemas.mall.cancel_delivery import CancelDeliveryRequest
from app.schemas.mall.delivery_list_register import MallApiDeliveryDTO
from app.schemas.mall.delivery_register import GoodsDTO

TODAY_PICKUP_API_BASE_URL = "https://admin.todaypickup.com"

async def cancel_delivery(
    request_data: CancelDeliveryRequest,
    authorization: str
) -> str:
    """
    Service to cancel a delivery.
    Corresponds to POST /api/mall/cancelDelivery
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{TODAY_PICKUP_API_BASE_URL}/api/mall/cancelDelivery",
            json=request_data.model_dump(),
            headers={"Authorization": authorization}
        )
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.text

async def get_delivery_info(
    invoice_number: str,
    authorization: str
) -> str:
    """
    Service to get delivery information for a single invoice number.
    Corresponds to GET /api/mall/delivery/{invoiceNumber}
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{TODAY_PICKUP_API_BASE_URL}/api/mall/delivery/{invoice_number}",
            headers={"Authorization": authorization}
        )
        response.raise_for_status()
        return response.text

async def get_delivery_list_info(
    invoice_number_list: str,  # As per API "018200405521,018200407527"
    authorization: str
) -> str:
    """
    Service to get delivery information for a list of invoice numbers.
    Corresponds to GET /api/mall/deliveryList/{invoiceNumberList}
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{TODAY_PICKUP_API_BASE_URL}/api/mall/deliveryList/{invoice_number_list}",
            headers={"Authorization": authorization}
        )
        response.raise_for_status()
        return response.text

async def register_delivery_list(
    request_data: MallApiDeliveryDTO,
    authorization: str
) -> str:
    """
    Service to register multiple deliveries.
    Corresponds to POST /api/mall/deliveryListRegister
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{TODAY_PICKUP_API_BASE_URL}/api/mall/deliveryListRegister",
            json=request_data.model_dump(),
            headers={"Authorization": authorization}
        )
        response.raise_for_status()
        return response.text

async def register_delivery(
    request_data: GoodsDTO,
    authorization: str
) -> str:
    """
    Service to register a single delivery.
    Corresponds to POST /api/mall/deliveryRegister
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{TODAY_PICKUP_API_BASE_URL}/api/mall/deliveryRegister",
            json=request_data.model_dump(),
            headers={"Authorization": authorization}
        )
        response.raise_for_status()
        return response.text

async def check_possible_delivery(
    address: str,
    authorization: str,
    postal_code: Optional[str] = None,
    dawn_delivery: Optional[str] = None
) -> str:
    """
    Service to check if delivery is possible for a given address.
    Corresponds to GET /api/mall/possibleDelivery
    """
    params = {"address": address}
    if postal_code:
        params["postalCode"] = postal_code
    if dawn_delivery:
        params["dawnDelivery"] = dawn_delivery

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{TODAY_PICKUP_API_BASE_URL}/api/mall/possibleDelivery",
            params=params,
            headers={"Authorization": authorization}
        )
        response.raise_for_status()
        return response.text
