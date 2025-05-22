"""
Tests for the TodayPickup API client classes.

This module contains unit tests for `AgencyApiClient` and `MallApiClient`
from `app.today_pickup_client.client`. It uses `pytest` for test structure
and `pytest-httpx` for mocking HTTP requests made by the clients.

Tests cover:
- Successful API calls with correct request formation (URL, method, headers, body).
- Correct parsing of successful JSON responses.
- Handling of API error responses (e.g., 401 Unauthorized).
"""
import pytest
import httpx # Required for httpx.HTTPStatusError
# Response class is not directly used here as httpx_mock handles response creation for mocking.
# from httpx import Response 

from app.today_pickup_client.client import AgencyApiClient, MallApiClient
# Import DTOs if tests involve constructing or asserting complex request/response bodies
# directly with DTO instances. For simple JSON, direct dicts are often sufficient in tests.
# from app.today_pickup_client.schemas import AuthAgencyDTO, ... 
from app.config.settings import TODAY_PICKUP_BASE_URL # For constructing expected URLs

@pytest.mark.asyncio
async def test_agency_check_auth_success(httpx_mock) -> None:
    """
    Tests successful authentication check for AgencyApiClient.

    Verifies that:
    - `AgencyApiClient.check_auth()` makes a POST request to the correct URL.
    - Authentication token and agency ID are correctly included in headers.
    - A successful JSON response is correctly parsed and returned.

    Args:
        httpx_mock: The `pytest-httpx` mock fixture.
    """
    mock_response_data = {"status": "success", "message": "Token is valid"}
    expected_url = f"{TODAY_PICKUP_BASE_URL}/agency/auth"
    
    # Configure the mock response for the expected URL and method
    httpx_mock.add_response(
        method="POST",
        url=expected_url,
        json=mock_response_data, # The client expects a JSON response
        status_code=200
    )

    # Instantiate the client with test credentials
    client = AgencyApiClient(auth_token="fake_token", agency_id="fake_agency_id")
    # Perform the API call
    response = await client.check_auth()
    # Ensure the client's httpx session is closed
    await client.close()

    # Assert that the parsed response matches the mocked data
    assert response == mock_response_data
    
    # Assert that the request was made as expected
    request = httpx_mock.get_request() # Get the single request made
    assert request is not None
    assert request.method == "POST"
    assert str(request.url) == expected_url
    assert request.headers.get("authorization") == "fake_token"
    assert request.headers.get("agencyid") == "fake_agency_id" # Header keys are case-insensitive in httpx

@pytest.mark.asyncio
async def test_mall_get_delivery_by_invoice_success(httpx_mock) -> None:
    """
    Tests successful retrieval of delivery info for MallApiClient.

    Verifies that:
    - `MallApiClient.get_delivery_by_invoice()` makes a GET request to the correct URL.
    - The invoice number is correctly included in the path.
    - Authentication token is correctly included in headers.
    - A successful JSON response is correctly parsed and returned.

    Args:
        httpx_mock: The `pytest-httpx` mock fixture.
    """
    invoice_num = "INV001"
    mock_response_data = {"invoiceNumber": invoice_num, "status": "Shipped"}
    expected_url = f"{TODAY_PICKUP_BASE_URL}/mall/delivery/{invoice_num}"

    httpx_mock.add_response(
        method="GET",
        url=expected_url,
        json=mock_response_data,
        status_code=200
    )

    client = MallApiClient(auth_token="fake_mall_token")
    response = await client.get_delivery_by_invoice(invoice_number=invoice_num)
    await client.close()

    assert response == mock_response_data
    
    request = httpx_mock.get_request()
    assert request is not None
    assert request.method == "GET"
    assert str(request.url) == expected_url
    assert request.headers.get("authorization") == "fake_mall_token"
    # Mall API client does not typically send agencyId
    assert request.headers.get("agencyid") is None


@pytest.mark.asyncio
async def test_agency_check_auth_unauthorized(httpx_mock) -> None:
    """
    Tests unauthorized (401) error handling for AgencyApiClient.check_auth.

    Verifies that:
    - If the API returns a 401 status, `AgencyApiClient.check_auth()`
      raises an `httpx.HTTPStatusError`.
    - The request was made to the correct URL with correct headers despite the error.

    Args:
        httpx_mock: The `pytest-httpx` mock fixture.
    """
    expected_url = f"{TODAY_PICKUP_BASE_URL}/agency/auth"
    
    # Mock a 401 Unauthorized response
    httpx_mock.add_response(
        method="POST",
        url=expected_url,
        status_code=401 
    )

    client = AgencyApiClient(auth_token="invalid_token", agency_id="fake_agency_id")
    
    # Use pytest.raises to assert that an exception is raised
    with pytest.raises(httpx.HTTPStatusError) as exc_info:
        await client.check_auth()
    
    await client.close()

    # Assert that the raised exception corresponds to a 401 error
    assert exc_info.value.response.status_code == 401
    
    # Optionally, verify the request details even in case of an error response
    request = httpx_mock.get_request()
    assert request is not None
    assert request.method == "POST"
    assert str(request.url) == expected_url
    assert request.headers.get("authorization") == "invalid_token"
    assert request.headers.get("agencyid") == "fake_agency_id"

# Further tests could be added for:
# - Other client methods (POST with body, PUT, DELETE).
# - Different error status codes (e.g., 400, 403, 404, 500).
# - Network errors (e.g., using httpx_mock.add_exception).
# - Timeout scenarios.
# - Responses that are not valid JSON (if applicable).
# - Correct serialization of request DTOs to JSON.
