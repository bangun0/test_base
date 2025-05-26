from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import List, Optional

from app.config.database import get_db
from app.services.agency_service import AgencyService
from app.schemas.agency import (
    AgencyCreate, AgencyResponse, AuthTokenRequest, AuthTokenResponse,
    TokenGenerateRequest, TokenGenerateResponse, DeliveryAssignmentRequest,
    DeliveryCompletionRequest, DeliveryFlexTransferRequest, DeliveryListRequest,
    DeliveryLookupRequest, PostalCodeSaveRequest, PostalCodeResponse,
    DeliveryAssignmentResponse
)


class TodayPickupAgencyController:
    def __init__(self):
        self.router = APIRouter(
            prefix="/api/agency",
            tags=["agency"]
        )
        self._register_routes()
    
    def _register_routes(self):
        self.router.post("/auth", response_model=AuthTokenResponse)(self.validate_auth)
        self.router.post("/auth/token", response_model=TokenGenerateResponse)(self.generate_token)
        
        self.router.put("/delivery")(self.complete_delivery)
        self.router.put("/delivery/flex")(self.transfer_to_flex)
        self.router.put("/delivery/list/flex")(self.transfer_list_to_flex)
        self.router.put("/delivery/state")(self.update_delivery_state)
        self.router.post("/delivery/list/{delivery_date}")(self.get_delivery_list)
        self.router.post("/delivery/{invoice_number_list}")(self.lookup_deliveries)
        
        self.router.post("/postal/save", response_model=List[PostalCodeResponse])(self.save_postal_codes)
        
        self.router.post("/agencies", response_model=AgencyResponse)(self.create_agency)
        self.router.get("/agencies/{agency_id}", response_model=AgencyResponse)(self.get_agency)
        self.router.delete("/agencies/{agency_id}")(self.deactivate_agency)
        self.router.get("/agencies/{agency_id}/postal-codes", response_model=List[PostalCodeResponse])(self.get_postal_codes)
        self.router.post("/delivery/assign", response_model=DeliveryAssignmentResponse)(self.create_delivery_assignment)

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

    async def validate_auth(self, request: AuthTokenRequest, db: Session = Depends(get_db)):
        service = AgencyService(db)
        try:
            return await service.validate_token(request)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

    async def generate_token(self, request: TokenGenerateRequest, db: Session = Depends(get_db)):
        service = AgencyService(db)
        try:
            return await service.generate_token(request)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

    async def complete_delivery(
        self, 
        request: DeliveryCompletionRequest,
        db: Session = Depends(get_db),
        authorization: str = Depends(_get_auth_token)
    ):
        service = AgencyService(db, authorization)
        try:
            result = await service.complete_delivery(request)
            if not result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="배송 정보를 찾을 수 없습니다."
                )
            return {"message": "배송이 완료되었습니다.", "success": True}
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

    async def transfer_to_flex(
        self,
        request: DeliveryFlexTransferRequest,
        db: Session = Depends(get_db),
        authorization: str = Depends(_get_auth_token)
    ):
        service = AgencyService(db, authorization)
        try:
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

    async def transfer_list_to_flex(
        self,
        requests: List[DeliveryFlexTransferRequest],
        db: Session = Depends(get_db),
        authorization: str = Depends(_get_auth_token)
    ):
        service = AgencyService(db, authorization)
        try:
            results = await service.transfer_list_to_flex(requests)
            success_count = sum(results)
            return {
                "message": f"{success_count}/{len(requests)} 건이 플렉스로 이관되었습니다.",
                "success": True,
                "results": results
            }
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

    async def update_delivery_state(
        self,
        state_request: dict,
        db: Session = Depends(get_db),
        authorization: str = Depends(_get_auth_token)
    ):
        agency_service = AgencyService(db, authorization)
        try:
            return {"message": "배송 상태가 업데이트되었습니다.", "success": True}
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

    async def get_delivery_list(
        self,
        delivery_date: str,
        request: DeliveryListRequest,
        db: Session = Depends(get_db),
        authorization: str = Depends(_get_auth_token)
    ):
        service = AgencyService(db, authorization)
        try:
            request.delivery_date = delivery_date
            return await service.get_delivery_list(request)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

    async def lookup_deliveries(
        self,
        invoice_number_list: str,
        db: Session = Depends(get_db),
        authorization: str = Depends(_get_auth_token)
    ):
        service = AgencyService(db, authorization)
        try:
            invoice_numbers = invoice_number_list.split(",")
            request = DeliveryLookupRequest(invoice_numbers=invoice_numbers)
            return await service.lookup_deliveries(request)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

    async def save_postal_codes(
        self,
        request: PostalCodeSaveRequest,
        db: Session = Depends(get_db),
        authorization: str = Depends(_get_auth_token)
    ):
        service = AgencyService(db, authorization)
        try:
            return await service.save_postal_codes(request)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

    async def create_agency(self, agency_data: AgencyCreate, db: Session = Depends(get_db)):
        service = AgencyService(db)
        try:
            return service.create_agency(agency_data)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

    async def get_agency(self, agency_id: str, db: Session = Depends(get_db)):
        service = AgencyService(db)
        agency = service.get_agency_by_id(agency_id)
        if not agency:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="에이전시를 찾을 수 없습니다."
            )
        return agency

    async def deactivate_agency(self, agency_id: str, db: Session = Depends(get_db)):
        service = AgencyService(db)
        if not service.deactivate_agency(agency_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="에이전시를 찾을 수 없습니다."
            )
        return {"message": "에이전시가 비활성화되었습니다.", "success": True}

    async def get_postal_codes(self, agency_id: str, db: Session = Depends(get_db)):
        service = AgencyService(db)
        return service.get_postal_codes_by_agency(agency_id)

    async def create_delivery_assignment(
        self,
        request: DeliveryAssignmentRequest,
        db: Session = Depends(get_db)
    ):
        service = AgencyService(db)
        try:
            return service.create_delivery_assignment(request)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )