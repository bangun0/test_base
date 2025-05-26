import httpx
import asyncio
from typing import Dict, List, Any, Optional
import json
import logging

logger = logging.getLogger(__name__)


class TodayPickupClient:
    def __init__(self, base_url: str = "https://admin.todaypickup.com", timeout: int = 30):
        self.base_url = base_url
        self.timeout = timeout
        
    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict] = None,
        headers: Optional[Dict] = None
    ) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"
        
        default_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        if headers:
            default_headers.update(headers)
            
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                if method.upper() == "GET":
                    response = await client.get(url, headers=default_headers, params=data)
                elif method.upper() == "POST":
                    response = await client.post(url, headers=default_headers, json=data)
                elif method.upper() == "PUT":
                    response = await client.put(url, headers=default_headers, json=data)
                else:
                    raise ValueError(f"지원하지 않는 HTTP 메서드: {method}")
                
                response.raise_for_status()
                return response.json()
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP 오류 발생: {e.response.status_code} - {e.response.text}")
            raise Exception(f"API 호출 실패: {e.response.status_code}")
        except httpx.RequestError as e:
            logger.error(f"요청 오류 발생: {str(e)}")
            raise Exception(f"네트워크 오류: {str(e)}")
        except Exception as e:
            logger.error(f"예상치 못한 오류 발생: {str(e)}")
            raise

    async def register_delivery(self, delivery_data: Dict, auth_token: str) -> Dict[str, Any]:
        headers = {"Authorization": f"Bearer {auth_token}"}
        return await self._make_request("POST", "/api/mall/deliveryRegister", delivery_data, headers)

    async def register_delivery_list(self, deliveries_data: List[Dict], auth_token: str) -> Dict[str, Any]:
        headers = {"Authorization": f"Bearer {auth_token}"}
        return await self._make_request("POST", "/api/mall/deliveryListRegister", {"deliveries": deliveries_data}, headers)

    async def lookup_delivery(self, invoice_number: str, auth_token: str) -> Dict[str, Any]:
        headers = {"Authorization": f"Bearer {auth_token}"}
        return await self._make_request("GET", f"/api/mall/delivery/{invoice_number}", headers=headers)

    async def lookup_delivery_list(self, invoice_numbers: List[str], auth_token: str) -> Dict[str, Any]:
        headers = {"Authorization": f"Bearer {auth_token}"}
        invoice_list = ",".join(invoice_numbers)
        return await self._make_request("GET", f"/api/mall/deliveryList/{invoice_list}", headers=headers)

    async def check_possible_delivery(self, zipcode: str, address: str, auth_token: str) -> Dict[str, Any]:
        headers = {"Authorization": f"Bearer {auth_token}"}
        params = {"zipcode": zipcode, "address": address}
        return await self._make_request("GET", "/api/mall/possibleDelivery", params, headers)

    async def cancel_delivery(self, cancel_data: Dict, auth_token: str) -> Dict[str, Any]:
        headers = {"Authorization": f"Bearer {auth_token}"}
        return await self._make_request("POST", "/api/mall/cancelDelivery", cancel_data, headers)

    async def request_return_delivery(self, return_data: Dict, auth_token: str) -> Dict[str, Any]:
        headers = {"Authorization": f"Bearer {auth_token}"}
        return await self._make_request("POST", "/api/mall/returnDelivery", return_data, headers)

    async def register_return(self, return_data: Dict, auth_token: str) -> Dict[str, Any]:
        headers = {"Authorization": f"Bearer {auth_token}"}
        return await self._make_request("POST", "/api/mall/returnRegister", return_data, headers)

    async def register_return_list(self, returns_data: List[Dict], auth_token: str) -> Dict[str, Any]:
        headers = {"Authorization": f"Bearer {auth_token}"}
        return await self._make_request("POST", "/api/mall/returnListRegister", {"returns": returns_data}, headers)

    async def agency_auth_validate(self, auth_data: Dict) -> Dict[str, Any]:
        return await self._make_request("POST", "/api/agency/auth", auth_data)

    async def agency_generate_token(self, token_data: Dict) -> Dict[str, Any]:
        return await self._make_request("POST", "/api/agency/auth/token", token_data)

    async def agency_complete_delivery(self, completion_data: Dict, auth_token: str) -> Dict[str, Any]:
        headers = {"Authorization": f"Bearer {auth_token}"}
        return await self._make_request("PUT", "/api/agency/delivery", completion_data, headers)

    async def agency_transfer_to_flex(self, transfer_data: Dict, auth_token: str) -> Dict[str, Any]:
        headers = {"Authorization": f"Bearer {auth_token}"}
        return await self._make_request("PUT", "/api/agency/delivery/flex", transfer_data, headers)

    async def agency_transfer_list_to_flex(self, transfers_data: List[Dict], auth_token: str) -> Dict[str, Any]:
        headers = {"Authorization": f"Bearer {auth_token}"}
        return await self._make_request("PUT", "/api/agency/delivery/list/flex", {"transfers": transfers_data}, headers)

    async def agency_update_delivery_state(self, state_data: Dict, auth_token: str) -> Dict[str, Any]:
        headers = {"Authorization": f"Bearer {auth_token}"}
        return await self._make_request("PUT", "/api/agency/delivery/state", state_data, headers)

    async def agency_get_delivery_list(self, delivery_date: str, agency_data: Dict, auth_token: str) -> Dict[str, Any]:
        headers = {"Authorization": f"Bearer {auth_token}"}
        return await self._make_request("POST", f"/api/agency/delivery/list/{delivery_date}", agency_data, headers)

    async def agency_lookup_deliveries(self, lookup_data: Dict, auth_token: str) -> Dict[str, Any]:
        headers = {"Authorization": f"Bearer {auth_token}"}
        invoice_list = ",".join(lookup_data.get("invoice_numbers", []))
        return await self._make_request("POST", f"/api/agency/delivery/{invoice_list}", {}, headers)

    async def agency_save_postal_codes(self, postal_data: Dict, auth_token: str) -> Dict[str, Any]:
        headers = {"Authorization": f"Bearer {auth_token}"}
        return await self._make_request("POST", "/api/agency/postal/save", postal_data, headers)