from fastapi import APIRouter, HTTPException, status
from typing import Any, Dict, Optional

from app.services.todaypickup_service import TodayPickupService


class TodayPickupController:
    """Controller exposing endpoints that proxy requests to the TodayPickup API."""

    def __init__(self) -> None:
        self.router = APIRouter(prefix="/todaypickup", tags=["todaypickup"])
        self.service = TodayPickupService()
        self._register_routes()

    def _register_routes(self) -> None:
        self.router.get("/{full_path:path}")(self.proxy_get)
        self.router.post("/{full_path:path}")(self.proxy_post)

    async def proxy_get(self, full_path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        response = await self.service.request("GET", f"/{full_path}", params=params)
        if response.is_success:
            return response.json()
        raise HTTPException(status_code=response.status_code, detail=response.text)

    async def proxy_post(
        self,
        full_path: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> Any:
        response = await self.service.request("POST", f"/{full_path}", data=data)
        if response.is_success:
            return response.json()
        raise HTTPException(status_code=response.status_code, detail=response.text)
