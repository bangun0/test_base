import pytest
from unittest.mock import Mock, AsyncMock, patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.config.database import Base
from app.services.return_service import ReturnService
from app.schemas.return_delivery import ReturnDeliveryCreate, ReturnDeliveryListCreate


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
def return_service(db_session):
    return ReturnService(db_session, "test_auth_token")


@pytest.fixture
def sample_return_data():
    return ReturnDeliveryCreate(
        original_invoice_number="INV1234567890",
        sender_name="반품 발송자",
        sender_phone="010-1234-5678",
        sender_zipcode="12345",
        sender_address1="서울시 강남구",
        sender_address2="테헤란로 123",
        receiver_name="반품 수령자",
        receiver_phone="010-9876-5432",
        receiver_zipcode="54321",
        receiver_address1="서울시 서초구",
        receiver_address2="강남대로 456",
        product_name="반품 상품",
        product_quantity=1,
        return_reason="상품 불량",
        return_memo="상품에 이상이 있습니다",
        return_date="2024-01-15"
    )


class TestReturnService:
    
    @pytest.mark.asyncio
    async def test_register_return_success(self, return_service, sample_return_data):
        mock_external_response = {
            "success": True,
            "return_invoice_number": "RET1234567890",
            "status": "REGISTERED"
        }
        
        with patch.object(return_service.client, 'register_return', new_callable=AsyncMock) as mock_register:
            mock_register.return_value = mock_external_response
            
            result = await return_service.register_return(sample_return_data)
            
            assert result is not None
            assert result.original_invoice_number == "INV1234567890"
            assert result.sender_name == "반품 발송자"
            assert result.receiver_name == "반품 수령자"
            assert result.product_name == "반품 상품"
            assert result.return_reason == "상품 불량"
            assert result.status == "REGISTERED"
            assert result.external_response == mock_external_response
            
            mock_register.assert_called_once_with(sample_return_data.model_dump(), "test_auth_token")

    @pytest.mark.asyncio
    async def test_register_return_list_success(self, return_service, sample_return_data):
        return_list = ReturnDeliveryListCreate(returns=[sample_return_data, sample_return_data])
        
        mock_external_response = {
            "success": True,
            "registered_count": 2
        }
        
        with patch.object(return_service.client, 'register_return_list', new_callable=AsyncMock) as mock_register:
            mock_register.return_value = mock_external_response
            
            results = await return_service.register_return_list(return_list)
            
            assert len(results) == 2
            for result in results:
                assert result.original_invoice_number == "INV1234567890"
                assert result.sender_name == "반품 발송자"
                assert result.external_response == mock_external_response
            
            mock_register.assert_called_once()

    @pytest.mark.asyncio
    async def test_lookup_return_success(self, return_service):
        # First create a return in the database
        return_data = {
            "original_invoice_number": "INV1234567890",
            "sender_name": "반품 발송자",
            "receiver_name": "반품 수령자",
            "product_name": "반품 상품",
            "return_reason": "상품 불량",
            "status": "IN_TRANSIT"
        }
        return_delivery = return_service.repository.create(return_data)
        
        result = await return_service.lookup_return(return_delivery.return_invoice_number)
        
        assert result is not None
        assert result.return_invoice_number == return_delivery.return_invoice_number
        assert result.original_invoice_number == "INV1234567890"
        assert result.status == "IN_TRANSIT"

    @pytest.mark.asyncio
    async def test_lookup_return_not_found(self, return_service):
        with pytest.raises(ValueError) as exc_info:
            await return_service.lookup_return("NONEXISTENT")
        
        assert "반품 정보를 찾을 수 없습니다" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_lookup_return_list_success(self, return_service):
        # Create multiple returns
        return_invoice_numbers = []
        for i in range(3):
            return_data = {
                "original_invoice_number": f"INV{i:010d}",
                "sender_name": f"반품 발송자{i}",
                "receiver_name": f"반품 수령자{i}",
                "product_name": f"반품 상품{i}",
                "return_reason": "상품 불량",
                "status": "REGISTERED"
            }
            return_delivery = return_service.repository.create(return_data)
            return_invoice_numbers.append(return_delivery.return_invoice_number)
        
        results = await return_service.lookup_return_list(return_invoice_numbers)
        
        assert len(results) == 3
        for i, result in enumerate(results):
            assert result.original_invoice_number == f"INV{i:010d}"
            assert result.status == "REGISTERED"

    @pytest.mark.asyncio
    async def test_lookup_return_list_with_errors(self, return_service):
        # Create one valid return and one invalid invoice number
        return_data = {
            "original_invoice_number": "INV1234567890",
            "sender_name": "반품 발송자",
            "receiver_name": "반품 수령자",
            "product_name": "반품 상품",
            "return_reason": "상품 불량",
            "status": "REGISTERED"
        }
        return_delivery = return_service.repository.create(return_data)
        
        invoice_numbers = [return_delivery.return_invoice_number, "NONEXISTENT"]
        results = await return_service.lookup_return_list(invoice_numbers)
        
        assert len(results) == 2
        assert results[0].status == "REGISTERED"
        assert results[1].status == "ERROR"
        assert "error" in results[1].return_info

    def test_get_return_by_invoice_success(self, return_service):
        return_data = {
            "original_invoice_number": "INV1234567890",
            "sender_name": "반품 발송자",
            "receiver_name": "반품 수령자",
            "product_name": "반품 상품",
            "return_reason": "상품 불량",
            "status": "REGISTERED"
        }
        return_delivery = return_service.repository.create(return_data)
        
        result = return_service.get_return_by_invoice(return_delivery.return_invoice_number)
        
        assert result is not None
        assert result.return_invoice_number == return_delivery.return_invoice_number
        assert result.original_invoice_number == "INV1234567890"
        assert result.sender_name == "반품 발송자"

    def test_get_return_by_invoice_not_found(self, return_service):
        result = return_service.get_return_by_invoice("NONEXISTENT")
        assert result is None

    def test_get_returns_by_original_invoice_success(self, return_service):
        original_invoice = "INV1234567890"
        
        # Create multiple returns for the same original invoice
        for i in range(3):
            return_data = {
                "original_invoice_number": original_invoice,
                "sender_name": f"반품 발송자{i}",
                "receiver_name": f"반품 수령자{i}",
                "product_name": f"반품 상품{i}",
                "return_reason": "상품 불량",
                "status": "REGISTERED"
            }
            return_service.repository.create(return_data)
        
        results = return_service.get_returns_by_original_invoice(original_invoice)
        
        assert len(results) == 3
        for result in results:
            assert result.original_invoice_number == original_invoice

    def test_get_returns_by_date_success(self, return_service):
        return_date = "2024-01-15"
        
        # Create multiple returns with the same date
        for i in range(3):
            return_data = {
                "original_invoice_number": f"INV{i:010d}",
                "sender_name": f"반품 발송자{i}",
                "receiver_name": f"반품 수령자{i}",
                "product_name": f"반품 상품{i}",
                "return_reason": "상품 불량",
                "return_date": return_date,
                "status": "REGISTERED"
            }
            return_service.repository.create(return_data)
        
        results = return_service.get_returns_by_date(return_date)
        
        assert len(results) == 3
        for result in results:
            assert result.return_date == return_date

    def test_update_return_status_success(self, return_service):
        return_data = {
            "original_invoice_number": "INV1234567890",
            "sender_name": "반품 발송자",
            "receiver_name": "반품 수령자",
            "product_name": "반품 상품",
            "return_reason": "상품 불량",
            "status": "IN_TRANSIT"
        }
        return_delivery = return_service.repository.create(return_data)
        
        result = return_service.update_return_status(
            return_delivery.return_invoice_number,
            "DELIVERED",
            location="반품 센터",
            memo="반품 완료"
        )
        
        assert result is not None
        assert result.status == "DELIVERED"
        
        # Check that tracking was added
        tracking_info = return_service.repository.get_tracking_by_return_invoice(
            return_delivery.return_invoice_number
        )
        assert len(tracking_info) == 1
        assert tracking_info[0].status == "DELIVERED"
        assert tracking_info[0].location == "반품 센터"

    def test_update_return_status_not_found(self, return_service):
        result = return_service.update_return_status("NONEXISTENT", "DELIVERED")
        assert result is None

    def test_delete_return_success(self, return_service):
        return_data = {
            "original_invoice_number": "INV1234567890",
            "sender_name": "반품 발송자",
            "receiver_name": "반품 수령자",
            "product_name": "반품 상품",
            "return_reason": "상품 불량",
            "status": "REGISTERED"
        }
        return_delivery = return_service.repository.create(return_data)
        
        result = return_service.delete_return(return_delivery.return_invoice_number)
        assert result is True
        
        # Verify the return was deleted
        deleted_return = return_service.get_return_by_invoice(return_delivery.return_invoice_number)
        assert deleted_return is None

    def test_delete_return_not_found(self, return_service):
        result = return_service.delete_return("NONEXISTENT")
        assert result is False

    @pytest.mark.asyncio
    async def test_register_return_external_api_error(self, return_service, sample_return_data):
        with patch.object(return_service.client, 'register_return', new_callable=AsyncMock) as mock_register:
            mock_register.side_effect = Exception("External API error")
            
            with pytest.raises(ValueError) as exc_info:
                await return_service.register_return(sample_return_data)
            
            assert "반품 등록 중 오류가 발생했습니다" in str(exc_info.value)

    def test_update_return_status_repository_error(self, return_service):
        # Create a return first
        return_data = {
            "original_invoice_number": "INV1234567890",
            "sender_name": "반품 발송자",
            "receiver_name": "반품 수령자",
            "product_name": "반품 상품",
            "return_reason": "상품 불량",
            "status": "REGISTERED"
        }
        return_delivery = return_service.repository.create(return_data)
        
        # Mock repository to raise an exception
        with patch.object(return_service.repository, 'update_status') as mock_update:
            mock_update.side_effect = Exception("Database error")
            
            with pytest.raises(ValueError) as exc_info:
                return_service.update_return_status(return_delivery.return_invoice_number, "DELIVERED")
            
            assert "반품 상태 업데이트 중 오류가 발생했습니다" in str(exc_info.value)