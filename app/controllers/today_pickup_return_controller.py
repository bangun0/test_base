from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import List, Optional

from app.config.database import get_db
from app.services.return_service import ReturnService
from app.schemas.return_delivery import (
    ReturnDeliveryCreate, ReturnDeliveryListCreate, ReturnDeliveryResponse,
    ReturnLookupResponse, ReturnListLookupRequest
)


class TodayPickupReturnController:
    def __init__(self):
        self.router = APIRouter(
            prefix="/api/mall",
            tags=["returns"]
        )
        self._register_routes()
    
    def _register_routes(self):
        self.router.post("/returnRegister", response_model=ReturnDeliveryResponse)(self.register_return)
        self.router.post("/returnListRegister", response_model=List[ReturnDeliveryResponse])(self.register_return_list)
        
        self.router.get("/returns", response_model=List[ReturnDeliveryResponse])(self.get_returns_by_date)
        self.router.get("/returns/{return_invoice_number}", response_model=ReturnDeliveryResponse)(self.get_return)
        self.router.get("/returns/lookup/{return_invoice_number}", response_model=ReturnLookupResponse)(self.lookup_return)
        self.router.post("/returns/lookup", response_model=List[ReturnLookupResponse])(self.lookup_return_list)
        self.router.get("/returns/original/{original_invoice_number}", response_model=List[ReturnDeliveryResponse])(self.get_returns_by_original_invoice)
        self.router.put("/returns/{return_invoice_number}/status")(self.update_return_status)
        self.router.delete("/returns/{return_invoice_number}")(self.delete_return)

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

    async def register_return(
        self,
        return_data: ReturnDeliveryCreate,
        db: Session = Depends(get_db),
        authorization: str = Depends(_get_auth_token)
    ):
        service = ReturnService(db, authorization)
        try:
            return await service.register_return(return_data)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

    async def register_return_list(
        self,
        returns_data: ReturnDeliveryListCreate,
        db: Session = Depends(get_db),
        authorization: str = Depends(_get_auth_token)
    ):
        service = ReturnService(db, authorization)
        try:
            return await service.register_return_list(returns_data)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

    async def lookup_return(
        self,
        return_invoice_number: str,
        db: Session = Depends(get_db)
    ):
        service = ReturnService(db)
        try:
            return await service.lookup_return(return_invoice_number)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

    async def lookup_return_list(
        self,
        request: ReturnListLookupRequest,
        db: Session = Depends(get_db)
    ):
        service = ReturnService(db)
        try:
            return await service.lookup_return_list(request.return_invoice_numbers)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

    async def get_returns_by_date(
        self,
        return_date: str,
        db: Session = Depends(get_db)
    ):
        service = ReturnService(db)
        try:
            return service.get_returns_by_date(return_date)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

    async def get_return(
        self,
        return_invoice_number: str,
        db: Session = Depends(get_db)
    ):
        service = ReturnService(db)
        return_delivery = service.get_return_by_invoice(return_invoice_number)
        if not return_delivery:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="반품 정보를 찾을 수 없습니다."
            )
        return return_delivery

    async def get_returns_by_original_invoice(
        self,
        original_invoice_number: str,
        db: Session = Depends(get_db)
    ):
        service = ReturnService(db)
        try:
            return service.get_returns_by_original_invoice(original_invoice_number)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

    async def update_return_status(
        self,
        return_invoice_number: str,
        status_request: dict,
        db: Session = Depends(get_db)
    ):
        service = ReturnService(db)
        try:
            new_status = status_request.get("status")
            location = status_request.get("location")
            memo = status_request.get("memo")
            
            if not new_status:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="상태 값이 필요합니다."
                )
            
            result = service.update_return_status(
                return_invoice_number, 
                new_status,
                location=location,
                memo=memo
            )
            
            if not result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="반품 정보를 찾을 수 없습니다."
                )
            
            return {"message": "반품 상태가 업데이트되었습니다.", "success": True}
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

    async def delete_return(
        self,
        return_invoice_number: str,
        db: Session = Depends(get_db)
    ):
        service = ReturnService(db)
        try:
            result = service.delete_return(return_invoice_number)
            if not result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="반품 정보를 찾을 수 없습니다."
                )
            return {"message": "반품이 삭제되었습니다.", "success": True}
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )