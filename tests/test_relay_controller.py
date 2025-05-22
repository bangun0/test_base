import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
import httpx

# Import the FastAPI application instance
from app.main import app

# Mark all tests in this module as asyncio
pytestmark = pytest.mark.asyncio

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture
def mock_httpx_request(mocker):
    # This fixture provides a mock for httpx.AsyncClient.request
    # It's set up to be an AsyncMock by default
    mock = mocker.patch("httpx.AsyncClient.request", new_callable=AsyncMock)
    return mock

async def test_relay_get_request(client: TestClient, mock_httpx_request: AsyncMock):
    """Test GET request forwarding, including path, query params, headers, and response."""
    mock_response_content = {"message": "Success from external GET"}
    mock_response_status = 200
    mock_response_headers = {"X-External-Header": "ExternalValue", "Content-Type": "application/json"}

    mock_httpx_request.return_value = httpx.Response(
        status_code=mock_response_status,
        json=mock_response_content,
        headers=mock_response_headers
    )

    path = "some/path"
    query_params = {"param1": "value1", "param2": "value2"}
    request_headers = {"X-Client-Header": "ClientValue", "Accept": "application/json"}

    response = client.get(f"/api/relay/{path}", params=query_params, headers=request_headers)

    assert response.status_code == mock_response_status
    assert response.json() == mock_response_content
    # Check for external header (Content-Type might be modified by TestClient/FastAPI)
    assert response.headers.get("X-External-Header") == "ExternalValue"
    
    # Assert httpx.AsyncClient.request was called correctly
    expected_external_url = f"https://admin.todaypickup.com/v2/api-docs/{path}?param1=value1&param2=value2"
    mock_httpx_request.assert_called_once()
    call_args = mock_httpx_request.call_args[1] # kwargs of the call
    
    assert call_args['method'] == "GET"
    assert call_args['url'] == expected_external_url
    assert call_args['content'] is None # No body for GET
    
    # Check forwarded headers (excluding Host, and including client-specific ones)
    forwarded_headers = call_args['headers']
    assert "X-Client-Header" in forwarded_headers
    assert forwarded_headers["X-Client-Header"] == "ClientValue"
    assert "accept" in forwarded_headers 
    assert "host" not in forwarded_headers # TestClient might add its own, but our controller should strip it

async def test_relay_post_request(client: TestClient, mock_httpx_request: AsyncMock):
    """Test POST request forwarding, including path, JSON body, headers, and response."""
    mock_response_content = {"message": "Success from external POST", "id": 123}
    mock_response_status = 201
    mock_response_headers = {"X-Created-Id": "123", "Content-Type": "application/json"}

    mock_httpx_request.return_value = httpx.Response(
        status_code=mock_response_status,
        json=mock_response_content,
        headers=mock_response_headers
    )

    path = "submit/data"
    request_body = {"key": "value", "number": 42}
    request_headers = {"X-Client-Specific": "PostValue", "Content-Type": "application/json"}

    response = client.post(f"/api/relay/{path}", json=request_body, headers=request_headers)

    assert response.status_code == mock_response_status
    assert response.json() == mock_response_content
    assert response.headers.get("X-Created-Id") == "123"

    # Assert httpx.AsyncClient.request was called correctly
    expected_external_url = f"https://admin.todaypickup.com/v2/api-docs/{path}"
    mock_httpx_request.assert_called_once()
    call_args = mock_httpx_request.call_args[1]

    assert call_args['method'] == "POST"
    assert call_args['url'] == expected_external_url
    assert call_args['content'] == b'{"key": "value", "number": 42}' # TestClient sends json as bytes
    
    forwarded_headers = call_args['headers']
    assert "X-Client-Specific" in forwarded_headers
    assert forwarded_headers["X-Client-Specific"] == "PostValue"
    assert "content-type" in forwarded_headers # TestClient adds this
    assert forwarded_headers["content-type"] == "application/json"


@pytest.mark.parametrize("method", ["PUT", "DELETE"])
async def test_relay_other_methods(client: TestClient, mock_httpx_request: AsyncMock, method: str):
    """Test forwarding of other HTTP methods like PUT and DELETE."""
    mock_response_status = 204 if method == "DELETE" else 200
    mock_httpx_request.return_value = httpx.Response(status_code=mock_response_status)

    path = f"resource/{method.lower()}"
    
    if method in ["PUT", "PATCH"]: # Methods that might have a body
        response = client.request(method, f"/api/relay/{path}", json={"data": "update"})
    else:
        response = client.request(method, f"/api/relay/{path}")

    assert response.status_code == mock_response_status

    expected_external_url = f"https://admin.todaypickup.com/v2/api-docs/{path}"
    mock_httpx_request.assert_called_once()
    call_args = mock_httpx_request.call_args[1]

    assert call_args['method'] == method
    assert call_args['url'] == expected_external_url

async def test_relay_header_forwarding(client: TestClient, mock_httpx_request: AsyncMock):
    """Test that client headers are forwarded and external API headers are relayed back."""
    # Mock external API response
    external_api_headers = {"X-External-Response-Header": "ExternalValue", "Connection": "should-be-removed"}
    mock_httpx_request.return_value = httpx.Response(200, text="OK", headers=external_api_headers)

    # Client request
    client_request_headers = {"X-Client-Request-Header": "ClientValue", "Host": "should-be-removed-by-controller"}
    path = "header/test"
    response = client.get(f"/api/relay/{path}", headers=client_request_headers)

    # Assertions for response headers (from external API)
    assert response.status_code == 200
    assert response.headers.get("X-External-Response-Header") == "ExternalValue"
    assert "Connection" not in response.headers # Hop-by-hop should be removed by httpx or FastAPI

    # Assertions for forwarded headers (to external API)
    mock_httpx_request.assert_called_once()
    forwarded_to_external_headers = mock_httpx_request.call_args[1]['headers']
    
    assert "X-Client-Request-Header" in forwarded_to_external_headers
    assert forwarded_to_external_headers["X-Client-Request-Header"] == "ClientValue"
    assert "host" not in forwarded_to_external_headers # Controller should remove it

async def test_relay_gateway_timeout(client: TestClient, mock_httpx_request: AsyncMock):
    """Test 504 Gateway Timeout when external API call times out."""
    mock_httpx_request.side_effect = httpx.TimeoutException("Request timed out", request=None) # type: ignore

    path = "timeout/test"
    response = client.get(f"/api/relay/{path}")

    assert response.status_code == 504
    assert "Gateway timeout" in response.json()["detail"]

async def test_relay_bad_gateway(client: TestClient, mock_httpx_request: AsyncMock):
    """Test 502 Bad Gateway when external API call fails with RequestError."""
    mock_httpx_request.side_effect = httpx.RequestError("Network error", request=None) # type: ignore

    path = "networkerror/test"
    response = client.get(f"/api/relay/{path}")

    assert response.status_code == 502
    assert "Bad gateway" in response.json()["detail"]

async def test_relay_internal_server_error_unexpected(client: TestClient, mock_httpx_request: AsyncMock):
    """Test 500 Internal Server Error for other unexpected issues."""
    # Simulate an unexpected error during the processing, after httpx call or within it
    # For instance, if rp.headers.items() or rp.content itself raised an error
    # Here we mock an error during the client.request call itself as a generic Exception
    mock_httpx_request.side_effect = Exception("Unexpected catastrophic failure")

    path = "unexpected/error"
    response = client.get(f"/api/relay/{path}")

    assert response.status_code == 500 # As per the controller's generic exception handler
    assert "Internal server error" in response.json()["detail"]

# TODO: Add test for query parameters being correctly relayed if not already covered enough.
# test_relay_get_request covers query params.

# TODO: Consider testing for binary responses if that's a use case.
# The controller uses rp.content which is good for binary. Test could verify Content-Type.
# For now, JSON and basic text are implicitly covered.

# TODO: Test case for when request.body() is empty but method is POST/PUT.
# The controller sends `content=body if body else None`. `httpx` handles this.

# TODO: Check if any sensitive headers from the external API response should be filtered out.
# The controller currently passes all headers from external API. This is per current spec.
# Example: `response_headers.pop("set-cookie", None)` if cookies shouldn't be relayed.

# Final check on hop-by-hop headers in response.
# The controller code does:
# for name, value in rp.headers.items():
#     response_headers[name] = value
# This will include hop-by-hop headers from the external service if they are present.
# Standard practice is that these should be handled by the server (FastAPI/uvicorn)
# and not explicitly stripped in the application layer unless strictly necessary.
# TestClient/httpx might also handle/strip some of these.
# `test_relay_header_forwarding` checks "Connection" header isn't in final response.
# This seems fine for now.
