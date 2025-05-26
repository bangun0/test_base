import pytest
from pydantic import ValidationError
from app.schemas.mall.cancel_delivery import CancelDeliveryRequest
from app.schemas.mall.delivery_list_register import GoodsNoDawnDTO, MallApiDeliveryDTO
from app.schemas.mall.delivery_register import GoodsDTO
from app.schemas.mall.return_delivery import ReturnDeliveryRequest
from app.schemas.mall.return_list_register import MallApiReturnDTO
# ReturnRegisterRequest is an alias for GoodsNoDawnDTO, so it's already covered by GoodsNoDawnDTO tests

def test_cancel_delivery_request_valid():
    data = {"invoiceNumber": "123456789012"}
    req = CancelDeliveryRequest(**data)
    assert req.invoiceNumber == "123456789012"

def test_cancel_delivery_request_invalid():
    with pytest.raises(ValidationError):
        CancelDeliveryRequest() # invoiceNumber is required

def test_goods_no_dawn_dto_valid():
    data = {
        "deliveryAddress": "123 Main St",
        "deliveryName": "John Doe",
        "deliveryPhone": "555-1234",
        "mallName": "TestMall",
        "childrenMallId": "child1",
        "invoiceNumber": "inv123",
        "invoicePrintYn": "Y",
        "quantity": 1,
    }
    dto = GoodsNoDawnDTO(**data)
    assert dto.deliveryAddress == "123 Main St"
    assert dto.invoicePrintYn == "Y"

def test_goods_no_dawn_dto_invalid_required():
    with pytest.raises(ValidationError):
        GoodsNoDawnDTO(deliveryName="Test", deliveryPhone="123", mallName="TestMall") # deliveryAddress missing

def test_goods_no_dawn_dto_invalid_invoice_print_yn():
    data = {
        "deliveryAddress": "123 Main St",
        "deliveryName": "John Doe",
        "deliveryPhone": "555-1234",
        "mallName": "TestMall",
        "invoicePrintYn": "Maybe" 
    }
    with pytest.raises(ValidationError):
        GoodsNoDawnDTO(**data)

def test_goods_no_dawn_dto_invoice_number_max_length():
    data = {
        "deliveryAddress": "123 Main St",
        "deliveryName": "John Doe",
        "deliveryPhone": "555-1234",
        "mallName": "TestMall",
        "invoiceNumber": "1234567890123" # 13 chars
    }
    with pytest.raises(ValidationError):
        GoodsNoDawnDTO(**data)
    
    data["invoiceNumber"] = "123456789012" # 12 chars
    dto = GoodsNoDawnDTO(**data)
    assert dto.invoiceNumber == "123456789012"


def test_mall_api_delivery_dto_valid():
    goods_data = {
        "deliveryAddress": "123 Main St",
        "deliveryName": "Jane Doe",
        "deliveryPhone": "555-5678",
        "mallName": "AnotherMall"
    }
    data = {"goodsList": [goods_data]}
    dto = MallApiDeliveryDTO(**data)
    assert len(dto.goodsList) == 1
    assert dto.goodsList[0].deliveryName == "Jane Doe"
    assert dto.dawnDelivery is None

    data_with_dawn = {"dawnDelivery": "Y", "goodsList": [goods_data]}
    dto_dawn = MallApiDeliveryDTO(**data_with_dawn)
    assert dto_dawn.dawnDelivery == "Y"


def test_mall_api_delivery_dto_invalid_missing_goods_list():
    with pytest.raises(ValidationError):
        MallApiDeliveryDTO() # goodsList is required

def test_mall_api_delivery_dto_invalid_goods_list_item():
    invalid_goods_data = {"deliveryName": "MissingAddress"}
    data = {"goodsList": [invalid_goods_data]}
    with pytest.raises(ValidationError):
        MallApiDeliveryDTO(**data)

def test_goods_dto_valid():
    data = {
        "deliveryAddress": "456 Oak St",
        "deliveryName": "Peter Pan",
        "deliveryPhone": "555-0000",
        "mallName": "Neverland Store",
        "dawnDelivery": "Y",
    }
    dto = GoodsDTO(**data)
    assert dto.deliveryAddress == "456 Oak St"
    assert dto.dawnDelivery == "Y"

def test_goods_dto_invalid_required():
    with pytest.raises(ValidationError):
        GoodsDTO(deliveryName="Test", deliveryPhone="123", mallName="TestMall") # deliveryAddress missing

def test_return_delivery_request_valid():
    data = {"invoiceNumber": "return12345"}
    req = ReturnDeliveryRequest(**data)
    assert req.invoiceNumber == "return12345"

def test_return_delivery_request_invalid():
    with pytest.raises(ValidationError):
        ReturnDeliveryRequest() # invoiceNumber is required

def test_mall_api_return_dto_valid():
    goods_data = {
        "deliveryAddress": "789 Pine St",
        "deliveryName": "Alice Wonderland",
        "deliveryPhone": "555-1111",
        "mallName": "WonderMall"
    }
    data = {"goodsList": [goods_data]}
    dto = MallApiReturnDTO(**data)
    assert len(dto.goodsList) == 1
    assert dto.goodsList[0].mallName == "WonderMall"

def test_mall_api_return_dto_invalid_missing_goods_list():
    with pytest.raises(ValidationError):
        MallApiReturnDTO() # goodsList is required

# ReturnRegisterRequest is an alias for GoodsNoDawnDTO, 
# so its validation is covered by test_goods_no_dawn_dto_valid and test_goods_no_dawn_dto_invalid_required
# No separate tests needed unless it has its own distinct logic or fields in the future.

# Example of testing optional fields default values if any
def test_goods_no_dawn_dto_defaults():
    data = {
        "deliveryAddress": "123 Main St",
        "deliveryName": "John Doe",
        "deliveryPhone": "555-1234",
        "mallName": "TestMall",
    }
    dto = GoodsNoDawnDTO(**data)
    assert dto.invoicePrintYn == "N" # Default value
    assert dto.childrenMallId is None
    assert dto.deliveryAddressEng is None
    assert dto.deliveryMessage is None
    assert dto.deliveryPostal is None
    assert dto.deliveryTel is None
    assert dto.goodsName is None
    assert dto.invoiceNumber is None
    assert dto.optionName is None
    assert dto.orderNumber is None
    assert dto.quantity is None
    assert dto.reserveDt is None

def test_goods_dto_defaults():
    data = {
        "deliveryAddress": "456 Oak St",
        "deliveryName": "Peter Pan",
        "deliveryPhone": "555-0000",
        "mallName": "Neverland Store",
    }
    dto = GoodsDTO(**data)
    assert dto.invoicePrintYn == "N"
    assert dto.dawnDelivery is None
    assert dto.childrenMallId is None
    assert dto.deliveryAddressEng is None
    assert dto.deliveryMessage is None
    assert dto.deliveryPostal is None
    assert dto.deliveryTel is None
    assert dto.goodsName is None
    assert dto.invoiceNumber is None
    assert dto.optionName is None
    assert dto.orderNumber is None
    assert dto.quantity is None
    assert dto.reserveDt is None
