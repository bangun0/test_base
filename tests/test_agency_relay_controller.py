import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
import httpx # Required for creating httpx.Response

# Import the FastAPI app instance
from app.main import app
# Import Pydantic models if you use them for request/response validation in tests
from app.controllers.agency_relay_controller import AuthAgencyDTO, DeliveryAgencyUpdateConsignDTO

client = TestClient(app)

EXTERNAL_API_BASE_URL = "https://admin.todaypickup.com"

@pytest.mark.asyncio
@patch('app.controllers.agency_relay_controller.httpx.AsyncClient')
async def test_auth_token_success(MockAsyncClient):
    mock_response_content = {"token": "new_jwt_token", "status": "success"}
    mock_external_response = httpx.Response(
        200,
        json=mock_response_content,
        headers={"content-type": "application/json"}
    )
    mock_instance = MockAsyncClient.return_value.__aenter__.return_value
    mock_instance.post = AsyncMock(return_value=mock_external_response)

    # Using dict for DTO for simplicity in test, or use AuthAgencyDTO(field1=value1, ...)
    request_body_dto = AuthAgencyDTO() # Create an empty DTO or with sample data
    request_body = request_body_dto.model_dump(by_alias=True) 

    headers = {"Authorization": "Bearer existingtoken", "agencyId": "agency001"}

    response = client.post("/api/agency/auth/token", json=request_body, headers=headers)

    assert response.status_code == 200
    assert response.json() == mock_response_content
    
    expected_external_url = f"{EXTERNAL_API_BASE_URL}/api/agency/auth/token"
    mock_instance.post.assert_called_once_with(
        expected_external_url,
        json=request_body,
        headers={
            "Authorization": "Bearer existingtoken", 
            "agencyId": "agency001",
            "Content-Type": "application/json",
            "Accept": "application/json" # As per controller implementation
        }
    )

@pytest.mark.asyncio
@patch('app.controllers.agency_relay_controller.httpx.AsyncClient')
async def test_update_delivery_success(MockAsyncClient):
    mock_response_content = {"message": "Delivery updated successfully", "order_id": "order123"}
    mock_external_response = httpx.Response(
        200,
        json=mock_response_content,
        headers={"content-type": "application/json"}
    )
    mock_instance = MockAsyncClient.return_value.__aenter__.return_value
    mock_instance.put = AsyncMock(return_value=mock_external_response)

    request_body_dto = DeliveryAgencyUpdateConsignDTO() # Or with sample data
    request_body = request_body_dto.model_dump(by_alias=True)
    
    headers = {"Authorization": "Bearer testtoken", "agencyId": "agency002"}

    response = client.put("/api/agency/delivery", json=request_body, headers=headers)

    assert response.status_code == 200
    assert response.json() == mock_response_content
    
    expected_external_url = f"{EXTERNAL_API_BASE_URL}/api/agency/delivery"
    mock_instance.put.assert_called_once_with(
        expected_external_url,
        json=request_body,
        headers={
            "Authorization": "Bearer testtoken", 
            "agencyId": "agency002",
            "Content-Type": "application/json",
            "Accept": "application/json" # As per controller implementation
        }
    )

@pytest.mark.asyncio
@patch('app.controllers.agency_relay_controller.httpx.AsyncClient')
async def test_auth_token_external_api_error(MockAsyncClient):
    mock_instance = MockAsyncClient.return_value.__aenter__.return_value
    mock_instance.post = AsyncMock(side_effect=httpx.RequestError("External service unavailable", request=None))

    request_body_dto = AuthAgencyDTO()
    request_body = request_body_dto.model_dump(by_alias=True)
    headers = {"Authorization": "Bearer existingtoken", "agencyId": "agency001"}

    response = client.post("/api/agency/auth/token", json=request_body, headers=headers)

    assert response.status_code == 500
    assert "Error connecting to external API" in response.json()["detail"]

@pytest.mark.asyncio
@patch('app.controllers.agency_relay_controller.httpx.AsyncClient')
async def test_update_delivery_external_api_http_error(MockAsyncClient):
    mock_external_response = httpx.Response(
        401, # Simulate an Unauthorized error from external API
        json={"detail": "Invalid agencyId or token"},
        headers={"content-type": "application/json"}
    )
    mock_instance = MockAsyncClient.return_value.__aenter__.return_value
    mock_instance.put = AsyncMock(return_value=mock_external_response)

    request_body_dto = DeliveryAgencyUpdateConsignDTO()
    request_body = request_body_dto.model_dump(by_alias=True)
    headers = {"Authorization": "Bearer testtoken", "agencyId": "agency00_invalid"}

    response = client.put("/api/agency/delivery", json=request_body, headers=headers)

    assert response.status_code == 401 # Relay forwards the external API's status
    assert response.json() == {"detail": "Invalid agencyId or token"}
    
    expected_external_url = f"{EXTERNAL_API_BASE_URL}/api/agency/delivery"
    mock_instance.put.assert_called_once_with(
        expected_external_url,
        json=request_body,
        headers={
            "Authorization": "Bearer testtoken", 
            "agencyId": "agency00_invalid",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    )
