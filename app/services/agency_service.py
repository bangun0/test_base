from typing import List, Optional
from sqlalchemy.orm import Session
import logging
from datetime import datetime

from app.repositories.agency_repository import AgencyRepository
from app.schemas.agency import (
    AgencyCreate, AgencyResponse, AuthTokenRequest, AuthTokenResponse,
    TokenGenerateRequest, TokenGenerateResponse, DeliveryAssignmentRequest,
    DeliveryCompletionRequest, DeliveryFlexTransferRequest, DeliveryListRequest,
    DeliveryLookupRequest, PostalCodeSaveRequest, PostalCodeResponse,
    DeliveryAssignmentResponse
)
from app.services.today_pickup_client import TodayPickupClient

logger = logging.getLogger(__name__)


class AgencyService:
    def __init__(self, db: Session, auth_token: str = None):
        self.repository = AgencyRepository(db)
        self.client = TodayPickupClient()
        self.auth_token = auth_token
    
    def create_agency(self, agency_data: AgencyCreate) -> AgencyResponse:
        try:
            agency_dict = agency_data.model_dump()
            agency = self.repository.create_agency(agency_dict)
            return AgencyResponse.model_validate(agency)
        except Exception as e:
            logger.error(f"에이전시 생성 실패: {str(e)}")
            raise ValueError(f"에이전시 생성 중 오류가 발생했습니다: {str(e)}")
    
    async def validate_token(self, request: AuthTokenRequest) -> AuthTokenResponse:
        try:
            auth_data = request.model_dump()
            external_response = await self.client.agency_auth_validate(auth_data)
            
            agency = self.repository.get_agency_by_id(request.agency_id)
            if not agency:
                return AuthTokenResponse(is_valid=False)
            
            agency_info = {
                "agency_id": agency.agency_id,
                "agency_name": agency.agency_name,
                "is_active": agency.is_active
            }
            
            return AuthTokenResponse(
                is_valid=external_response.get("valid", False),
                agency_info=agency_info
            )
        except Exception as e:
            logger.error(f"토큰 검증 실패: {str(e)}")
            return AuthTokenResponse(is_valid=False)
    
    async def generate_token(self, request: TokenGenerateRequest) -> TokenGenerateResponse:
        try:
            token_data = request.model_dump()
            external_response = await self.client.agency_generate_token(token_data)
            
            token = external_response.get("token")
            if token:
                self.repository.update_agency_token(request.agency_id, token)
            
            return TokenGenerateResponse(
                token=token,
                expires_at=external_response.get("expires_at")
            )
        except Exception as e:
            logger.error(f"토큰 생성 실패: {str(e)}")
            raise ValueError(f"토큰 생성 중 오류가 발생했습니다: {str(e)}")
    
    async def complete_delivery(self, request: DeliveryCompletionRequest) -> bool:
        try:
            completion_data = request.model_dump()
            external_response = await self.client.agency_complete_delivery(completion_data, self.auth_token)
            
            completion_data["external_response"] = external_response
            if request.completion_date:
                completion_data["completion_date"] = datetime.fromisoformat(request.completion_date)
            
            assignment = self.repository.complete_delivery_assignment(
                request.invoice_number, completion_data
            )
            
            return assignment is not None
        except Exception as e:
            logger.error(f"배송 완료 처리 실패: {str(e)}")
            raise ValueError(f"배송 완료 처리 중 오류가 발생했습니다: {str(e)}")
    
    async def transfer_to_flex(self, request: DeliveryFlexTransferRequest) -> bool:
        try:
            transfer_data = request.model_dump()
            external_response = await self.client.agency_transfer_to_flex(transfer_data, self.auth_token)
            
            assignment = self.repository.update_assignment_status(
                request.invoice_number,
                "FLEX_TRANSFERRED",
                external_response=external_response
            )
            
            return assignment is not None
        except Exception as e:
            logger.error(f"플렉스 이관 실패: {str(e)}")
            raise ValueError(f"플렉스 이관 중 오류가 발생했습니다: {str(e)}")
    
    async def transfer_list_to_flex(self, requests: List[DeliveryFlexTransferRequest]) -> List[bool]:
        try:
            transfers_data = [req.model_dump() for req in requests]
            external_response = await self.client.agency_transfer_list_to_flex(transfers_data, self.auth_token)
            
            results = []
            for request in requests:
                assignment = self.repository.update_assignment_status(
                    request.invoice_number,
                    "FLEX_TRANSFERRED",
                    external_response=external_response
                )
                results.append(assignment is not None)
            
            return results
        except Exception as e:
            logger.error(f"플렉스 목록 이관 실패: {str(e)}")
            raise ValueError(f"플렉스 목록 이관 중 오류가 발생했습니다: {str(e)}")
    
    async def get_delivery_list(self, request: DeliveryListRequest) -> List[DeliveryAssignmentResponse]:
        try:
            request_data = {"agency_id": request.agency_id}
            external_response = await self.client.agency_get_delivery_list(
                request.delivery_date, request_data, self.auth_token
            )
            
            local_assignments = self.repository.get_assignments_by_agency_and_date(
                request.agency_id, request.delivery_date
            )
            
            return [DeliveryAssignmentResponse.model_validate(assignment) for assignment in local_assignments]
        except Exception as e:
            logger.error(f"배송 목록 조회 실패: {str(e)}")
            raise ValueError(f"배송 목록 조회 중 오류가 발생했습니다: {str(e)}")
    
    async def lookup_deliveries(self, request: DeliveryLookupRequest) -> List[dict]:
        try:
            lookup_data = request.model_dump()
            external_response = await self.client.agency_lookup_deliveries(lookup_data, self.auth_token)
            
            results = []
            for invoice_number in request.invoice_numbers:
                assignment = self.repository.get_assignment_by_invoice(invoice_number)
                if assignment:
                    assignment_data = DeliveryAssignmentResponse.model_validate(assignment).model_dump()
                    assignment_data.update(external_response.get(invoice_number, {}))
                    results.append(assignment_data)
                else:
                    results.append({
                        "invoice_number": invoice_number,
                        "error": "배송 할당 정보를 찾을 수 없습니다."
                    })
            
            return results
        except Exception as e:
            logger.error(f"배송 조회 실패: {str(e)}")
            raise ValueError(f"배송 조회 중 오류가 발생했습니다: {str(e)}")
    
    async def save_postal_codes(self, request: PostalCodeSaveRequest) -> List[PostalCodeResponse]:
        try:
            postal_data = request.model_dump()
            external_response = await self.client.agency_save_postal_codes(postal_data, self.auth_token)
            
            postal_codes_data = []
            for postal_code in request.postal_codes:
                postal_dict = postal_code.model_dump()
                postal_dict["agency_id"] = request.agency_id
                postal_codes_data.append(postal_dict)
            
            postal_codes = self.repository.create_postal_codes_bulk(postal_codes_data)
            
            return [PostalCodeResponse.model_validate(pc) for pc in postal_codes]
        except Exception as e:
            logger.error(f"우편번호 저장 실패: {str(e)}")
            raise ValueError(f"우편번호 저장 중 오류가 발생했습니다: {str(e)}")
    
    def get_agency_by_id(self, agency_id: str) -> Optional[AgencyResponse]:
        agency = self.repository.get_agency_by_id(agency_id)
        if not agency:
            return None
        return AgencyResponse.model_validate(agency)
    
    def get_postal_codes_by_agency(self, agency_id: str) -> List[PostalCodeResponse]:
        postal_codes = self.repository.get_postal_codes_by_agency(agency_id)
        return [PostalCodeResponse.model_validate(pc) for pc in postal_codes]
    
    def check_postal_code_deliverable(self, agency_id: str, postal_code: str) -> bool:
        postal_info = self.repository.check_postal_code_deliverable(agency_id, postal_code)
        return postal_info is not None and postal_info.is_deliverable
    
    def create_delivery_assignment(self, request: DeliveryAssignmentRequest) -> DeliveryAssignmentResponse:
        try:
            assignment_data = request.model_dump()
            assignment = self.repository.create_delivery_assignment(assignment_data)
            return DeliveryAssignmentResponse.model_validate(assignment)
        except Exception as e:
            logger.error(f"배송 할당 생성 실패: {str(e)}")
            raise ValueError(f"배송 할당 생성 중 오류가 발생했습니다: {str(e)}")
    
    def deactivate_agency(self, agency_id: str) -> bool:
        try:
            return self.repository.deactivate_agency(agency_id)
        except Exception as e:
            logger.error(f"에이전시 비활성화 실패: {str(e)}")
            raise ValueError(f"에이전시 비활성화 중 오류가 발생했습니다: {str(e)}")