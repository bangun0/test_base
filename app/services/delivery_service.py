from typing import List, Optional
from sqlalchemy.orm import Session
import logging

from app.repositories.delivery_repository import DeliveryRepository
from app.schemas.delivery import (
    DeliveryCreate, DeliveryListCreate, DeliveryResponse, 
    DeliveryLookupResponse, DeliveryCancelRequest, DeliveryReturnRequest,
    PossibleDeliveryRequest, PossibleDeliveryResponse, DeliveryFlexTransferRequest,
    DeliveryStatusUpdateRequest
)
from app.services.today_pickup_client import TodayPickupClient

logger = logging.getLogger(__name__)


class DeliveryService:
    def __init__(self, db: Session, auth_token: str = None):
        self.repository = DeliveryRepository(db)
        self.client = TodayPickupClient()
        self.auth_token = auth_token
    
    async def register_delivery(self, delivery_data: DeliveryCreate) -> DeliveryResponse:
        try:
            delivery_dict = delivery_data.model_dump()
            external_response = await self.client.register_delivery(delivery_dict, self.auth_token)
            
            delivery_dict["external_response"] = external_response
            delivery = self.repository.create(delivery_dict)
            
            return DeliveryResponse.model_validate(delivery)
        except Exception as e:
            logger.error(f"배송 등록 실패: {str(e)}")
            raise ValueError(f"배송 등록 중 오류가 발생했습니다: {str(e)}")
    
    async def register_delivery_list(self, deliveries_data: DeliveryListCreate) -> List[DeliveryResponse]:
        try:
            deliveries_list = [delivery.model_dump() for delivery in deliveries_data.deliveries]
            external_response = await self.client.register_delivery_list(deliveries_list, self.auth_token)
            
            deliveries_with_response = []
            for delivery_dict in deliveries_list:
                delivery_dict["external_response"] = external_response
                deliveries_with_response.append(delivery_dict)
            
            deliveries = self.repository.create_multiple(deliveries_with_response)
            
            return [DeliveryResponse.model_validate(delivery) for delivery in deliveries]
        except Exception as e:
            logger.error(f"배송 목록 등록 실패: {str(e)}")
            raise ValueError(f"배송 목록 등록 중 오류가 발생했습니다: {str(e)}")
    
    async def lookup_delivery(self, invoice_number: str) -> DeliveryLookupResponse:
        try:
            external_response = await self.client.lookup_delivery(invoice_number, self.auth_token)
            
            local_delivery = self.repository.get_by_invoice_number(invoice_number)
            if local_delivery:
                self.repository.update_status(
                    invoice_number, 
                    external_response.get("status", local_delivery.status),
                    external_response=external_response
                )
            
            tracking_info = self.repository.get_tracking_by_invoice(invoice_number)
            tracking_list = [
                {
                    "status": track.status,
                    "message": track.status_message,
                    "date": track.tracking_date.isoformat() if track.tracking_date else None,
                    "location": track.location
                } for track in tracking_info
            ]
            
            return DeliveryLookupResponse(
                invoice_number=invoice_number,
                status=external_response.get("status", "UNKNOWN"),
                tracking_info=tracking_list,
                delivery_info=external_response
            )
        except Exception as e:
            logger.error(f"배송 조회 실패: {str(e)}")
            raise ValueError(f"배송 조회 중 오류가 발생했습니다: {str(e)}")
    
    async def lookup_delivery_list(self, invoice_numbers: List[str]) -> List[DeliveryLookupResponse]:
        try:
            external_response = await self.client.lookup_delivery_list(invoice_numbers, self.auth_token)
            
            results = []
            for invoice_number in invoice_numbers:
                delivery_info = external_response.get(invoice_number, {})
                
                local_delivery = self.repository.get_by_invoice_number(invoice_number)
                if local_delivery:
                    self.repository.update_status(
                        invoice_number,
                        delivery_info.get("status", local_delivery.status),
                        external_response=delivery_info
                    )
                
                tracking_info = self.repository.get_tracking_by_invoice(invoice_number)
                tracking_list = [
                    {
                        "status": track.status,
                        "message": track.status_message,
                        "date": track.tracking_date.isoformat() if track.tracking_date else None,
                        "location": track.location
                    } for track in tracking_info
                ]
                
                results.append(DeliveryLookupResponse(
                    invoice_number=invoice_number,
                    status=delivery_info.get("status", "UNKNOWN"),
                    tracking_info=tracking_list,
                    delivery_info=delivery_info
                ))
            
            return results
        except Exception as e:
            logger.error(f"배송 목록 조회 실패: {str(e)}")
            raise ValueError(f"배송 목록 조회 중 오류가 발생했습니다: {str(e)}")
    
    async def check_possible_delivery(self, request: PossibleDeliveryRequest) -> PossibleDeliveryResponse:
        try:
            external_response = await self.client.check_possible_delivery(
                request.zipcode, request.address, self.auth_token
            )
            
            return PossibleDeliveryResponse(
                is_possible=external_response.get("possible", False),
                estimated_delivery_date=external_response.get("estimated_date"),
                delivery_fee=external_response.get("fee")
            )
        except Exception as e:
            logger.error(f"배송 가능 여부 확인 실패: {str(e)}")
            raise ValueError(f"배송 가능 여부 확인 중 오류가 발생했습니다: {str(e)}")
    
    async def cancel_delivery(self, request: DeliveryCancelRequest) -> bool:
        try:
            cancel_data = request.model_dump()
            external_response = await self.client.cancel_delivery(cancel_data, self.auth_token)
            
            delivery = self.repository.update_status(
                request.invoice_number,
                "CANCELLED",
                external_response=external_response
            )
            
            return delivery is not None
        except Exception as e:
            logger.error(f"배송 취소 실패: {str(e)}")
            raise ValueError(f"배송 취소 중 오류가 발생했습니다: {str(e)}")
    
    async def request_return_delivery(self, request: DeliveryReturnRequest) -> bool:
        try:
            return_data = request.model_dump()
            external_response = await self.client.request_return_delivery(return_data, self.auth_token)
            
            delivery = self.repository.update_status(
                request.invoice_number,
                "RETURN_REQUESTED",
                external_response=external_response
            )
            
            return delivery is not None
        except Exception as e:
            logger.error(f"반품 요청 실패: {str(e)}")
            raise ValueError(f"반품 요청 중 오류가 발생했습니다: {str(e)}")
    
    async def transfer_to_flex(self, request: DeliveryFlexTransferRequest) -> bool:
        try:
            transfer_data = request.model_dump()
            external_response = await self.client.agency_transfer_to_flex(transfer_data, self.auth_token)
            
            delivery = self.repository.transfer_to_flex(request.invoice_number)
            if delivery:
                delivery.external_response = external_response
                
            return delivery is not None
        except Exception as e:
            logger.error(f"플렉스 이관 실패: {str(e)}")
            raise ValueError(f"플렉스 이관 중 오류가 발생했습니다: {str(e)}")
    
    async def update_delivery_status(self, request: DeliveryStatusUpdateRequest) -> bool:
        try:
            status_data = request.model_dump()
            external_response = await self.client.agency_update_delivery_state(status_data, self.auth_token)
            
            if request.location or request.memo:
                tracking_data = {
                    "invoice_number": request.invoice_number,
                    "status": request.status,
                    "status_message": request.memo or f"상태 변경: {request.status}",
                    "location": request.location
                }
                self.repository.add_tracking(tracking_data)
            
            delivery = self.repository.update_status(
                request.invoice_number,
                request.status,
                external_response=external_response
            )
            
            return delivery is not None
        except Exception as e:
            logger.error(f"배송 상태 업데이트 실패: {str(e)}")
            raise ValueError(f"배송 상태 업데이트 중 오류가 발생했습니다: {str(e)}")
    
    def get_delivery_by_invoice(self, invoice_number: str) -> Optional[DeliveryResponse]:
        delivery = self.repository.get_by_invoice_number(invoice_number)
        if not delivery:
            return None
        return DeliveryResponse.model_validate(delivery)
    
    def get_deliveries_by_date(self, delivery_date: str) -> List[DeliveryResponse]:
        deliveries = self.repository.get_deliveries_by_date(delivery_date)
        return [DeliveryResponse.model_validate(delivery) for delivery in deliveries]