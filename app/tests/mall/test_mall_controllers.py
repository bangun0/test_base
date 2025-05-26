import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock

# It's important to set up the app for the TestClient
# We need to create a minimal FastAPI app and include the routers
from fastapi import FastAPI, APIRouter
from app.controllers.mall import delivery_controller, return_controller

# Create a fixture for the app
@pytest.fixture(scope="module")
def test_app():
    app = FastAPI()
    app.include_router(delivery_controller.router)
    app.include_router(return_controller.router)
    return app

# Create a fixture for the TestClient
@pytest.fixture(scope="module")
def client(test_app):
    return TestClient(test_app)

MOCK_AUTH_TOKEN = "test_auth_token"
MOCK_SUCCESS_RESPONSE_TEXT = "Mocked service success"

# Delivery Controller Tests
@patch("app.services.mall.delivery_service.cancel_delivery", new_callable=AsyncMock)
def test_cancel_delivery_endpoint_success(mock_service, client: TestClient):
    mock_service.return_value = MOCK_SUCCESS_RESPONSE_TEXT
    payload = {"invoiceNumber": "inv123"}
    response = client.post(
        "/api/mall/cancelDelivery",
        json=payload,
        headers={"Authorization": MOCK_AUTH_TOKEN}
    )
    assert response.status_code == 200
    assert response.json() == MOCK_SUCCESS_RESPONSE_TEXT
    mock_service.assert_called_once()
    # Check if called with Pydantic model correctly - first arg of mock is the model instance
    assert mock_service.call_args[0][0].invoiceNumber == payload["invoiceNumber"] 
    assert mock_service.call_args[0][1] == MOCK_AUTH_TOKEN


def test_cancel_delivery_endpoint_missing_auth(client: TestClient):
    response = client.post("/api/mall/cancelDelivery", json={"invoiceNumber": "inv123"})
    assert response.status_code == 400 # As per controller's HTTPException
    assert "Authorization header required" in response.json()["detail"]

@patch("app.services.mall.delivery_service.cancel_delivery", new_callable=AsyncMock)
def test_cancel_delivery_endpoint_service_error(mock_service, client: TestClient):
    mock_service.side_effect = Exception("Service layer error")
    response = client.post(
        "/api/mall/cancelDelivery",
        json={"invoiceNumber": "inv123"},
        headers={"Authorization": MOCK_AUTH_TOKEN}
    )
    assert response.status_code == 500
    assert "Service layer error" in response.json()["detail"]

def test_cancel_delivery_endpoint_invalid_payload(client: TestClient):
    response = client.post(
        "/api/mall/cancelDelivery",
        json={}, # Missing invoiceNumber
        headers={"Authorization": MOCK_AUTH_TOKEN}
    )
    assert response.status_code == 422 # FastAPI's unprocessable entity

@patch("app.services.mall.delivery_service.get_delivery_info", new_callable=AsyncMock)
def test_get_delivery_info_endpoint_success(mock_service, client: TestClient):
    invoice_num = "inv789"
    mock_service.return_value = MOCK_SUCCESS_RESPONSE_TEXT
    response = client.get(
        f"/api/mall/delivery/{invoice_num}",
        headers={"Authorization": MOCK_AUTH_TOKEN}
    )
    assert response.status_code == 200
    assert response.json() == MOCK_SUCCESS_RESPONSE_TEXT
    mock_service.assert_called_once_with(invoice_num, MOCK_AUTH_TOKEN)

def test_get_delivery_info_endpoint_missing_auth(client: TestClient):
    response = client.get("/api/mall/delivery/inv789")
    assert response.status_code == 400

@patch("app.services.mall.delivery_service.get_delivery_list_info", new_callable=AsyncMock)
def test_get_delivery_list_info_endpoint_success(mock_service, client: TestClient):
    invoice_list_str = "inv1,inv2,inv3"
    mock_service.return_value = MOCK_SUCCESS_RESPONSE_TEXT
    response = client.get(
        f"/api/mall/deliveryList/{invoice_list_str}",
        headers={"Authorization": MOCK_AUTH_TOKEN}
    )
    assert response.status_code == 200
    assert response.json() == MOCK_SUCCESS_RESPONSE_TEXT
    mock_service.assert_called_once_with(invoice_list_str, MOCK_AUTH_TOKEN)

@patch("app.services.mall.delivery_service.register_delivery_list", new_callable=AsyncMock)
def test_register_delivery_list_endpoint_success(mock_service, client: TestClient):
    mock_service.return_value = MOCK_SUCCESS_RESPONSE_TEXT
    payload = {
        "goodsList": [{
            "deliveryAddress": "123 Test St",
            "deliveryName": "Test User",
            "deliveryPhone": "1234567890",
            "mallName": "Test Mall"
        }]
    }
    response = client.post(
        "/api/mall/deliveryListRegister",
        json=payload,
        headers={"Authorization": MOCK_AUTH_TOKEN}
    )
    assert response.status_code == 200
    assert response.json() == MOCK_SUCCESS_RESPONSE_TEXT
    mock_service.assert_called_once()
    assert mock_service.call_args[0][0].goodsList[0].deliveryAddress == payload["goodsList"][0]["deliveryAddress"]
    assert mock_service.call_args[0][1] == MOCK_AUTH_TOKEN

@patch("app.services.mall.delivery_service.register_delivery", new_callable=AsyncMock)
def test_register_delivery_endpoint_success(mock_service, client: TestClient):
    mock_service.return_value = MOCK_SUCCESS_RESPONSE_TEXT
    payload = {
        "deliveryAddress": "456 Test Ave",
        "deliveryName": "Another User",
        "deliveryPhone": "0987654321",
        "mallName": "Another Mall"
    }
    response = client.post(
        "/api/mall/deliveryRegister",
        json=payload,
        headers={"Authorization": MOCK_AUTH_TOKEN}
    )
    assert response.status_code == 200
    assert response.json() == MOCK_SUCCESS_RESPONSE_TEXT
    mock_service.assert_called_once()
    assert mock_service.call_args[0][0].mallName == payload["mallName"]
    assert mock_service.call_args[0][1] == MOCK_AUTH_TOKEN

@patch("app.services.mall.delivery_service.check_possible_delivery", new_callable=AsyncMock)
def test_check_possible_delivery_endpoint_success(mock_service, client: TestClient):
    mock_service.return_value = MOCK_SUCCESS_RESPONSE_TEXT
    params = {"address": "Test Address", "postalCode": "12345", "dawnDelivery": "Y"}
    response = client.get(
        "/api/mall/possibleDelivery",
        params=params,
        headers={"Authorization": MOCK_AUTH_TOKEN}
    )
    assert response.status_code == 200
    assert response.json() == MOCK_SUCCESS_RESPONSE_TEXT
    mock_service.assert_called_once_with(
        address=params["address"],
        authorization=MOCK_AUTH_TOKEN,
        postal_code=params["postalCode"],
        dawn_delivery=params["dawnDelivery"]
    )

def test_check_possible_delivery_endpoint_missing_address(client: TestClient):
    response = client.get(
        "/api/mall/possibleDelivery",
        headers={"Authorization": MOCK_AUTH_TOKEN}
        # Missing 'address' query parameter
    )
    assert response.status_code == 422 # FastAPI unprocessable entity

# Return Controller Tests
@patch("app.services.mall.return_service.request_return_delivery", new_callable=AsyncMock)
def test_request_return_delivery_endpoint_success(mock_service, client: TestClient):
    mock_service.return_value = MOCK_SUCCESS_RESPONSE_TEXT
    payload = {"invoiceNumber": "returnInv1"}
    response = client.post(
        "/api/mall/returnDelivery",
        json=payload,
        headers={"Authorization": MOCK_AUTH_TOKEN}
    )
    assert response.status_code == 200
    assert response.json() == MOCK_SUCCESS_RESPONSE_TEXT
    mock_service.assert_called_once()
    assert mock_service.call_args[0][0].invoiceNumber == payload["invoiceNumber"]
    assert mock_service.call_args[0][1] == MOCK_AUTH_TOKEN

def test_request_return_delivery_endpoint_missing_auth(client: TestClient):
    response = client.post("/api/mall/returnDelivery", json={"invoiceNumber": "returnInv1"})
    assert response.status_code == 400

@patch("app.services.mall.return_service.register_return_list", new_callable=AsyncMock)
def test_register_return_list_endpoint_success(mock_service, client: TestClient):
    mock_service.return_value = MOCK_SUCCESS_RESPONSE_TEXT
    payload = {
        "goodsList": [{
            "deliveryAddress": "Return Addr",
            "deliveryName": "Return User",
            "deliveryPhone": "5555555555",
            "mallName": "Return Mall"
        }]
    }
    response = client.post(
        "/api/mall/returnListRegister",
        json=payload,
        headers={"Authorization": MOCK_AUTH_TOKEN}
    )
    assert response.status_code == 200
    assert response.json() == MOCK_SUCCESS_RESPONSE_TEXT
    mock_service.assert_called_once()
    assert mock_service.call_args[0][0].goodsList[0].deliveryName == payload["goodsList"][0]["deliveryName"]
    assert mock_service.call_args[0][1] == MOCK_AUTH_TOKEN

@patch("app.services.mall.return_service.register_return", new_callable=AsyncMock)
def test_register_return_endpoint_success(mock_service, client: TestClient):
    mock_service.return_value = MOCK_SUCCESS_RESPONSE_TEXT
    payload = { # GoodsNoDawnDTO
        "deliveryAddress": "Single Return Addr",
        "deliveryName": "Single Return User",
        "deliveryPhone": "1112223333",
        "mallName": "Single Return Mall"
    }
    response = client.post(
        "/api/mall/returnRegister",
        json=payload,
        headers={"Authorization": MOCK_AUTH_TOKEN}
    )
    assert response.status_code == 200
    assert response.json() == MOCK_SUCCESS_RESPONSE_TEXT
    mock_service.assert_called_once()
    assert mock_service.call_args[0][0].mallName == payload["mallName"]
    assert mock_service.call_args[0][1] == MOCK_AUTH_TOKEN
