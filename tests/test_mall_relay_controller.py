import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
import httpx # Required for creating httpx.Response

# Import the FastAPI app instance
# Assuming your FastAPI app instance is named 'app' in 'app.main'
from app.main import app
# Import Pydantic models if you use them for request/response validation in tests
# from app.controllers.mall_relay_controller import GoodsReturnRequestDTO (example)

client = TestClient(app)

EXTERNAL_API_BASE_URL = "https://admin.todaypickup.com"

@pytest.mark.asyncio
@patch('app.controllers.mall_relay_controller.httpx.AsyncClient')
async def test_cancel_delivery_success(MockAsyncClient):
    # Configure the mock for the external API call
    mock_response_content = {"status": "success", "message": "Delivery cancelled"}
    mock_external_response = httpx.Response(
        200,
        json=mock_response_content,
        headers={"content-type": "application/json"}
    )
    # Set up the AsyncClient's post method to return our mock response
    mock_instance = MockAsyncClient.return_value.__aenter__.return_value # Access the client instance from async context manager
    mock_instance.post = AsyncMock(return_value=mock_external_response)

    request_body = {"orderId": "12345", "reason": "Test cancellation"}
    headers = {"Authorization": "Bearer testtoken"}

    # Call the API endpoint
    response = client.post("/api/mall/cancelDelivery", json=request_body, headers=headers)

    # Assertions
    assert response.status_code == 200
    assert response.json() == mock_response_content
    
    # Check if the external API was called correctly
    expected_external_url = f"{EXTERNAL_API_BASE_URL}/api/mall/cancelDelivery"
    mock_instance.post.assert_called_once_with(
        expected_external_url,
        json=request_body,
        headers={"Authorization": "Bearer testtoken", "Content-Type": "application/json"}
    )

@pytest.mark.asyncio
@patch('app.controllers.mall_relay_controller.httpx.AsyncClient')
async def test_find_by_invoice_success(MockAsyncClient):
    invoice_number = "INV123456"
    mock_response_content = {"invoiceNumber": invoice_number, "status": "delivered"}
    mock_external_response = httpx.Response(
        200,
        json=mock_response_content,
        headers={"content-type": "application/json"}
    )
    mock_instance = MockAsyncClient.return_value.__aenter__.return_value
    mock_instance.get = AsyncMock(return_value=mock_external_response)

    headers = {"Authorization": "Bearer testtoken"}

    # Call the API endpoint
    response = client.get(f"/api/mall/delivery/{invoice_number}", headers=headers)

    # Assertions
    assert response.status_code == 200
    assert response.json() == mock_response_content
    
    expected_external_url = f"{EXTERNAL_API_BASE_URL}/api/mall/delivery/{invoice_number}"
    mock_instance.get.assert_called_once_with(
        expected_external_url,
        headers={"Authorization": "Bearer testtoken", "Accept": "application/json"}
    )

@pytest.mark.asyncio
@patch('app.controllers.mall_relay_controller.httpx.AsyncClient')
async def test_cancel_delivery_external_api_error(MockAsyncClient):
    mock_instance = MockAsyncClient.return_value.__aenter__.return_value
    # Simulate an httpx.RequestError from the external API
    mock_instance.post = AsyncMock(side_effect=httpx.RequestError("Connection failed", request=None))

    request_body = {"orderId": "12345", "reason": "Test cancellation"}
    headers = {"Authorization": "Bearer testtoken"}

    response = client.post("/api/mall/cancelDelivery", json=request_body, headers=headers)

    assert response.status_code == 500
    assert "Error connecting to external API" in response.json()["detail"]

@pytest.mark.asyncio
@patch('app.controllers.mall_relay_controller.httpx.AsyncClient')
async def test_find_by_invoice_external_api_http_error(MockAsyncClient):
    invoice_number = "INV_ERROR"
    mock_external_response = httpx.Response(
        404, # Simulate a 404 from external API
        json={"detail": "Not Found"},
        headers={"content-type": "application/json"}
    )
    mock_instance = MockAsyncClient.return_value.__aenter__.return_value
    mock_instance.get = AsyncMock(return_value=mock_external_response)

    headers = {"Authorization": "Bearer testtoken"}
    response = client.get(f"/api/mall/delivery/{invoice_number}", headers=headers)

    # The relay should forward the status code and content from the external API
    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}
    
    expected_external_url = f"{EXTERNAL_API_BASE_URL}/api/mall/delivery/{invoice_number}"
    mock_instance.get.assert_called_once_with(
        expected_external_url,
        headers={"Authorization": "Bearer testtoken", "Accept": "application/json"}
    )
