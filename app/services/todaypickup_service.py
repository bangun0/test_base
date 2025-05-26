from typing import Any, Dict, Optional
from app.repositories.todaypickup_repository import TodayPickupRepository
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

class TodayPickupService:
    def __init__(self, repository: TodayPickupRepository):
        self.repo = repository

    async def agency_auth(self, authorization: str, agency_id: str) -> Any:
        headers = {"Authorization": authorization, "agencyId": agency_id}
        return await self.repo.post("/api/agency/auth", headers, None)

    async def agency_auth_token(self, authorization: str, agency_id: str, payload: AuthAgencyDTO) -> Any:
        headers = {"Authorization": authorization, "agencyId": agency_id}
        return await self.repo.post("/api/agency/auth/token", headers, payload.model_dump())

    async def agency_delivery(self, authorization: str, agency_id: str, payload: DeliveryAgencyUpdateConsignDTO) -> Any:
        headers = {"Authorization": authorization, "agencyId": agency_id}
        return await self.repo.put("/api/agency/delivery", headers, payload.model_dump())

    async def agency_delivery_flex(self, authorization: str, agency_id: str, payload: DeliveryInvoiceNumberDTO) -> Any:
        headers = {"Authorization": authorization, "agencyId": agency_id}
        return await self.repo.put("/api/agency/delivery/flex", headers, payload.model_dump())

    async def agency_delivery_list_flex(self, authorization: str, agency_id: str, payload: DeliveryAgencyFlexListUpdateDTO) -> Any:
        headers = {"Authorization": authorization, "agencyId": agency_id}
        return await self.repo.put("/api/agency/delivery/list/flex", headers, payload.model_dump())

    async def agency_delivery_list(self, authorization: str, agency_id: str, delivery_dt: str) -> Any:
        headers = {"Authorization": authorization, "agencyId": agency_id}
        path = f"/api/agency/delivery/list/{delivery_dt}"
        return await self.repo.post(path, headers, None)

    async def agency_delivery_state(self, authorization: str, agency_id: str, payload: DeliveryAgencyStateUpdateDTO) -> Any:
        headers = {"Authorization": authorization, "agencyId": agency_id}
        return await self.repo.put("/api/agency/delivery/state", headers, payload.model_dump())

    async def agency_delivery_invoice(self, authorization: str, agency_id: str, invoice_number_list: str) -> Any:
        headers = {"Authorization": authorization, "agencyId": agency_id}
        path = f"/api/agency/delivery/{invoice_number_list}"
        return await self.repo.post(path, headers, None)

    async def agency_postal_save(self, authorization: str, agency_id: str, payload: PostalCodeListDTO) -> Any:
        headers = {"Authorization": authorization, "agencyId": agency_id}
        return await self.repo.post("/api/agency/postal/save", headers, payload.model_dump())

    async def mall_cancel_delivery(self, authorization: str, payload: GoodsReturnRequestDTO) -> Any:
        headers = {"Authorization": authorization}
        return await self.repo.post("/api/mall/cancelDelivery", headers, payload.model_dump())

    async def mall_delivery(self, authorization: str, invoice_number: str) -> Any:
        headers = {"Authorization": authorization}
        path = f"/api/mall/delivery/{invoice_number}"
        return await self.repo.get(path, headers)

    async def mall_delivery_list(self, authorization: str, invoice_number_list: str) -> Any:
        headers = {"Authorization": authorization}
        path = f"/api/mall/deliveryList/{invoice_number_list}"
        return await self.repo.get(path, headers)

    async def mall_delivery_list_register(self, authorization: str, payload: MallApiDeliveryDTO) -> Any:
        headers = {"Authorization": authorization}
        return await self.repo.post("/api/mall/deliveryListRegister", headers, payload.model_dump())

    async def mall_delivery_register(self, authorization: str, payload: GoodsNoDawnDTO) -> Any:
        headers = {"Authorization": authorization}
        return await self.repo.post("/api/mall/deliveryRegister", headers, payload.model_dump())

    async def mall_possible_delivery(self, authorization: str, address: str, postal_code: Optional[str] = None, dawn_delivery: Optional[str] = None) -> Any:
        headers = {"Authorization": authorization}
        params = {"address": address}
        if postal_code:
            params["postalCode"] = postal_code
        if dawn_delivery:
            params["dawnDelivery"] = dawn_delivery
        return await self.repo.get("/api/mall/possibleDelivery", headers, params=params)

    async def mall_return_delivery(self, authorization: str, payload: GoodsReturnRequestDTO) -> Any:
        headers = {"Authorization": authorization}
        return await self.repo.post("/api/mall/returnDelivery", headers, payload.model_dump())

    async def mall_return_list_register(self, authorization: str, payload: MallApiReturnDTO) -> Any:
        headers = {"Authorization": authorization}
        return await self.repo.post("/api/mall/returnListRegister", headers, payload.model_dump())

    async def mall_return_register(self, authorization: str, payload: GoodsNoDawnDTO) -> Any:
        headers = {"Authorization": authorization}
        return await self.repo.post("/api/mall/returnRegister", headers, payload.model_dump())
