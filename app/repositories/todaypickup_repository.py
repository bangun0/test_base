import httpx
from typing import Any, Dict, Optional

class TodayPickupRepository:
    BASE_URL = "https://admin.todaypickup.com"

    def __init__(self, client: Optional[httpx.AsyncClient] = None):
        self.client = client

    async def _request(self, method: str, path: str, *, headers: Optional[Dict[str, str]] = None,
                       json: Any = None, params: Dict[str, Any] | None = None) -> Any:
        async with (self.client or httpx.AsyncClient(base_url=self.BASE_URL)) as client:
            response = await client.request(method, path, headers=headers, json=json, params=params)
            response.raise_for_status()
            return response.json()

    async def post(self, path: str, headers: Dict[str, str], payload: Any) -> Any:
        return await self._request("POST", path, headers=headers, json=payload)

    async def put(self, path: str, headers: Dict[str, str], payload: Any) -> Any:
        return await self._request("PUT", path, headers=headers, json=payload)

    async def get(self, path: str, headers: Dict[str, str], params: Optional[Dict[str, Any]] = None) -> Any:
        return await self._request("GET", path, headers=headers, params=params)
