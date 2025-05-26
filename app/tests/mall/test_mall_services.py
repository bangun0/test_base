import pytest
import httpx
from respx import MockRouter
from app.schemas.mall.cancel_delivery import CancelDeliveryRequest
from app.schemas.mall.delivery_list_register import MallApiDeliveryDTO, GoodsNoDawnDTO
from app.schemas.mall.delivery_register import GoodsDTO
from app.schemas.mall.return_delivery import ReturnDeliveryRequest
from app.schemas.mall.return_list_register import MallApiReturnDTO
from app.services.mall import delivery_service, return_service

TODAY_PICKUP_API_BASE_URL = "https://admin.todaypickup.com"
MOCK_AUTH_TOKEN = "test_auth_token"

@pytest.mark.asyncio
async def test_cancel_delivery_service_success(respx_mock: MockRouter):
    request_data = CancelDeliveryRequest(invoiceNumber="inv123")
    expected_response_text = "Cancel success"
    
    respx_mock.post(f"{TODAY_PICKUP_API_BASE_URL}/api/mall/cancelDelivery").mock(
        return_value=httpx.Response(200, text=expected_response_text)
    )

    response = await delivery_service.cancel_delivery(request_data, MOCK_AUTH_TOKEN)
    
    assert response == expected_response_text
    called_request = respx_mock.calls.last.request
    assert called_request.method == "POST"
    assert str(called_request.url) == f"{TODAY_PICKUP_API_BASE_URL}/api/mall/cancelDelivery"
    assert called_request.headers["authorization"] == MOCK_AUTH_TOKEN
    assert await called_request.aread() == request_data.model_dump_json().encode()


@pytest.mark.asyncio
async def test_cancel_delivery_service_http_error(respx_mock: MockRouter):
    request_data = CancelDeliveryRequest(invoiceNumber="inv123")
    
    respx_mock.post(f"{TODAY_PICKUP_API_BASE_URL}/api/mall/cancelDelivery").mock(
        return_value=httpx.Response(400, text="Bad Request")
    )

    with pytest.raises(httpx.HTTPStatusError):
        await delivery_service.cancel_delivery(request_data, MOCK_AUTH_TOKEN)

@pytest.mark.asyncio
async def test_get_delivery_info_service_success(respx_mock: MockRouter):
    invoice_number = "inv789"
    expected_response_text = "Delivery info"

    respx_mock.get(f"{TODAY_PICKUP_API_BASE_URL}/api/mall/delivery/{invoice_number}").mock(
        return_value=httpx.Response(200, text=expected_response_text)
    )

    response = await delivery_service.get_delivery_info(invoice_number, MOCK_AUTH_TOKEN)

    assert response == expected_response_text
    called_request = respx_mock.calls.last.request
    assert called_request.method == "GET"
    assert called_request.headers["authorization"] == MOCK_AUTH_TOKEN

@pytest.mark.asyncio
async def test_get_delivery_list_info_service_success(respx_mock: MockRouter):
    invoice_list = "inv1,inv2"
    expected_response_text = "Delivery list info"

    respx_mock.get(f"{TODAY_PICKUP_API_BASE_URL}/api/mall/deliveryList/{invoice_list}").mock(
        return_value=httpx.Response(200, text=expected_response_text)
    )
    response = await delivery_service.get_delivery_list_info(invoice_list, MOCK_AUTH_TOKEN)
    assert response == expected_response_text
    called_request = respx_mock.calls.last.request
    assert called_request.method == "GET"
    assert called_request.headers["authorization"] == MOCK_AUTH_TOKEN


@pytest.mark.asyncio
async def test_register_delivery_list_service_success(respx_mock: MockRouter):
    goods_item = GoodsNoDawnDTO(deliveryAddress="addr", deliveryName="name", deliveryPhone="phone", mallName="mall")
    request_data = MallApiDeliveryDTO(goodsList=[goods_item])
    expected_response_text = "Register list success"

    respx_mock.post(f"{TODAY_PICKUP_API_BASE_URL}/api/mall/deliveryListRegister").mock(
        return_value=httpx.Response(200, text=expected_response_text)
    )
    response = await delivery_service.register_delivery_list(request_data, MOCK_AUTH_TOKEN)
    assert response == expected_response_text
    called_request = respx_mock.calls.last.request
    assert called_request.method == "POST"
    assert await called_request.aread() == request_data.model_dump_json().encode()
    assert called_request.headers["authorization"] == MOCK_AUTH_TOKEN

@pytest.mark.asyncio
async def test_register_delivery_service_success(respx_mock: MockRouter):
    request_data = GoodsDTO(deliveryAddress="addr", deliveryName="name", deliveryPhone="phone", mallName="mall")
    expected_response_text = "Register success"

    respx_mock.post(f"{TODAY_PICKUP_API_BASE_URL}/api/mall/deliveryRegister").mock(
        return_value=httpx.Response(200, text=expected_response_text)
    )
    response = await delivery_service.register_delivery(request_data, MOCK_AUTH_TOKEN)
    assert response == expected_response_text
    called_request = respx_mock.calls.last.request
    assert called_request.method == "POST"
    assert await called_request.aread() == request_data.model_dump_json().encode()
    assert called_request.headers["authorization"] == MOCK_AUTH_TOKEN


@pytest.mark.asyncio
async def test_check_possible_delivery_service_success(respx_mock: MockRouter):
    address = "123 Main St"
    postal_code = "12345"
    dawn_delivery = "Y"
    expected_response_text = "Possible"

    url = f"{TODAY_PICKUP_API_BASE_URL}/api/mall/possibleDelivery"
    respx_mock.get(url).mock(
        return_value=httpx.Response(200, text=expected_response_text)
    )
    
    response = await delivery_service.check_possible_delivery(
        address, MOCK_AUTH_TOKEN, postal_code, dawn_delivery
    )
    assert response == expected_response_text
    called_request = respx_mock.calls.last.request
    assert called_request.method == "GET"
    assert str(called_request.url.params) == f"address={address.replace(' ', '+')}&postalCode={postal_code}&dawnDelivery={dawn_delivery}" # httpx encodes params
    assert called_request.headers["authorization"] == MOCK_AUTH_TOKEN

@pytest.mark.asyncio
async def test_check_possible_delivery_service_no_optionals_success(respx_mock: MockRouter):
    address = "123 Main St"
    expected_response_text = "Possible"

    url = f"{TODAY_PICKUP_API_BASE_URL}/api/mall/possibleDelivery"
    respx_mock.get(url).mock(
        return_value=httpx.Response(200, text=expected_response_text)
    )
    
    response = await delivery_service.check_possible_delivery(address, MOCK_AUTH_TOKEN)
    assert response == expected_response_text
    called_request = respx_mock.calls.last.request
    assert str(called_request.url.params) == f"address={address.replace(' ', '+')}"


# Return Services Tests
@pytest.mark.asyncio
async def test_request_return_delivery_service_success(respx_mock: MockRouter):
    request_data = ReturnDeliveryRequest(invoiceNumber="return123")
    expected_response_text = "Return request success"

    respx_mock.post(f"{TODAY_PICKUP_API_BASE_URL}/api/mall/returnDelivery").mock(
        return_value=httpx.Response(200, text=expected_response_text)
    )
    response = await return_service.request_return_delivery(request_data, MOCK_AUTH_TOKEN)
    assert response == expected_response_text
    called_request = respx_mock.calls.last.request
    assert called_request.method == "POST"
    assert await called_request.aread() == request_data.model_dump_json().encode()
    assert called_request.headers["authorization"] == MOCK_AUTH_TOKEN

@pytest.mark.asyncio
async def test_request_return_delivery_service_http_error(respx_mock: MockRouter):
    request_data = ReturnDeliveryRequest(invoiceNumber="return123")
    respx_mock.post(f"{TODAY_PICKUP_API_BASE_URL}/api/mall/returnDelivery").mock(
        return_value=httpx.Response(500, text="Server Error")
    )
    with pytest.raises(httpx.HTTPStatusError):
        await return_service.request_return_delivery(request_data, MOCK_AUTH_TOKEN)

@pytest.mark.asyncio
async def test_register_return_list_service_success(respx_mock: MockRouter):
    goods_item = GoodsNoDawnDTO(deliveryAddress="addr_ret", deliveryName="name_ret", deliveryPhone="phone_ret", mallName="mall_ret")
    request_data = MallApiReturnDTO(goodsList=[goods_item])
    expected_response_text = "Return list register success"

    respx_mock.post(f"{TODAY_PICKUP_API_BASE_URL}/api/mall/returnListRegister").mock(
        return_value=httpx.Response(200, text=expected_response_text)
    )
    response = await return_service.register_return_list(request_data, MOCK_AUTH_TOKEN)
    assert response == expected_response_text
    called_request = respx_mock.calls.last.request
    assert called_request.method == "POST"
    assert await called_request.aread() == request_data.model_dump_json().encode()
    assert called_request.headers["authorization"] == MOCK_AUTH_TOKEN

@pytest.mark.asyncio
async def test_register_return_service_success(respx_mock: MockRouter):
    request_data = GoodsNoDawnDTO(deliveryAddress="addr_ret_single", deliveryName="name_ret_single", deliveryPhone="phone_ret_single", mallName="mall_ret_single")
    expected_response_text = "Return register success"

    respx_mock.post(f"{TODAY_PICKUP_API_BASE_URL}/api/mall/returnRegister").mock(
        return_value=httpx.Response(200, text=expected_response_text)
    )
    response = await return_service.register_return(request_data, MOCK_AUTH_TOKEN)
    assert response == expected_response_text
    called_request = respx_mock.calls.last.request
    assert called_request.method == "POST"
    assert await called_request.aread() == request_data.model_dump_json().encode()
    assert called_request.headers["authorization"] == MOCK_AUTH_TOKEN
