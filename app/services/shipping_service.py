"""
Example service demonstrating the use of TodayPickup client services.

This module, `shipping_service.py`, provides a `ShippingService` class
that showcases how to integrate and use the `TodayPickupMallService` and
`TodayPickupAgencyService` for common operations like checking shipment
status or agency authentication. It's intended as an illustrative example
of service layer composition.
"""
from app.today_pickup_client.services import TodayPickupMallService, TodayPickupAgencyService
# Example DTOs are imported for type hinting or if methods were to use them directly.
# Adjust imports based on actual DTOs used by the specific client service methods being called.
from app.today_pickup_client.schemas import GoodsReturnRequestDTO, MallApiDeliveryDTO 
from typing import Any

class ShippingService:
    """
    An example service that uses TodayPickupMallService and TodayPickupAgencyService.

    This service class demonstrates patterns for:
    - Instantiating TodayPickup service clients.
    - Calling methods on those clients.
    - Handling potential exceptions.
    - Managing the lifecycle of the client (e.g., closing connections).

    It is not a core part of the TodayPickup client library itself but serves
    as an example of how that library might be consumed within a broader application.
    """
    def __init__(self):
        """
        Initializes the ShippingService.

        In a real application, this service might receive configurations
        (e.g., API keys, base URLs if not handled by the client's config)
        or other dependencies through its constructor, possibly managed by a
        dependency injection framework. For this example, it's kept simple.
        """
        # No complex initialization needed for this example service itself,
        # as API clients are instantiated per method call with tokens passed in.
        pass

    async def get_shipment_status(self, invoice_number: str, mall_auth_token: str) -> Any:
        """
        Retrieves the shipment status for a given invoice number using TodayPickupMallService.

        This method demonstrates:
        - Instantiating `TodayPickupMallService` with an authentication token.
        - Calling the `get_delivery_by_invoice` method.
        - Basic error handling and client closure in a `finally` block.

        Args:
            invoice_number: The invoice number for which to retrieve status.
            mall_auth_token: The authentication token for the Mall API.

        Returns:
            The shipment status information as returned by the API, or an
            error dictionary if an exception occurs. The actual structure of
            the success response depends on the TodayPickup API.
        """
        print(f"ShippingService: Attempting to get shipment status for invoice: {invoice_number}")
        # Instantiate the service client required for this operation.
        # Tokens are passed directly; in a larger app, token management might be more complex.
        service = TodayPickupMallService(auth_token=mall_auth_token)
        try:
            # Call the relevant method on the TodayPickupMallService.
            # This example uses `get_delivery_by_invoice`, which is one of the
            # methods implemented in the client and service layers.
            status_info = await service.get_delivery_by_invoice(invoice_number=invoice_number)
            print(f"ShippingService: Shipment status for {invoice_number}: {status_info}")
            # In a real application, you would likely return a structured DTO
            # or raise specific exceptions rather than returning an error dictionary.
            return status_info 
        except Exception as e:
            # Basic error handling. In a production system, this would involve
            # more specific exception types and logging.
            print(f"ShippingService: Error getting shipment status for {invoice_number}: {e}")
            # Example: return an error object or raise a custom service exception.
            return {"error": str(e), "details": "Failed to retrieve shipment status."}
        finally:
            # Always ensure the client is closed to release resources.
            await service.close()
            print(f"ShippingService: Mall service client closed for invoice: {invoice_number}")

    async def check_agency_auth_status(self, agency_auth_token: str, agency_id: str) -> Any:
        """
        Checks the authentication status for a given agency using TodayPickupAgencyService.

        This method demonstrates:
        - Instantiating `TodayPickupAgencyService` with an agency token and ID.
        - Calling the `check_auth` method.
        - Basic error handling and client closure.

        Args:
            agency_auth_token: The authentication token for the Agency API.
            agency_id: The ID of the agency.

        Returns:
            The authentication status information as returned by the API, or an
            error dictionary if an exception occurs. The actual structure of
            the success response depends on the TodayPickup API.
        """
        print(f"ShippingService: Attempting to check agency auth status for agency ID: {agency_id}")
        service = TodayPickupAgencyService(auth_token=agency_auth_token, agency_id=agency_id)
        try:
            # Call the `check_auth` method on the TodayPickupAgencyService.
            auth_status = await service.check_auth()
            print(f"ShippingService: Agency auth status for {agency_id}: {auth_status}")
            # In a real application, the response might be processed or mapped to an internal status.
            return auth_status
        except Exception as e:
            print(f"ShippingService: Error checking agency auth status for {agency_id}: {e}")
            return {"error": str(e), "details": "Failed to check agency authentication status."}
        finally:
            await service.close()
            print(f"ShippingService: Agency service client closed for agency ID: {agency_id}")


# The following is an example of how this service might be used.
# It's commented out as it's for illustration/testing and not part of the service's core logic.
#
# async def main_example_usage():
#     """Illustrative example of using the ShippingService."""
#     shipping_service = ShippingService()
#
#     # These would be retrieved from a secure source or configuration in a real app
#     MOCK_MALL_AUTH_TOKEN = "your_mall_api_token_placeholder"
#     MOCK_AGENCY_AUTH_TOKEN = "your_agency_api_token_placeholder"
#     MOCK_AGENCY_ID = "your_agency_id_placeholder"
#     MOCK_INVOICE_NUMBER = "test_invoice_001"
#
#     print("\n--- Example: Testing get_shipment_status ---")
#     shipment_details = await shipping_service.get_shipment_status(
#         invoice_number=MOCK_INVOICE_NUMBER,
#         mall_auth_token=MOCK_MALL_AUTH_TOKEN
#     )
#     print(f"Result for get_shipment_status ({MOCK_INVOICE_NUMBER}): {shipment_details}")
#
#     print("\n--- Example: Testing check_agency_auth_status ---")
#     agency_status = await shipping_service.check_agency_auth_status(
#         agency_auth_token=MOCK_AGENCY_AUTH_TOKEN,
#         agency_id=MOCK_AGENCY_ID
#     )
#     print(f"Result for check_agency_auth_status ({MOCK_AGENCY_ID}): {agency_status}")
#
# if __name__ == "__main__":
#     import asyncio
#     # To run the example, ensure you have valid (or mock) tokens and an async environment.
#     # For instance, you could use:
#     # asyncio.run(main_example_usage())
#     # This part is for direct script execution demonstration and would not be in a typical library.
#     pass
