from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import List, Optional

from app.config.database import get_db
from app.services.delivery_service import DeliveryService
from app.schemas.delivery import (
    DeliveryCreate, DeliveryListCreate, DeliveryResponse,
    DeliveryLookupResponse, DeliveryCancelRequest, DeliveryReturnRequest,
    PossibleDeliveryRequest, PossibleDeliveryResponse, DeliveryFlexTransferRequest,
    DeliveryStatusUpdateRequest
)


class TodayPickupDeliveryController:
    def __init__(self):
        self.router = APIRouter(
            prefix="/api/mall",
            tags=["delivery"]
        )
        self._register_routes()
    
    def _register_routes(self):
        self.router.post("/deliveryRegister", response_model=DeliveryResponse)(self.register_delivery)
        self.router.post("/deliveryListRegister", response_model=List[DeliveryResponse])(self.register_delivery_list)
        self.router.get("/delivery/{invoice_number}", response_model=DeliveryLookupResponse)(self.lookup_delivery)
        self.router.get("/deliveryList/{invoice_number_list}", response_model=List[DeliveryLookupResponse])(self.lookup_delivery_list)
        self.router.get("/possibleDelivery", response_model=PossibleDeliveryResponse)(self.check_possible_delivery)
        self.router.post("/cancelDelivery")(self.cancel_delivery)
        self.router.post("/returnDelivery")(self.request_return_delivery)
        
        self.router.get("/deliveries", response_model=List[DeliveryResponse])(self.get_deliveries_by_date)
        self.router.get("/deliveries/{invoice_number}", response_model=DeliveryResponse)(self.get_delivery)
        self.router.put("/deliveries/{invoice_number}/status")(self.update_delivery_status)
        self.router.put("/deliveries/{invoice_number}/flex")(self.transfer_to_flex)

    def _get_auth_token(self, authorization: Optional[str] = Header(None)) -> str:
        if not authorization:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization 헤더가 필요합니다."
            )
        
        if not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Bearer 토큰이 필요합니다."
            )
        
        return authorization.replace("Bearer ", "")

    async def register_delivery(
        self,
        delivery_data: DeliveryCreate,
        db: Session = Depends(get_db),
        authorization: str = Depends(_get_auth_token)
    ):
        service = DeliveryService(db, authorization)
        try:
            return await service.register_delivery(delivery_data)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

    async def register_delivery_list(
        self,
        deliveries_data: DeliveryListCreate,
        db: Session = Depends(get_db),
        authorization: str = Depends(_get_auth_token)
    ):
        service = DeliveryService(db, authorization)
        try:
            return await service.register_delivery_list(deliveries_data)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

    async def lookup_delivery(
        self,
        invoice_number: str,
        db: Session = Depends(get_db),
        authorization: str = Depends(_get_auth_token)
    ):
        service = DeliveryService(db, authorization)
        try:
            return await service.lookup_delivery(invoice_number)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

    async def lookup_delivery_list(
        self,
        invoice_number_list: str,
        db: Session = Depends(get_db),
        authorization: str = Depends(_get_auth_token)
    ):
        service = DeliveryService(db, authorization)
        try:
            invoice_numbers = invoice_number_list.split(",")
            return await service.lookup_delivery_list(invoice_numbers)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

    async def check_possible_delivery(
        self,
        zipcode: str,
        address: str,
        db: Session = Depends(get_db),
        authorization: str = Depends(_get_auth_token)
    ):
        service = DeliveryService(db, authorization)
        try:
            request = PossibleDeliveryRequest(zipcode=zipcode, address=address)
            return await service.check_possible_delivery(request)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

    async def cancel_delivery(
        self,
        request: DeliveryCancelRequest,
        db: Session = Depends(get_db),
        authorization: str = Depends(_get_auth_token)
    ):
        service = DeliveryService(db, authorization)
        try:
            result = await service.cancel_delivery(request)
            if not result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="배송 정보를 찾을 수 없습니다."
                )
            return {"message": "배송이 취소되었습니다.", "success": True}
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

    async def request_return_delivery(
        self,
        request: DeliveryReturnRequest,
        db: Session = Depends(get_db),
        authorization: str = Depends(_get_auth_token)
    ):
        service = DeliveryService(db, authorization)
        try:
            result = await service.request_return_delivery(request)
            if not result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="배송 정보를 찾을 수 없습니다."
                )
            return {"message": "반품이 요청되었습니다.", "success": True}
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

    async def get_deliveries_by_date(
        self,
        delivery_date: str,
        db: Session = Depends(get_db)
    ):
        service = DeliveryService(db)
        try:
            return service.get_deliveries_by_date(delivery_date)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

    async def get_delivery(
        self,
        invoice_number: str,
        db: Session = Depends(get_db)
    ):
        service = DeliveryService(db)
        delivery = service.get_delivery_by_invoice(invoice_number)
        if not delivery:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="배송 정보를 찾을 수 없습니다."
            )
        return delivery

    async def update_delivery_status(
        self,
        invoice_number: str,
        request: DeliveryStatusUpdateRequest,
        db: Session = Depends(get_db),
        authorization: str = Depends(_get_auth_token)
    ):
        service = DeliveryService(db, authorization)
        try:
            request.invoice_number = invoice_number
            result = await service.update_delivery_status(request)
            if not result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="배송 정보를 찾을 수 없습니다."
                )
            return {"message": "배송 상태가 업데이트되었습니다.", "success": True}
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

    async def transfer_to_flex(
        self,
        invoice_number: str,
        request: DeliveryFlexTransferRequest,
        db: Session = Depends(get_db),
        authorization: str = Depends(_get_auth_token)
    ):
        service = DeliveryService(db, authorization)
        try:
            request.invoice_number = invoice_number
            result = await service.transfer_to_flex(request)
            if not result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="배송 정보를 찾을 수 없습니다."
                )
            return {"message": "플렉스로 이관되었습니다.", "success": True}
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )