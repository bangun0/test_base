"""
API Controller for TodayPickup Agency related operations.

This module defines FastAPI routes that expose functionalities of the
TodayPickup Agency API. It utilizes the TodayPickupAgencyService for
business logic and depends on shared dependencies for authentication
(token and agency ID) and service instantiation.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from app.today_pickup_client.services import TodayPickupAgencyService
from app.today_pickup_client.schemas import AuthAgencyDTO, DeliveryAgencyUpdateConsignDTO
from app.controllers.dependencies import get_agency_auth_token, get_agency_id
from typing import Any

router = APIRouter(
    prefix="/todaypickup/agency",
    tags=["TodayPickup Agency API"],
    # Consider common responses, e.g., 400, 401, 403
)

async def get_agency_service(
    auth_token: str = Depends(get_agency_auth_token),
    agency_id: str = Depends(get_agency_id)
) -> TodayPickupAgencyService:
    """
    Dependency to create and provide an instance of TodayPickupAgencyService.

    This function is used by FastAPI's dependency injection. It retrieves the
    agency authentication token and agency ID using shared dependencies and
    uses them to instantiate the service.

    Args:
        auth_token: The agency authentication token, injected by `get_agency_auth_token`.
        agency_id: The agency ID, injected by `get_agency_id`.

    Returns:
        An instance of TodayPickupAgencyService.
    """
    # Service instance created per request.
    # Similar to MallService, more complex lifecycle management could be used if needed.
    service = TodayPickupAgencyService(auth_token=auth_token, agency_id=agency_id)
    return service


@router.post(
    "/auth/check", 
    summary="Check agency authentication status."
)
async def check_agency_auth(
    service: TodayPickupAgencyService = Depends(get_agency_service)
) -> Any:
    """
    Endpoint to check the validity of the agency's authentication credentials.

    Relies on `get_agency_service` to provide an authenticated service instance.
    The service then makes a call to the TodayPickup API to verify authentication.

    Args:
        service: Injected `TodayPickupAgencyService` instance.

    Returns:
        The response from `TodayPickupAgencyService.check_auth()`, indicating
        authentication status. Structure depends on the TodayPickup API.

    Raises:
        HTTPException: If authentication headers are missing/invalid (from dependencies),
                       or if any other error occurs (e.g., 500).
    """
    try:
        response = await service.check_auth()
        return response
    except HTTPException:
        # Re-raise if it's an HTTPException (e.g., from auth dependencies)
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
    "/auth/token", 
    summary="Get a new agency authentication token."
)
async def get_agency_auth_token_api( 
    payload: AuthAgencyDTO,
    service: TodayPickupAgencyService = Depends(get_agency_service)
) -> Any:
    """
    Endpoint to obtain a new authentication token for the agency.
    
    Note: The endpoint function is named `get_agency_auth_token_api` to avoid
    naming conflicts with the `get_agency_auth_token` dependency.

    Args:
        payload: An `AuthAgencyDTO` containing accessKey, nonce, and timestamp.
        service: Injected `TodayPickupAgencyService` instance.

    Returns:
        The response from `TodayPickupAgencyService.get_auth_token()`, which
        typically includes the new token. Structure depends on the TodayPickup API.

    Raises:
        HTTPException: If authentication headers are missing/invalid,
                       or if any other error occurs (e.g., 500).
    """
    try:
        response = await service.get_auth_token(payload)
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


@router.put(
    "/delivery/update-consign", 
    summary="Update delivery external order ID or other consignee information."
)
async def update_delivery_consign(
    payload: DeliveryAgencyUpdateConsignDTO,
    service: TodayPickupAgencyService = Depends(get_agency_service)
) -> Any:
    """
    Endpoint to update delivery consignment information (e.g., external order ID, status).

    Args:
        payload: A `DeliveryAgencyUpdateConsignDTO` containing the invoice number
                 and the details to be updated.
        service: Injected `TodayPickupAgencyService` instance.

    Returns:
        The response from `TodayPickupAgencyService.update_delivery_ext_order_id()`,
        confirming the update. Structure depends on the TodayPickup API.

    Raises:
        HTTPException: If authentication headers are missing/invalid,
                       or if any other error occurs (e.g., 500).
    """
    try:
        response = await service.update_delivery_ext_order_id(payload)
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
