from fastapi import APIRouter, Depends, Header
from app.repositories.todaypickup_repository import TodayPickupRepository
from app.services.todaypickup_service import TodayPickupService
from app.schemas.todaypickup import (
    AuthAgencyDTO,
    DeliveryAgencyUpdateConsignDTO,
    DeliveryAgencyStateUpdateDTO,
    DeliveryAgencyFlexListUpdateDTO,
    DeliveryInvoiceNumberDTO,
    PostalCodeListDTO,
    GoodsReturnRequestDTO,
    MallApiDeliveryDTO,
    GoodsNoDawnDTO,
    MallApiReturnDTO,
)


def get_service() -> TodayPickupService:
    repo = TodayPickupRepository()
    return TodayPickupService(repo)


class TodayPickupController:
    def __init__(self):
        self.router = APIRouter(tags=["todaypickup"])
        self._register_routes()

    def _register_routes(self):
        self.router.post("/api/agency/auth")(self.agency_auth)
        self.router.post("/api/agency/auth/token")(self.agency_auth_token)
        self.router.put("/api/agency/delivery")(self.agency_delivery)
        self.router.put("/api/agency/delivery/flex")(self.agency_delivery_flex)
        self.router.put("/api/agency/delivery/list/flex")(self.agency_delivery_list_flex)
        self.router.post("/api/agency/delivery/list/{delivery_dt}")(self.agency_delivery_list)
        self.router.put("/api/agency/delivery/state")(self.agency_delivery_state)
        self.router.post("/api/agency/delivery/{invoice_number_list}")(self.agency_delivery_invoice)
        self.router.post("/api/agency/postal/save")(self.agency_postal_save)
        self.router.post("/api/mall/cancelDelivery")(self.mall_cancel_delivery)
        self.router.get("/api/mall/delivery/{invoice_number}")(self.mall_delivery)
        self.router.get("/api/mall/deliveryList/{invoice_number_list}")(self.mall_delivery_list)
        self.router.post("/api/mall/deliveryListRegister")(self.mall_delivery_list_register)
        self.router.post("/api/mall/deliveryRegister")(self.mall_delivery_register)
        self.router.get("/api/mall/possibleDelivery")(self.mall_possible_delivery)
        self.router.post("/api/mall/returnDelivery")(self.mall_return_delivery)
        self.router.post("/api/mall/returnListRegister")(self.mall_return_list_register)
        self.router.post("/api/mall/returnRegister")(self.mall_return_register)

    async def agency_auth(self, Authorization: str = Header(...), agencyId: str = Header(...), service: TodayPickupService = Depends(get_service)):
        return await service.agency_auth(Authorization, agencyId)

    async def agency_auth_token(self, payload: AuthAgencyDTO, Authorization: str = Header(...), agencyId: str = Header(...), service: TodayPickupService = Depends(get_service)):
        return await service.agency_auth_token(Authorization, agencyId, payload)

    async def agency_delivery(self, payload: DeliveryAgencyUpdateConsignDTO, Authorization: str = Header(...), agencyId: str = Header(...), service: TodayPickupService = Depends(get_service)):
        return await service.agency_delivery(Authorization, agencyId, payload)

    async def agency_delivery_flex(self, payload: DeliveryInvoiceNumberDTO, Authorization: str = Header(...), agencyId: str = Header(...), service: TodayPickupService = Depends(get_service)):
        return await service.agency_delivery_flex(Authorization, agencyId, payload)

    async def agency_delivery_list_flex(self, payload: DeliveryAgencyFlexListUpdateDTO, Authorization: str = Header(...), agencyId: str = Header(...), service: TodayPickupService = Depends(get_service)):
        return await service.agency_delivery_list_flex(Authorization, agencyId, payload)

    async def agency_delivery_list(self, delivery_dt: str, Authorization: str = Header(...), agencyId: str = Header(...), service: TodayPickupService = Depends(get_service)):
        return await service.agency_delivery_list(Authorization, agencyId, delivery_dt)

    async def agency_delivery_state(self, payload: DeliveryAgencyStateUpdateDTO, Authorization: str = Header(...), agencyId: str = Header(...), service: TodayPickupService = Depends(get_service)):
        return await service.agency_delivery_state(Authorization, agencyId, payload)

    async def agency_delivery_invoice(self, invoice_number_list: str, Authorization: str = Header(...), agencyId: str = Header(...), service: TodayPickupService = Depends(get_service)):
        return await service.agency_delivery_invoice(Authorization, agencyId, invoice_number_list)

    async def agency_postal_save(self, payload: PostalCodeListDTO, Authorization: str = Header(...), agencyId: str = Header(...), service: TodayPickupService = Depends(get_service)):
        return await service.agency_postal_save(Authorization, agencyId, payload)

    async def mall_cancel_delivery(self, payload: GoodsReturnRequestDTO, Authorization: str = Header(...), service: TodayPickupService = Depends(get_service)):
        return await service.mall_cancel_delivery(Authorization, payload)

    async def mall_delivery(self, invoice_number: str, Authorization: str = Header(...), service: TodayPickupService = Depends(get_service)):
        return await service.mall_delivery(Authorization, invoice_number)

    async def mall_delivery_list(self, invoice_number_list: str, Authorization: str = Header(...), service: TodayPickupService = Depends(get_service)):
        return await service.mall_delivery_list(Authorization, invoice_number_list)

    async def mall_delivery_list_register(self, payload: MallApiDeliveryDTO, Authorization: str = Header(...), service: TodayPickupService = Depends(get_service)):
        return await service.mall_delivery_list_register(Authorization, payload)

    async def mall_delivery_register(self, payload: GoodsNoDawnDTO, Authorization: str = Header(...), service: TodayPickupService = Depends(get_service)):
        return await service.mall_delivery_register(Authorization, payload)

    async def mall_possible_delivery(self, address: str, Authorization: str = Header(...), postalCode: str | None = None, dawnDelivery: str | None = None, service: TodayPickupService = Depends(get_service)):
        return await service.mall_possible_delivery(Authorization, address, postalCode, dawnDelivery)

    async def mall_return_delivery(self, payload: GoodsReturnRequestDTO, Authorization: str = Header(...), service: TodayPickupService = Depends(get_service)):
        return await service.mall_return_delivery(Authorization, payload)

    async def mall_return_list_register(self, payload: MallApiReturnDTO, Authorization: str = Header(...), service: TodayPickupService = Depends(get_service)):
        return await service.mall_return_list_register(Authorization, payload)

    async def mall_return_register(self, payload: GoodsNoDawnDTO, Authorization: str = Header(...), service: TodayPickupService = Depends(get_service)):
        return await service.mall_return_register(Authorization, payload)
