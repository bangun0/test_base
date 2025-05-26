import pytest
from unittest.mock import Mock, AsyncMock, patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from datetime import datetime

from app.config.database import Base
from app.services.agency_service import AgencyService
from app.schemas.agency import (
    AgencyCreate, AuthTokenRequest, TokenGenerateRequest,
    DeliveryAssignmentRequest, DeliveryCompletionRequest, 
    DeliveryFlexTransferRequest, DeliveryListRequest,
    DeliveryLookupRequest, PostalCodeSaveRequest, PostalCodeBase
)


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
def agency_service(db_session):
    return AgencyService(db_session, "test_auth_token")


@pytest.fixture
def sample_agency_data():
    return AgencyCreate(
        agency_id="TEST_AGENCY_001",
        agency_name="테스트 에이전시",
        agency_token="test_token_12345"
    )


class TestAgencyService:
    
    def test_create_agency_success(self, agency_service, sample_agency_data):
        result = agency_service.create_agency(sample_agency_data)
        
        assert result is not None
        assert result.agency_id == "TEST_AGENCY_001"
        assert result.agency_name == "테스트 에이전시"
        assert result.is_active is True

    def test_create_agency_duplicate_id(self, agency_service, sample_agency_data):
        # Create first agency
        agency_service.create_agency(sample_agency_data)
        
        # Try to create another agency with the same ID
        with pytest.raises(ValueError) as exc_info:
            agency_service.create_agency(sample_agency_data)
        
        assert "에이전시 생성 중 오류가 발생했습니다" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_validate_token_success(self, agency_service, sample_agency_data):
        # Create agency first
        agency_service.create_agency(sample_agency_data)
        
        request = AuthTokenRequest(
            agency_id="TEST_AGENCY_001",
            token="test_token_12345"
        )
        
        mock_external_response = {
            "valid": True
        }
        
        with patch.object(agency_service.client, 'agency_auth_validate', new_callable=AsyncMock) as mock_validate:
            mock_validate.return_value = mock_external_response
            
            result = await agency_service.validate_token(request)
            
            assert result.is_valid is True
            assert result.agency_info["agency_id"] == "TEST_AGENCY_001"
            assert result.agency_info["agency_name"] == "테스트 에이전시"
            
            mock_validate.assert_called_once_with(request.model_dump())

    @pytest.mark.asyncio
    async def test_validate_token_agency_not_found(self, agency_service):
        request = AuthTokenRequest(
            agency_id="NONEXISTENT_AGENCY",
            token="test_token"
        )
        
        mock_external_response = {
            "valid": True
        }
        
        with patch.object(agency_service.client, 'agency_auth_validate', new_callable=AsyncMock) as mock_validate:
            mock_validate.return_value = mock_external_response
            
            result = await agency_service.validate_token(request)
            
            assert result.is_valid is False
            assert result.agency_info is None

    @pytest.mark.asyncio
    async def test_generate_token_success(self, agency_service, sample_agency_data):
        # Create agency first
        agency_service.create_agency(sample_agency_data)
        
        request = TokenGenerateRequest(
            agency_id="TEST_AGENCY_001",
            credentials={"username": "test", "password": "password"}
        )
        
        mock_external_response = {
            "token": "new_token_12345",
            "expires_at": "2024-12-31T23:59:59"
        }
        
        with patch.object(agency_service.client, 'agency_generate_token', new_callable=AsyncMock) as mock_generate:
            mock_generate.return_value = mock_external_response
            
            result = await agency_service.generate_token(request)
            
            assert result.token == "new_token_12345"
            assert result.expires_at == "2024-12-31T23:59:59"
            
            # Check that the agency token was updated
            agency = agency_service.get_agency_by_id("TEST_AGENCY_001")
            # Note: In the actual implementation, you might want to verify the token was updated
            
            mock_generate.assert_called_once_with(request.model_dump())

    @pytest.mark.asyncio
    async def test_complete_delivery_success(self, agency_service):
        # Create delivery assignment first
        assignment_request = DeliveryAssignmentRequest(
            invoice_number="INV1234567890",
            delivery_date="2024-01-15",
            agency_id="TEST_AGENCY_001"
        )
        agency_service.create_delivery_assignment(assignment_request)
        
        completion_request = DeliveryCompletionRequest(
            invoice_number="INV1234567890",
            completion_status="DELIVERED",
            completion_date="2024-01-15T14:30:00",
            delivery_memo="성공적으로 배송 완료"
        )
        
        mock_external_response = {
            "success": True,
            "completed": True
        }
        
        with patch.object(agency_service.client, 'agency_complete_delivery', new_callable=AsyncMock) as mock_complete:
            mock_complete.return_value = mock_external_response
            
            result = await agency_service.complete_delivery(completion_request)
            
            assert result is True
            
            mock_complete.assert_called_once()

    @pytest.mark.asyncio
    async def test_transfer_to_flex_success(self, agency_service):
        # Create delivery assignment first
        assignment_request = DeliveryAssignmentRequest(
            invoice_number="INV1234567890",
            delivery_date="2024-01-15",
            agency_id="TEST_AGENCY_001"
        )
        agency_service.create_delivery_assignment(assignment_request)
        
        transfer_request = DeliveryFlexTransferRequest(
            invoice_number="INV1234567890",
            reason="배송 불가 지역"
        )
        
        mock_external_response = {
            "success": True,
            "transferred": True
        }
        
        with patch.object(agency_service.client, 'agency_transfer_to_flex', new_callable=AsyncMock) as mock_transfer:
            mock_transfer.return_value = mock_external_response
            
            result = await agency_service.transfer_to_flex(transfer_request)
            
            assert result is True
            
            mock_transfer.assert_called_once_with(transfer_request.model_dump(), "test_auth_token")

    @pytest.mark.asyncio
    async def test_transfer_list_to_flex_success(self, agency_service):
        # Create multiple delivery assignments
        invoice_numbers = ["INV001", "INV002", "INV003"]
        for invoice_number in invoice_numbers:
            assignment_request = DeliveryAssignmentRequest(
                invoice_number=invoice_number,
                delivery_date="2024-01-15",
                agency_id="TEST_AGENCY_001"
            )
            agency_service.create_delivery_assignment(assignment_request)
        
        transfer_requests = [
            DeliveryFlexTransferRequest(invoice_number=inv, reason="배송 불가")
            for inv in invoice_numbers
        ]
        
        mock_external_response = {
            "success": True,
            "transferred_count": 3
        }
        
        with patch.object(agency_service.client, 'agency_transfer_list_to_flex', new_callable=AsyncMock) as mock_transfer:
            mock_transfer.return_value = mock_external_response
            
            results = await agency_service.transfer_list_to_flex(transfer_requests)
            
            assert len(results) == 3
            assert all(result is True for result in results)
            
            mock_transfer.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_delivery_list_success(self, agency_service, sample_agency_data):
        # Create agency first
        agency_service.create_agency(sample_agency_data)
        
        # Create delivery assignments
        for i in range(3):
            assignment_request = DeliveryAssignmentRequest(
                invoice_number=f"INV{i:010d}",
                delivery_date="2024-01-15",
                agency_id="TEST_AGENCY_001"
            )
            agency_service.create_delivery_assignment(assignment_request)
        
        request = DeliveryListRequest(
            delivery_date="2024-01-15",
            agency_id="TEST_AGENCY_001"
        )
        
        mock_external_response = {
            "deliveries": [
                {"invoice_number": "INV0000000000", "status": "ASSIGNED"},
                {"invoice_number": "INV0000000001", "status": "ASSIGNED"},
                {"invoice_number": "INV0000000002", "status": "ASSIGNED"}
            ]
        }
        
        with patch.object(agency_service.client, 'agency_get_delivery_list', new_callable=AsyncMock) as mock_get_list:
            mock_get_list.return_value = mock_external_response
            
            results = await agency_service.get_delivery_list(request)
            
            assert len(results) == 3
            for result in results:
                assert result.delivery_date == "2024-01-15"
                assert result.agency_id == "TEST_AGENCY_001"
            
            mock_get_list.assert_called_once()

    @pytest.mark.asyncio
    async def test_lookup_deliveries_success(self, agency_service):
        # Create delivery assignments
        invoice_numbers = ["INV001", "INV002"]
        for invoice_number in invoice_numbers:
            assignment_request = DeliveryAssignmentRequest(
                invoice_number=invoice_number,
                delivery_date="2024-01-15",
                agency_id="TEST_AGENCY_001"
            )
            agency_service.create_delivery_assignment(assignment_request)
        
        request = DeliveryLookupRequest(invoice_numbers=invoice_numbers)
        
        mock_external_response = {
            "INV001": {"status": "IN_TRANSIT", "location": "배송 센터"},
            "INV002": {"status": "DELIVERED", "location": "수령 완료"}
        }
        
        with patch.object(agency_service.client, 'agency_lookup_deliveries', new_callable=AsyncMock) as mock_lookup:
            mock_lookup.return_value = mock_external_response
            
            results = await agency_service.lookup_deliveries(request)
            
            assert len(results) == 2
            assert results[0]["invoice_number"] == "INV001"
            assert results[1]["invoice_number"] == "INV002"
            
            mock_lookup.assert_called_once()

    @pytest.mark.asyncio
    async def test_save_postal_codes_success(self, agency_service, sample_agency_data):
        # Create agency first
        agency_service.create_agency(sample_agency_data)
        
        postal_codes = [
            PostalCodeBase(postal_code="12345", region_name="강남구", is_deliverable=True),
            PostalCodeBase(postal_code="54321", region_name="서초구", is_deliverable=True),
            PostalCodeBase(postal_code="99999", region_name="제주도", is_deliverable=False)
        ]
        
        request = PostalCodeSaveRequest(
            agency_id="TEST_AGENCY_001",
            postal_codes=postal_codes
        )
        
        mock_external_response = {
            "success": True,
            "saved_count": 3
        }
        
        with patch.object(agency_service.client, 'agency_save_postal_codes', new_callable=AsyncMock) as mock_save:
            mock_save.return_value = mock_external_response
            
            results = await agency_service.save_postal_codes(request)
            
            assert len(results) == 3
            for result in results:
                assert result.agency_id == "TEST_AGENCY_001"
            
            # Verify postal codes can be retrieved
            saved_codes = agency_service.get_postal_codes_by_agency("TEST_AGENCY_001")
            assert len(saved_codes) == 3
            
            mock_save.assert_called_once()

    def test_get_agency_by_id_success(self, agency_service, sample_agency_data):
        # Create agency first
        agency_service.create_agency(sample_agency_data)
        
        result = agency_service.get_agency_by_id("TEST_AGENCY_001")
        
        assert result is not None
        assert result.agency_id == "TEST_AGENCY_001"
        assert result.agency_name == "테스트 에이전시"

    def test_get_agency_by_id_not_found(self, agency_service):
        result = agency_service.get_agency_by_id("NONEXISTENT")
        assert result is None

    def test_check_postal_code_deliverable_success(self, agency_service, sample_agency_data):
        # Create agency and postal codes
        agency_service.create_agency(sample_agency_data)
        
        postal_codes = [
            PostalCodeBase(postal_code="12345", region_name="강남구", is_deliverable=True),
            PostalCodeBase(postal_code="99999", region_name="제주도", is_deliverable=False)
        ]
        
        request = PostalCodeSaveRequest(
            agency_id="TEST_AGENCY_001",
            postal_codes=postal_codes
        )
        
        # Mock the external API call
        mock_external_response = {"success": True, "saved_count": 2}
        with patch.object(agency_service.client, 'agency_save_postal_codes', new_callable=AsyncMock) as mock_save:
            mock_save.return_value = mock_external_response
            # Need to use asyncio.run for the async method
            import asyncio
            asyncio.run(agency_service.save_postal_codes(request))
        
        # Test deliverable postal code
        result = agency_service.check_postal_code_deliverable("TEST_AGENCY_001", "12345")
        assert result is True
        
        # Test non-deliverable postal code
        result = agency_service.check_postal_code_deliverable("TEST_AGENCY_001", "99999")
        assert result is False
        
        # Test non-existent postal code
        result = agency_service.check_postal_code_deliverable("TEST_AGENCY_001", "00000")
        assert result is False

    def test_create_delivery_assignment_success(self, agency_service):
        request = DeliveryAssignmentRequest(
            invoice_number="INV1234567890",
            delivery_date="2024-01-15",
            agency_id="TEST_AGENCY_001"
        )
        
        result = agency_service.create_delivery_assignment(request)
        
        assert result is not None
        assert result.invoice_number == "INV1234567890"
        assert result.delivery_date == "2024-01-15"
        assert result.agency_id == "TEST_AGENCY_001"
        assert result.assignment_status == "ASSIGNED"

    def test_deactivate_agency_success(self, agency_service, sample_agency_data):
        # Create agency first
        agency_service.create_agency(sample_agency_data)
        
        result = agency_service.deactivate_agency("TEST_AGENCY_001")
        assert result is True
        
        # Verify agency was deactivated (note: this might require additional implementation)

    def test_deactivate_agency_not_found(self, agency_service):
        result = agency_service.deactivate_agency("NONEXISTENT")
        assert result is False

    @pytest.mark.asyncio
    async def test_validate_token_external_api_error(self, agency_service):
        request = AuthTokenRequest(
            agency_id="TEST_AGENCY_001",
            token="test_token"
        )
        
        with patch.object(agency_service.client, 'agency_auth_validate', new_callable=AsyncMock) as mock_validate:
            mock_validate.side_effect = Exception("External API error")
            
            result = await agency_service.validate_token(request)
            assert result.is_valid is False

    @pytest.mark.asyncio
    async def test_generate_token_external_api_error(self, agency_service):
        request = TokenGenerateRequest(
            agency_id="TEST_AGENCY_001",
            credentials={"username": "test", "password": "password"}
        )
        
        with patch.object(agency_service.client, 'agency_generate_token', new_callable=AsyncMock) as mock_generate:
            mock_generate.side_effect = Exception("External API error")
            
            with pytest.raises(ValueError) as exc_info:
                await agency_service.generate_token(request)
            
            assert "토큰 생성 중 오류가 발생했습니다" in str(exc_info.value)