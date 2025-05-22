from fastapi import APIRouter, HTTPException
from starlette.requests import Request
from starlette.responses import Response
import httpx
import logging

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

router = APIRouter()

BASE_URL = "https://admin.todaypickup.com/v2/api-docs/"

# Headers to remove from the incoming request before forwarding
# Host header is automatically managed by httpx, but good to be aware
HOP_BY_HOP_HEADERS = [
    "connection", "keep-alive", "proxy-authenticate", "proxy-authorization",
    "te", "trailers", "transfer-encoding", "upgrade", "host"
]

@router.api_route("/relay/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"])
async def relay_request(request: Request, path: str):
    target_url = f"{BASE_URL}{path}"

    # Preserve query parameters
    if request.url.query:
        target_url += f"?{request.url.query}"

    # Prepare headers
    forward_headers = {}
    for name, value in request.headers.items():
        if name.lower() not in HOP_BY_HOP_HEADERS:
            forward_headers[name] = value
    
    # Get request body
    body = await request.body()

    async with httpx.AsyncClient() as client:
        try:
            logger.info(f"Forwarding request: {request.method} {target_url}")
            rp = await client.request(
                method=request.method,
                url=target_url,
                headers=forward_headers,
                content=body if body else None,
                # Timeout can be configured if needed, e.g., timeout=10.0
            )
            logger.info(f"Received response: Status {rp.status_code}")

            # Prepare response headers
            response_headers = {}
            for name, value in rp.headers.items():
                # Example of filtering out a sensitive header from the response
                # if name.lower() not in ["x-sensitive-header"]:
                response_headers[name] = value
            
            # It's important to use rp.content instead of rp.text for binary responses
            return Response(content=rp.content, status_code=rp.status_code, headers=response_headers)

        except httpx.TimeoutException as e:
            logger.error(f"Request to {target_url} timed out: {e}")
            raise HTTPException(status_code=504, detail=f"Gateway timeout: {e}")
        except httpx.RequestError as e:
            logger.error(f"Error forwarding request to {target_url}: {e}")
            # More specific error handling can be added here based on error type
            raise HTTPException(status_code=502, detail=f"Bad gateway: Error connecting to the upstream server. {e}")
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            raise HTTPException(status_code=500, detail=f"Internal server error: {e}")
