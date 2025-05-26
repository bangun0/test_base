from typing import List, Optional
from sqlalchemy.orm import Session
import logging

from app.repositories.return_repository import ReturnRepository
from app.schemas.return_delivery import (
    ReturnDeliveryCreate, ReturnDeliveryListCreate, ReturnDeliveryResponse,
    ReturnLookupResponse
)
from app.services.today_pickup_client import TodayPickupClient

logger = logging.getLogger(__name__)


class ReturnService:
    def __init__(self, db: Session, auth_token: str = None):
        self.repository = ReturnRepository(db)
        self.client = TodayPickupClient()
        self.auth_token = auth_token
    
    async def register_return(self, return_data: ReturnDeliveryCreate) -> ReturnDeliveryResponse:
        try:
            return_dict = return_data.model_dump()
            external_response = await self.client.register_return(return_dict, self.auth_token)
            
            return_dict["external_response"] = external_response
            return_delivery = self.repository.create(return_dict)
            
            return ReturnDeliveryResponse.model_validate(return_delivery)
        except Exception as e:
            logger.error(f"반품 등록 실패: {str(e)}")
            raise ValueError(f"반품 등록 중 오류가 발생했습니다: {str(e)}")
    
    async def register_return_list(self, returns_data: ReturnDeliveryListCreate) -> List[ReturnDeliveryResponse]:
        try:
            returns_list = [return_item.model_dump() for return_item in returns_data.returns]
            external_response = await self.client.register_return_list(returns_list, self.auth_token)
            
            returns_with_response = []
            for return_dict in returns_list:
                return_dict["external_response"] = external_response
                returns_with_response.append(return_dict)
            
            returns = self.repository.create_multiple(returns_with_response)
            
            return [ReturnDeliveryResponse.model_validate(return_item) for return_item in returns]
        except Exception as e:
            logger.error(f"반품 목록 등록 실패: {str(e)}")
            raise ValueError(f"반품 목록 등록 중 오류가 발생했습니다: {str(e)}")
    
    async def lookup_return(self, return_invoice_number: str) -> ReturnLookupResponse:
        try:
            local_return = self.repository.get_by_return_invoice_number(return_invoice_number)
            if not local_return:
                raise ValueError("반품 정보를 찾을 수 없습니다.")
            
            tracking_info = self.repository.get_tracking_by_return_invoice(return_invoice_number)
            tracking_list = [
                {
                    "status": track.status,
                    "message": track.status_message,
                    "date": track.tracking_date.isoformat() if track.tracking_date else None,
                    "location": track.location
                } for track in tracking_info
            ]
            
            return ReturnLookupResponse(
                return_invoice_number=return_invoice_number,
                original_invoice_number=local_return.original_invoice_number,
                status=local_return.status,
                tracking_info=tracking_list,
                return_info=local_return.external_response
            )
        except Exception as e:
            logger.error(f"반품 조회 실패: {str(e)}")
            raise ValueError(f"반품 조회 중 오류가 발생했습니다: {str(e)}")
    
    async def lookup_return_list(self, return_invoice_numbers: List[str]) -> List[ReturnLookupResponse]:
        try:
            results = []
            for return_invoice_number in return_invoice_numbers:
                try:
                    return_info = await self.lookup_return(return_invoice_number)
                    results.append(return_info)
                except Exception as e:
                    logger.warning(f"반품 조회 실패 - {return_invoice_number}: {str(e)}")
                    results.append(ReturnLookupResponse(
                        return_invoice_number=return_invoice_number,
                        original_invoice_number="",
                        status="ERROR",
                        tracking_info=[],
                        return_info={"error": str(e)}
                    ))
            
            return results
        except Exception as e:
            logger.error(f"반품 목록 조회 실패: {str(e)}")
            raise ValueError(f"반품 목록 조회 중 오류가 발생했습니다: {str(e)}")
    
    def get_return_by_invoice(self, return_invoice_number: str) -> Optional[ReturnDeliveryResponse]:
        return_delivery = self.repository.get_by_return_invoice_number(return_invoice_number)
        if not return_delivery:
            return None
        return ReturnDeliveryResponse.model_validate(return_delivery)
    
    def get_returns_by_original_invoice(self, original_invoice_number: str) -> List[ReturnDeliveryResponse]:
        returns = self.repository.get_by_original_invoice_number(original_invoice_number)
        return [ReturnDeliveryResponse.model_validate(return_item) for return_item in returns]
    
    def get_returns_by_date(self, return_date: str) -> List[ReturnDeliveryResponse]:
        returns = self.repository.get_returns_by_date(return_date)
        return [ReturnDeliveryResponse.model_validate(return_item) for return_item in returns]
    
    def update_return_status(self, return_invoice_number: str, status: str, **kwargs) -> Optional[ReturnDeliveryResponse]:
        try:
            return_delivery = self.repository.update_status(return_invoice_number, status, **kwargs)
            if not return_delivery:
                return None
            
            if kwargs.get("location") or kwargs.get("memo"):
                tracking_data = {
                    "return_invoice_number": return_invoice_number,
                    "status": status,
                    "status_message": kwargs.get("memo", f"상태 변경: {status}"),
                    "location": kwargs.get("location")
                }
                self.repository.add_tracking(tracking_data)
            
            return ReturnDeliveryResponse.model_validate(return_delivery)
        except Exception as e:
            logger.error(f"반품 상태 업데이트 실패: {str(e)}")
            raise ValueError(f"반품 상태 업데이트 중 오류가 발생했습니다: {str(e)}")
    
    def delete_return(self, return_invoice_number: str) -> bool:
        try:
            return self.repository.delete(return_invoice_number)
        except Exception as e:
            logger.error(f"반품 삭제 실패: {str(e)}")
            raise ValueError(f"반품 삭제 중 오류가 발생했습니다: {str(e)}")