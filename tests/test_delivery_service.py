import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.config.database import Base
from app.services.delivery_service import DeliveryService
from app.schemas.delivery import (
    DeliveryCreate, DeliveryListCreate, DeliveryCancelRequest,
    DeliveryReturnRequest, PossibleDeliveryRequest, DeliveryFlexTransferRequest,
    DeliveryStatusUpdateRequest
)
from app.models.delivery import Delivery


@pytest.fixture
def db_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def delivery_service(db_session):
    return DeliveryService(db_session, "test_auth_token")


@pytest.fixture
def sample_delivery_data():
    return DeliveryCreate(
        sender_name="발송자",
        sender_phone="010-1234-5678",
        sender_zipcode="12345",
        sender_address1="서울시 강남구",
        sender_address2="테헤란로 123",
        receiver_name="수령자",
        receiver_phone="010-9876-5432",
        receiver_zipcode="54321",
        receiver_address1="서울시 서초구",
        receiver_address2="강남대로 456",
        product_name="테스트 상품",
        product_quantity=1,
        payment_type="PREPAID",
        collect_amount=0,
        delivery_memo="조심히 배송해주세요",
        delivery_date="2024-01-15"
    )


class TestDeliveryService:
    
    @pytest.mark.asyncio
    async def test_register_delivery_success(self, delivery_service, sample_delivery_data):
        # Mock external API response
        mock_external_response = {
            "success": True,
            "invoice_number": "INV1234567890",
            "status": "REGISTERED"
        }
        
        with patch.object(delivery_service.client, 'register_delivery', new_callable=AsyncMock) as mock_register:
            mock_register.return_value = mock_external_response
            
            result = await delivery_service.register_delivery(sample_delivery_data)
            
            assert result is not None
            assert result.sender_name == "발송자"
            assert result.receiver_name == "수령자"
            assert result.product_name == "테스트 상품"
            assert result.status == "REGISTERED"
            assert result.external_response == mock_external_response
            
            mock_register.assert_called_once_with(sample_delivery_data.model_dump(), "test_auth_token")

    @pytest.mark.asyncio
    async def test_register_delivery_list_success(self, delivery_service, sample_delivery_data):
        # Create delivery list
        delivery_list = DeliveryListCreate(deliveries=[sample_delivery_data, sample_delivery_data])
        
        mock_external_response = {
            "success": True,
            "registered_count": 2
        }
        
        with patch.object(delivery_service.client, 'register_delivery_list', new_callable=AsyncMock) as mock_register:
            mock_register.return_value = mock_external_response
            
            results = await delivery_service.register_delivery_list(delivery_list)
            
            assert len(results) == 2
            for result in results:
                assert result.sender_name == "발송자"
                assert result.external_response == mock_external_response
            
            mock_register.assert_called_once()

    @pytest.mark.asyncio
    async def test_lookup_delivery_success(self, delivery_service):
        # First create a delivery in the database
        delivery_data = {
            "sender_name": "발송자",
            "receiver_name": "수령자",
            "product_name": "테스트 상품",
            "status": "IN_TRANSIT"
        }
        delivery = delivery_service.repository.create(delivery_data)
        
        mock_external_response = {
            "status": "DELIVERED",
            "tracking_info": [
                {"status": "DELIVERED", "date": "2024-01-15", "location": "서울시"}
            ]
        }
        
        with patch.object(delivery_service.client, 'lookup_delivery', new_callable=AsyncMock) as mock_lookup:
            mock_lookup.return_value = mock_external_response
            
            result = await delivery_service.lookup_delivery(delivery.invoice_number)
            
            assert result is not None
            assert result.invoice_number == delivery.invoice_number
            assert result.status == "DELIVERED"
            assert result.delivery_info == mock_external_response
            
            mock_lookup.assert_called_once_with(delivery.invoice_number, "test_auth_token")

    @pytest.mark.asyncio
    async def test_cancel_delivery_success(self, delivery_service):
        # Create a delivery first
        delivery_data = {
            "sender_name": "발송자",
            "receiver_name": "수령자",
            "product_name": "테스트 상품",
            "status": "REGISTERED"
        }
        delivery = delivery_service.repository.create(delivery_data)
        
        cancel_request = DeliveryCancelRequest(
            invoice_number=delivery.invoice_number,
            cancel_reason="고객 요청"
        )
        
        mock_external_response = {
            "success": True,
            "cancelled": True
        }
        
        with patch.object(delivery_service.client, 'cancel_delivery', new_callable=AsyncMock) as mock_cancel:
            mock_cancel.return_value = mock_external_response
            
            result = await delivery_service.cancel_delivery(cancel_request)
            
            assert result is True
            
            # Check that the delivery status was updated
            updated_delivery = delivery_service.repository.get_by_invoice_number(delivery.invoice_number)
            assert updated_delivery.status == "CANCELLED"
            
            mock_cancel.assert_called_once_with(cancel_request.model_dump(), "test_auth_token")

    @pytest.mark.asyncio
    async def test_request_return_delivery_success(self, delivery_service):
        # Create a delivery first
        delivery_data = {
            "sender_name": "발송자",
            "receiver_name": "수령자",
            "product_name": "테스트 상품",
            "status": "DELIVERED"
        }
        delivery = delivery_service.repository.create(delivery_data)
        
        return_request = DeliveryReturnRequest(
            invoice_number=delivery.invoice_number,
            return_reason="상품 불량",
            return_address="반품 주소"
        )
        
        mock_external_response = {
            "success": True,
            "return_requested": True
        }
        
        with patch.object(delivery_service.client, 'request_return_delivery', new_callable=AsyncMock) as mock_return:
            mock_return.return_value = mock_external_response
            
            result = await delivery_service.request_return_delivery(return_request)
            
            assert result is True
            
            # Check that the delivery status was updated
            updated_delivery = delivery_service.repository.get_by_invoice_number(delivery.invoice_number)
            assert updated_delivery.status == "RETURN_REQUESTED"
            
            mock_return.assert_called_once_with(return_request.model_dump(), "test_auth_token")

    @pytest.mark.asyncio
    async def test_check_possible_delivery_success(self, delivery_service):
        request = PossibleDeliveryRequest(
            zipcode="12345",
            address="서울시 강남구 테헤란로 123"
        )
        
        mock_external_response = {
            "possible": True,
            "estimated_date": "2024-01-16",
            "fee": 3000
        }
        
        with patch.object(delivery_service.client, 'check_possible_delivery', new_callable=AsyncMock) as mock_check:
            mock_check.return_value = mock_external_response
            
            result = await delivery_service.check_possible_delivery(request)
            
            assert result.is_possible is True
            assert result.estimated_delivery_date == "2024-01-16"
            assert result.delivery_fee == 3000
            
            mock_check.assert_called_once_with(request.zipcode, request.address, "test_auth_token")

    @pytest.mark.asyncio
    async def test_transfer_to_flex_success(self, delivery_service):
        # Create a delivery first
        delivery_data = {
            "sender_name": "발송자",
            "receiver_name": "수령자",
            "product_name": "테스트 상품",
            "status": "ASSIGNED"
        }
        delivery = delivery_service.repository.create(delivery_data)
        
        transfer_request = DeliveryFlexTransferRequest(
            invoice_number=delivery.invoice_number,
            reason="배송 불가"
        )
        
        mock_external_response = {
            "success": True,
            "transferred_to_flex": True
        }
        
        with patch.object(delivery_service.client, 'agency_transfer_to_flex', new_callable=AsyncMock) as mock_transfer:
            mock_transfer.return_value = mock_external_response
            
            result = await delivery_service.transfer_to_flex(transfer_request)
            
            assert result is True
            
            # Check that the delivery was transferred to flex
            updated_delivery = delivery_service.repository.get_by_invoice_number(delivery.invoice_number)
            assert updated_delivery.is_flex is True
            assert updated_delivery.status == "FLEX_TRANSFERRED"
            
            mock_transfer.assert_called_once_with(transfer_request.model_dump(), "test_auth_token")

    @pytest.mark.asyncio
    async def test_update_delivery_status_success(self, delivery_service):
        # Create a delivery first
        delivery_data = {
            "sender_name": "발송자",
            "receiver_name": "수령자",
            "product_name": "테스트 상품",
            "status": "IN_TRANSIT"
        }
        delivery = delivery_service.repository.create(delivery_data)
        
        status_request = DeliveryStatusUpdateRequest(
            invoice_number=delivery.invoice_number,
            status="OUT_FOR_DELIVERY",
            location="배송 센터",
            memo="배송 출발"
        )
        
        mock_external_response = {
            "success": True,
            "status_updated": True
        }
        
        with patch.object(delivery_service.client, 'agency_update_delivery_state', new_callable=AsyncMock) as mock_update:
            mock_update.return_value = mock_external_response
            
            result = await delivery_service.update_delivery_status(status_request)
            
            assert result is True
            
            # Check that the delivery status was updated
            updated_delivery = delivery_service.repository.get_by_invoice_number(delivery.invoice_number)
            assert updated_delivery.status == "OUT_FOR_DELIVERY"
            
            # Check that tracking was added
            tracking_info = delivery_service.repository.get_tracking_by_invoice(delivery.invoice_number)
            assert len(tracking_info) == 1
            assert tracking_info[0].status == "OUT_FOR_DELIVERY"
            assert tracking_info[0].location == "배송 센터"
            
            mock_update.assert_called_once_with(status_request.model_dump(), "test_auth_token")

    def test_get_delivery_by_invoice_success(self, delivery_service):
        # Create a delivery first
        delivery_data = {
            "sender_name": "발송자",
            "receiver_name": "수령자",
            "product_name": "테스트 상품",
            "status": "REGISTERED"
        }
        delivery = delivery_service.repository.create(delivery_data)
        
        result = delivery_service.get_delivery_by_invoice(delivery.invoice_number)
        
        assert result is not None
        assert result.sender_name == "발송자"
        assert result.receiver_name == "수령자"
        assert result.invoice_number == delivery.invoice_number

    def test_get_delivery_by_invoice_not_found(self, delivery_service):
        result = delivery_service.get_delivery_by_invoice("NONEXISTENT")
        assert result is None

    def test_get_deliveries_by_date_success(self, delivery_service):
        # Create multiple deliveries with the same date
        delivery_date = "2024-01-15"
        for i in range(3):
            delivery_data = {
                "sender_name": f"발송자{i}",
                "receiver_name": f"수령자{i}",
                "product_name": f"테스트 상품{i}",
                "delivery_date": delivery_date,
                "status": "REGISTERED"
            }
            delivery_service.repository.create(delivery_data)
        
        results = delivery_service.get_deliveries_by_date(delivery_date)
        
        assert len(results) == 3
        for result in results:
            assert result.delivery_date == delivery_date

    @pytest.mark.asyncio
    async def test_register_delivery_external_api_error(self, delivery_service, sample_delivery_data):
        with patch.object(delivery_service.client, 'register_delivery', new_callable=AsyncMock) as mock_register:
            mock_register.side_effect = Exception("External API error")
            
            with pytest.raises(ValueError) as exc_info:
                await delivery_service.register_delivery(sample_delivery_data)
            
            assert "배송 등록 중 오류가 발생했습니다" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_lookup_delivery_external_api_error(self, delivery_service):
        with patch.object(delivery_service.client, 'lookup_delivery', new_callable=AsyncMock) as mock_lookup:
            mock_lookup.side_effect = Exception("External API error")
            
            with pytest.raises(ValueError) as exc_info:
                await delivery_service.lookup_delivery("TEST_INVOICE")
            
            assert "배송 조회 중 오류가 발생했습니다" in str(exc_info.value)