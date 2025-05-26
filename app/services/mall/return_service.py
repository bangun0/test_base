import httpx
from app.schemas.mall.return_delivery import ReturnDeliveryRequest
from app.schemas.mall.return_list_register import MallApiReturnDTO
from app.schemas.mall.delivery_list_register import GoodsNoDawnDTO # Correctly reusing GoodsNoDawnDTO for returnRegister

TODAY_PICKUP_API_BASE_URL = "https://admin.todaypickup.com"

async def request_return_delivery(
    request_data: ReturnDeliveryRequest,
    authorization: str
) -> str:
    """
    Service to request a return for a delivery.
    Corresponds to POST /api/mall/returnDelivery
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{TODAY_PICKUP_API_BASE_URL}/api/mall/returnDelivery",
            json=request_data.model_dump(),
            headers={"Authorization": authorization}
        )
        response.raise_for_status()
        return response.text

async def register_return_list(
    request_data: MallApiReturnDTO,
    authorization: str
) -> str:
    """
    Service to register multiple return pickups.
    Corresponds to POST /api/mall/returnListRegister
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{TODAY_PICKUP_API_BASE_URL}/api/mall/returnListRegister",
            json=request_data.model_dump(),
            headers={"Authorization": authorization}
        )
        response.raise_for_status()
        return response.text

async def register_return(
    request_data: GoodsNoDawnDTO,  # API doc says GoodsNoDawnDTO for this endpoint
    authorization: str
) -> str:
    """
    Service to register a single return pickup.
    Corresponds to POST /api/mall/returnRegister
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{TODAY_PICKUP_API_BASE_URL}/api/mall/returnRegister",
            json=request_data.model_dump(),
            headers={"Authorization": authorization}
        )
        response.raise_for_status()
        return response.text
