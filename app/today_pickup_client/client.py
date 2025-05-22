"""
HTTP client for interacting with the TodayPickup API.

This module provides asynchronous client classes for both Agency and Mall APIs
offered by TodayPickup. It handles request formation, authentication headers,
and basic response processing. Configuration, such as the base URL, is
imported from `app.config.settings`.
"""
import httpx
from typing import List, Optional, Dict, Any
from app.today_pickup_client.schemas import (
    AuthAgencyDTO,
    DeliveryAgencyUpdateConsignDTO,
    DeliveryInvoiceNumberDTO,
    DeliveryAgencyFlexListUpdateDTO,
    DeliveryAgencyStateUpdateDTO,
    PostalCodeListDTO,
    GoodsReturnRequestDTO,
    MallApiDeliveryDTO,
    GoodsDTO,
    # MallApiReturnDTO, # Not used yet, but good to have for later
    # PostalCodeSaveDTO, # Used within PostalCodeListDTO
)

from app.config.settings import TODAY_PICKUP_BASE_URL # Import the configuration

class TodayPickupClientBase:
    """
    Base client for TodayPickup API interactions.

    Handles common functionalities like initializing an httpx.AsyncClient,
    preparing authentication headers, and making HTTP requests.
    It is intended to be subclassed by specific API clients (Agency, Mall).
    """
    def __init__(self, auth_token: Optional[str] = None, agency_id: Optional[str] = None):
        """
        Initializes the TodayPickupClientBase.

        Args:
            auth_token: The authentication token (e.g., JWT) for API access.
                        Required for most calls.
            agency_id: The agency identifier, required for Agency API calls.
        """
        self.auth_token = auth_token
        self.agency_id = agency_id
        # Initialize an asynchronous HTTP client with the base URL from settings
        # A timeout of 10.0 seconds is configured for requests.
        self.client = httpx.AsyncClient(base_url=TODAY_PICKUP_BASE_URL, timeout=10.0) 

    async def _request(self, method: str, endpoint: str, headers: Optional[Dict[str, str]] = None, **kwargs: Any) -> Any:
        """
        Makes an asynchronous HTTP request to the specified endpoint.

        This method constructs the necessary headers, including Authorization
        and agencyId if provided, and sends the request. It handles JSON
        responses and raises exceptions for HTTP errors.

        Args:
            method: HTTP method (e.g., "GET", "POST", "PUT").
            endpoint: API endpoint path (e.g., "/agency/auth").
            headers: Optional additional headers to include in the request.
            **kwargs: Additional keyword arguments to pass to httpx.AsyncClient.request
                      (e.g., json for request body).

        Returns:
            The JSON response from the API as a Python dictionary or list,
            or None if the response status code is 204 (No Content).

        Raises:
            httpx.HTTPStatusError: If the API returns an HTTP error status (4xx or 5xx).
            httpx.RequestError: For other request-related issues (e.g., network problems).
        """
        request_headers = {}
        if self.auth_token:
            request_headers["Authorization"] = self.auth_token
        if self.agency_id: # Relevant for Agency APIs, include if provided
            request_headers["agencyId"] = self.agency_id
        
        if headers: # Merge any explicitly passed headers
            request_headers.update(headers)

        try:
            # Debugging prints (can be removed or replaced with proper logging)
            print(f"Request: {method} {self.client.base_url}{endpoint}") 
            print(f"Headers: {request_headers}") 
            if 'json' in kwargs:
                print(f"JSON Body: {kwargs['json']}") 

            response = await self.client.request(method, endpoint, headers=request_headers, **kwargs)
            
            # Debugging print for response status
            print(f"Response Status: {response.status_code}")
            # print(f"Response Content: {response.text}") # Can be verbose

            response.raise_for_status() # Raises HTTPStatusError for 4xx/5xx responses
            
            if response.status_code == 204: # Handle No Content responses
                return None
            return response.json() # Assuming most API responses are JSON
        except httpx.HTTPStatusError as e:
            # Log or handle specific HTTP status errors before re-raising
            print(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
            raise
        except httpx.RequestError as e:
            # Log or handle other network-related errors before re-raising
            print(f"Request error occurred: {e}")
            raise

    async def close(self) -> None:
        """
        Closes the underlying httpx.AsyncClient.

        It's important to call this method when the client is no longer needed
        to release resources, especially in asynchronous applications.
        """
        await self.client.aclose()

class AgencyApiClient(TodayPickupClientBase):
    """
    API client for TodayPickup Agency-specific endpoints.

    Inherits from TodayPickupClientBase and is initialized with
    an authentication token and an agency ID, which are required
    for all Agency API calls.
    """
    def __init__(self, auth_token: str, agency_id: str):
        """
        Initializes the AgencyApiClient.

        Args:
            auth_token: The authentication token for API access.
            agency_id: The agency identifier.
        """
        super().__init__(auth_token=auth_token, agency_id=agency_id)

    async def check_auth(self) -> Any:
        """
        Checks the validity of the agency authentication token.
        Corresponds to POST /agency/auth.

        Returns:
            API response, typically confirming authentication status.
        """
        # API Endpoint: POST /agency/auth
        # Required Headers: Authorization, agencyId (handled by TodayPickupClientBase)
        return await self._request("POST", "/agency/auth")

    async def get_auth_token(self, auth_dto: AuthAgencyDTO) -> Any:
        """
        Obtains a new authentication token for the agency.
        Corresponds to POST /agency/auth/token.

        Args:
            auth_dto: An AuthAgencyDTO containing accessKey, nonce, and timestamp.

        Returns:
            API response, typically containing the new authentication token.
        """
        # API Endpoint: POST /agency/auth/token
        # Required Headers: Authorization, agencyId (handled by TodayPickupClientBase)
        # Request Body: AuthAgencyDTO
        # Note: The client should ideally be re-initialized or updated with the new token after this call.
        return await self._request("POST", "/agency/auth/token", json=auth_dto.model_dump(exclude_none=True))
            
    async def update_delivery_ext_order_id(self, delivery_update_dto: DeliveryAgencyUpdateConsignDTO) -> Any:
        """
        Updates delivery information, such as external order ID or status.
        Corresponds to PUT /agency/delivery.

        Args:
            delivery_update_dto: A DeliveryAgencyUpdateConsignDTO containing
                                 the invoice number and details to update.

        Returns:
            API response, typically confirming the update.
        """
        # API Endpoint: PUT /agency/delivery
        # Required Headers: Authorization, agencyId
        # Request Body: DeliveryAgencyUpdateConsignDTO
        return await self._request("PUT", "/agency/delivery", json=delivery_update_dto.model_dump(exclude_none=True))
            
    async def find_delivery_list(self, delivery_dt: str) -> Any:
        """
        (Placeholder) Finds a list of deliveries for a specific date.
        Corresponds to POST /api/agency/delivery/list/{deliveryDt}.

        Args:
            delivery_dt: The delivery date string (e.g., "YYYY-MM-DD").

        Returns:
            API response, typically a list of delivery details.
        """
        # API Endpoint: POST /api/agency/delivery/list/{deliveryDt}
        # This is a placeholder implementation.
        print(f"Placeholder: AgencyApiClient.find_delivery_list called with delivery_dt: {delivery_dt}")
        return await self._request("POST", f"/agency/delivery/list/{delivery_dt}")


    async def update_delivery_state(self, delivery_state_dto: DeliveryAgencyStateUpdateDTO) -> Any:
        """
        (Placeholder) Updates the state of a specific delivery.
        Corresponds to PUT /api/agency/delivery/state.

        Args:
            delivery_state_dto: A DeliveryAgencyStateUpdateDTO containing
                                invoice number and state update details.

        Returns:
            API response, typically confirming the state update.
        """
        # API Endpoint: PUT /api/agency/delivery/state
        # This is a placeholder implementation.
        print(f"Placeholder: AgencyApiClient.update_delivery_state called with DTO: {delivery_state_dto}")
        return await self._request("PUT", "/agency/delivery/state", json=delivery_state_dto.model_dump(exclude_none=True))

    async def find_delivery(self, invoice_number_list_str: str) -> Any:
        """
        (Placeholder) Finds delivery details for a list of invoice numbers.
        Corresponds to POST /api/agency/delivery/{invoiceNumberList}.
        The API spec indicates a POST, but the path parameter usage is unusual for POST.

        Args:
            invoice_number_list_str: A string containing comma-separated invoice numbers.

        Returns:
            API response, typically a list of delivery details.
        """
        # API Endpoint: POST /api/agency/delivery/{invoiceNumberList}
        # This is a placeholder implementation.
        print(f"Placeholder: AgencyApiClient.find_delivery called with invoice_number_list_str: {invoice_number_list_str}")
        return await self._request("POST", f"/agency/delivery/{invoice_number_list_str}")


    async def save_postal_codes(self, postal_code_list_dto: PostalCodeListDTO) -> Any:
        """
        (Placeholder) Saves a list of postal codes for the agency.
        Corresponds to POST /api/agency/postal/save.

        Args:
            postal_code_list_dto: A PostalCodeListDTO containing postal codes to save.

        Returns:
            API response, typically confirming the save operation.
        """
        # API Endpoint: POST /api/agency/postal/save
        # This is a placeholder implementation.
        print(f"Placeholder: AgencyApiClient.save_postal_codes called with DTO: {postal_code_list_dto}")
        return await self._request("POST", "/agency/postal/save", json=postal_code_list_dto.model_dump(exclude_none=True))

    async def return_delivery_flex(self, delivery_invoice_dto: DeliveryInvoiceNumberDTO) -> Any:
        """
        (Placeholder) Processes a flex delivery return for a single invoice.
        Corresponds to PUT /api/agency/delivery/flex.

        Args:
            delivery_invoice_dto: A DeliveryInvoiceNumberDTO containing the invoice number.

        Returns:
            API response, typically confirming the return processing.
        """
        # API Endpoint: PUT /api/agency/delivery/flex
        # This is a placeholder implementation.
        print(f"Placeholder: AgencyApiClient.return_delivery_flex called with DTO: {delivery_invoice_dto}")
        return await self._request("PUT", "/agency/delivery/flex", json=delivery_invoice_dto.model_dump(exclude_none=True))

    async def return_delivery_list_flex(self, flex_list_update_dto: DeliveryAgencyFlexListUpdateDTO) -> Any:
        """
        (Placeholder) Processes flex delivery returns for a list of invoices.
        Corresponds to PUT /api/agency/delivery/list/flex.

        Args:
            flex_list_update_dto: A DeliveryAgencyFlexListUpdateDTO containing
                                  a list of invoice numbers.

        Returns:
            API response, typically confirming the processing of the list.
        """
        # API Endpoint: PUT /api/agency/delivery/list/flex
        # This is a placeholder implementation.
        print(f"Placeholder: AgencyApiClient.return_delivery_list_flex called with DTO: {flex_list_update_dto}")
        return await self._request("PUT", "/agency/delivery/list/flex", json=flex_list_update_dto.model_dump(exclude_none=True))


class MallApiClient(TodayPickupClientBase):
    """
    API client for TodayPickup Mall-specific endpoints.

    Inherits from TodayPickupClientBase and is initialized with
    an authentication token, which is required for all Mall API calls.
    The agency_id is not typically used for Mall APIs.
    """
    def __init__(self, auth_token: str):
        """
        Initializes the MallApiClient.

        Args:
            auth_token: The authentication token for API access.
        """
        # Mall APIs usually don't require agency_id, so it's not passed to super().
        super().__init__(auth_token=auth_token) 

    async def cancel_delivery(self, goods_return_dto: GoodsReturnRequestDTO) -> Any:
        """
        Cancels a specific delivery.
        Corresponds to POST /mall/cancelDelivery.

        Args:
            goods_return_dto: A GoodsReturnRequestDTO containing the invoice number
                              of the delivery to cancel.

        Returns:
            API response, typically confirming the cancellation.
        """
        # API Endpoint: POST /mall/cancelDelivery
        # Required Headers: Authorization (handled by TodayPickupClientBase)
        # Request Body: GoodsReturnRequestDTO
        return await self._request("POST", "/mall/cancelDelivery", json=goods_return_dto.model_dump(exclude_none=True))

    async def get_delivery_by_invoice(self, invoice_number: str) -> Any:
        """
        Retrieves delivery information for a specific invoice number.
        Corresponds to GET /mall/delivery/{invoiceNumber}.

        Args:
            invoice_number: The invoice number to query.

        Returns:
            API response containing details of the delivery.
        """
        # API Endpoint: GET /mall/delivery/{invoiceNumber}
        # Required Headers: Authorization
        return await self._request("GET", f"/mall/delivery/{invoice_number}")

    async def delivery_list_register(self, mall_delivery_dto: MallApiDeliveryDTO) -> Any:
        """
        Registers a list of deliveries.
        Corresponds to POST /mall/deliveryListRegister.

        Args:
            mall_delivery_dto: A MallApiDeliveryDTO containing a list of goods
                               and delivery details.

        Returns:
            API response, typically confirming the registration.
        """
        # API Endpoint: POST /mall/deliveryListRegister
        # Required Headers: Authorization
        # Request Body: MallApiDeliveryDTO
        return await self._request("POST", "/mall/deliveryListRegister", json=mall_delivery_dto.model_dump(exclude_none=True))

    async def find_by_invoice_list(self, invoice_number_list_str: str) -> Any:
        """
        (Placeholder) Finds delivery details for a list of invoice numbers.
        Corresponds to GET /api/mall/deliveryList/{invoiceNumberList}.

        Args:
            invoice_number_list_str: A string containing comma-separated invoice numbers.

        Returns:
            API response, typically a list of delivery details.
        """
        # API Endpoint: GET /api/mall/deliveryList/{invoiceNumberList}
        # This is a placeholder implementation.
        print(f"Placeholder: MallApiClient.find_by_invoice_list called with: {invoice_number_list_str}")
        return await self._request("GET", f"/mall/deliveryList/{invoice_number_list_str}")

    async def delivery_register(self, goods_dto: GoodsDTO) -> Any:
        """
        (Placeholder) Registers a single delivery.
        Corresponds to POST /api/mall/deliveryRegister.

        Args:
            goods_dto: A GoodsDTO containing details of the goods and delivery.

        Returns:
            API response, typically confirming the registration.
        """
        # API Endpoint: POST /api/mall/deliveryRegister
        # This is a placeholder implementation.
        print(f"Placeholder: MallApiClient.delivery_register called with DTO: {goods_dto}")
        return await self._request("POST", "/mall/deliveryRegister", json=goods_dto.model_dump(exclude_none=True))

    async def possible_delivery(self, address: str, postal_code: str, dawn_delivery: Optional[bool] = False) -> Any:
        """
        (Placeholder) Checks if delivery is possible for a given address and postal code.
        Corresponds to GET /api/mall/possibleDelivery.

        Args:
            address: The delivery address.
            postal_code: The postal code.
            dawn_delivery: Optional flag to check for dawn delivery possibility.
                           Defaults to False.

        Returns:
            API response, indicating if delivery is possible.
        """
        # API Endpoint: GET /api/mall/possibleDelivery
        # Query Parameters: address, postalCode, dawnDelivery
        # This is a placeholder implementation.
        params = {"address": address, "postalCode": postal_code}
        if dawn_delivery is not None: 
             # API might expect string "true" or "false" for boolean query params
             params["dawnDelivery"] = str(dawn_delivery).lower() 
        print(f"Placeholder: MallApiClient.possible_delivery called with params: {params}")
        return await self._request("GET", "/mall/possibleDelivery", params=params)

    async def return_delivery(self, goods_return_dto: GoodsReturnRequestDTO) -> Any:
        """
        (Placeholder) Processes a return for a specific delivery.
        Corresponds to POST /api/mall/returnDelivery.

        Args:
            goods_return_dto: A GoodsReturnRequestDTO containing the invoice number
                              for the return.

        Returns:
            API response, typically confirming the return processing.
        """
        # API Endpoint: POST /api/mall/returnDelivery
        # This is a placeholder implementation.
        print(f"Placeholder: MallApiClient.return_delivery called with DTO: {goods_return_dto}")
        return await self._request("POST", "/mall/returnDelivery", json=goods_return_dto.model_dump(exclude_none=True))

    async def return_list_register(self, mall_api_return_dto: Any) -> Any: # Replace Any with actual DTO if defined
        """
        (Placeholder) Registers a list of returns.
        Corresponds to POST /api/mall/returnListRegister.

        Args:
            mall_api_return_dto: A DTO (e.g., MallApiReturnDTO) containing a list
                                 of goods for return.

        Returns:
            API response, typically confirming the registration of returns.
        """
        # API Endpoint: POST /api/mall/returnListRegister
        # Body: MallApiReturnDTO (or similar)
        # This is a placeholder implementation.
        # from app.today_pickup_client.schemas import MallApiReturnDTO # Ensure imported if specific DTO is used
        print(f"Placeholder: MallApiClient.return_list_register called with DTO: {mall_api_return_dto}")
        # Assuming mall_api_return_dto is an instance of a Pydantic model
        return await self._request("POST", "/mall/returnListRegister", json=mall_api_return_dto.model_dump(exclude_none=True))


    async def return_register(self, goods_dto: GoodsDTO) -> Any:
        """
        (Placeholder) Registers a single return.
        Corresponds to POST /api/mall/returnRegister.

        Args:
            goods_dto: A GoodsDTO containing details for the return.

        Returns:
            API response, typically confirming the return registration.
        """
        # API Endpoint: POST /api/mall/returnRegister
        # This is a placeholder implementation.
        print(f"Placeholder: MallApiClient.return_register called with DTO: {goods_dto}")
        return await self._request("POST", "/mall/returnRegister", json=goods_dto.model_dump(exclude_none=True))

# Example usage (optional, for testing purposes if this file is run directly)
# This section can be useful for quick, direct testing of the client.
# Ensure to handle asyncio correctly if uncommented.
#
# import asyncio
# async def main_example():
#     # This is a placeholder, actual token and agencyId would come from a secure source/config
#     # or environment variables for real testing.
#     MOCK_AGENCY_TOKEN = "YOUR_AGENCY_AUTH_TOKEN"
#     MOCK_AGENCY_ID = "YOUR_AGENCY_ID"
#     MOCK_MALL_TOKEN = "YOUR_MALL_AUTH_TOKEN"
#     
#     # --- Test Agency API ---
#     print("Testing Agency API...")
#     agency_client = AgencyApiClient(auth_token=MOCK_AGENCY_TOKEN, agency_id=MOCK_AGENCY_ID)
#     try:
#         # Example: Check authentication
#         # auth_status = await agency_client.check_auth()
#         # print(f"Agency Auth Status: {auth_status}")
#
#         # Example: Get auth token (This is a sensitive operation)
#         # auth_payload = AuthAgencyDTO(accessKey="your_access_key", nonce="generated_nonce", timestamp="current_timestamp")
#         # token_info = await agency_client.get_auth_token(auth_payload)
#         # print(f"New Token Info: {token_info}")
#
#         # Example: Update delivery external order ID
#         # update_payload = DeliveryAgencyUpdateConsignDTO(extOrderId="ext123", invoiceNumber="inv789", status="DELIVERED")
#         # update_status = await agency_client.update_delivery_ext_order_id(update_payload)
#         # print(f"Update Delivery Status: {update_status}")
#
#         # Example: Call a placeholder method
#         # delivery_list = await agency_client.find_delivery_list(delivery_dt="2023-01-01")
#         # print(f"Delivery list for 2023-01-01: {delivery_list}")
#
#     except httpx.HTTPStatusError as hse:
#         print(f"Agency API HTTP Error: {hse.response.status_code} - {hse.response.text}")
#     except Exception as e:
#         print(f"An error occurred during Agency API test: {e}")
#     finally:
#         await agency_client.close()
#
#     # --- Test Mall API ---
#     print("\nTesting Mall API...")
#     mall_client = MallApiClient(auth_token=MOCK_MALL_TOKEN)
#     try:
#         # Example: Get delivery by invoice
#         # delivery_info = await mall_client.get_delivery_by_invoice("INV001TEST")
#         # print(f"Delivery Info for INV001TEST: {delivery_info}")
#
#         # Example: Cancel delivery
#         # cancel_payload = GoodsReturnRequestDTO(invoiceNumber="INV002CANCEL")
#         # cancel_status = await mall_client.cancel_delivery(cancel_payload)
#         # print(f"Cancel Delivery Status: {cancel_status}")
#
#         # Example: Register a list of deliveries
#         # from app.today_pickup_client.schemas import GoodsNoDawnDTO # ensure imported
#         # delivery_list_payload = MallApiDeliveryDTO(
#         #     goodsList=[
#         #         GoodsNoDawnDTO(deliveryAddress="123 Test St", deliveryName="Test User", deliveryPhone="01012345678", mallName="TestMall")
#         #     ]
#         # )
#         # register_status = await mall_client.delivery_list_register(delivery_list_payload)
#         # print(f"Delivery List Register Status: {register_status}")
#
#         # Example: Call a placeholder method
#         # possible = await mall_client.possible_delivery(address="Some Address", postal_code="12345")
#         # print(f"Delivery possible: {possible}")
#
#     except httpx.HTTPStatusError as hse:
#         print(f"Mall API HTTP Error: {hse.response.status_code} - {hse.response.text}")
#     except Exception as e:
#         print(f"An error occurred during Mall API test: {e}")
#     finally:
#         await mall_client.close()

# if __name__ == "__main__":
#     # To run the example main, you'd need to uncomment the main_example function, 
#     # the asyncio import, and potentially DTO imports within main_example.
#     # Also, provide actual test tokens and data.
#     # Example:
#     # import asyncio
#     # asyncio.run(main_example())
#     pass
