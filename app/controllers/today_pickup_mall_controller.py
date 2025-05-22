"""
API Controller for TodayPickup Mall related operations.

This module defines FastAPI routes that expose functionalities of the
TodayPickup Mall API. It uses the TodayPickupMallService for business logic
and depends on shared dependencies for authentication and service instantiation.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from app.today_pickup_client.services import TodayPickupMallService
from app.today_pickup_client.schemas import GoodsReturnRequestDTO, MallApiDeliveryDTO
from app.controllers.dependencies import get_mall_auth_token 
from typing import Any

router = APIRouter(
    prefix="/todaypickup/mall",
    tags=["TodayPickup Mall API"],
    # Consider adding responses common to all endpoints in this router, e.g., 401, 403
)

async def get_mall_service(
    auth_token: str = Depends(get_mall_auth_token)
) -> TodayPickupMallService:
    """
    Dependency to create and provide an instance of TodayPickupMallService.

    This function is used by FastAPI's dependency injection system. It retrieves
    the mall authentication token using `get_mall_auth_token` and uses it
    to instantiate the service.

    Args:
        auth_token: The mall authentication token, injected by `get_mall_auth_token`.

    Returns:
        An instance of TodayPickupMallService.
    """
    # Service instance is created per request.
    # For applications with complex service dependencies or resource management needs
    # (e.g., database connection pools managed by the service), a more sophisticated
    # lifecycle management for the service instance might be considered.
    service = TodayPickupMallService(auth_token=auth_token)
    return service


@router.post(
    "/cancel-delivery", 
    summary="Cancel a delivery using its invoice number."
)
async def cancel_delivery(
    payload: GoodsReturnRequestDTO,
    service: TodayPickupMallService = Depends(get_mall_service)
) -> Any:
    """
    Endpoint to cancel a delivery.

    It expects a payload containing the `invoiceNumber` of the delivery to be canceled.
    The actual cancellation is performed by the `TodayPickupMallService`.

    Args:
        payload: A `GoodsReturnRequestDTO` containing the invoice number.
        service: Injected `TodayPickupMallService` instance.

    Returns:
        The response from the `TodayPickupMallService.cancel_delivery` method,
        which typically confirms the cancellation. The specific structure of this
        response depends on the TodayPickup API.

    Raises:
        HTTPException: If the authorization is invalid (from dependency),
                       or if any other error occurs during the process (e.g., 500).
    """
    try:
        response = await service.cancel_delivery(payload)
        return response
    except HTTPException:
        # Re-raise HTTPException if it's already one (e.g., from auth dependency)
        raise 
    except Exception as e:
        # In a production environment, log the exception `e` with more details.
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"An unexpected error occurred: {e}" # Keep detailed error messages for server logs, not necessarily for client
        )
    finally:
        # Ensure the service client is closed after the request,
        # especially if it manages resources like HTTP connection pools.
        if service: 
            await service.close()


@router.get(
    "/delivery/{invoice_number}", 
    summary="Get delivery information by invoice number."
)
async def get_delivery_by_invoice(
    invoice_number: str,
    service: TodayPickupMallService = Depends(get_mall_service)
) -> Any:
    """
    Endpoint to retrieve delivery information for a specific invoice number.

    Args:
        invoice_number: The invoice number of the delivery to retrieve.
        service: Injected `TodayPickupMallService` instance.

    Returns:
        The delivery information for the given invoice number. The structure
        depends on the TodayPickup API. Returns a 404 if not found.

    Raises:
        HTTPException: If authorization is invalid, delivery is not found (404),
                       or any other error occurs (e.g., 500).
    """
    try:
        response = await service.get_delivery_by_invoice(invoice_number)
        if response is None: 
            # This condition depends on how the service/client indicates "not found".
            # It might return None, or the client might raise a specific exception.
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Delivery not found")
        return response
    except HTTPException:
        raise
    except Exception as e:
        # Log exception `e`.
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"An unexpected error occurred: {e}"
        )
    finally:
        if service:
            await service.close()


@router.post(
    "/delivery-list-register", 
    summary="Register a list of deliveries with the Mall API."
)
async def delivery_list_register(
    payload: MallApiDeliveryDTO,
    service: TodayPickupMallService = Depends(get_mall_service)
) -> Any:
    """
    Endpoint to register a list of deliveries.

    It expects a payload containing a list of goods and their delivery details.
    The registration is performed by the `TodayPickupMallService`.

    Args:
        payload: A `MallApiDeliveryDTO` containing the list of deliveries.
        service: Injected `TodayPickupMallService` instance.

    Returns:
        The response from `TodayPickupMallService.delivery_list_register`,
        typically confirming the registration. The structure depends on the TodayPickup API.

    Raises:
        HTTPException: If authorization is invalid or any other error occurs (e.g., 500).
    """
    try:
        response = await service.delivery_list_register(payload)
        return response
    except HTTPException:
        raise
    except Exception as e:
        # Log exception `e`.
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"An unexpected error occurred: {e}"
        )
    finally:
        if service:
            await service.close()
