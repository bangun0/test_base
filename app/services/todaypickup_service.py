import httpx
from typing import Any, Dict, Optional


class TodayPickupService:
    """Service for interacting with the TodayPickup external API."""

    BASE_URL = "https://admin.todaypickup.com"

    async def request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> httpx.Response:
        """Make an HTTP request to the TodayPickup API."""
        url = f"{self.BASE_URL}{path}"
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method,
                url,
                params=params,
                json=data,
                headers=headers,
            )
        return response
