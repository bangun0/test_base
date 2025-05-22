"""
FastAPI Dependencies for Authentication and Authorization.

This module provides reusable dependency functions for FastAPI endpoints,
primarily focused on extracting and validating authentication credentials
(like tokens and agency IDs) from request headers. These dependencies
can be injected into endpoint functions to ensure that requests are
properly authenticated before proceeding.
"""
from fastapi import Header, HTTPException, status
from typing import Optional

async def get_mall_auth_token(authorization: Optional[str] = Header(None)) -> str:
    """
    Retrieves and validates the Mall API authentication token from the 'Authorization' header.

    It expects the token to be in the "Bearer <token>" format.

    Args:
        authorization: The content of the 'Authorization' header.
                       FastAPI injects this from the request. Defaults to None.

    Returns:
        The extracted authentication token if valid.

    Raises:
        HTTPException (401 Unauthorized): If the 'Authorization' header is missing,
                                          not in "Bearer <token>" format, or invalid.
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header is missing",
        )
    
    # Expecting "Bearer <token>" format for Mall API token
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization header format. Expected 'Bearer <token>'",
        )
    return parts[1] # Return the token part

async def get_agency_auth_token(authorization: Optional[str] = Header(None)) -> str:
    """
    Retrieves the Agency API authentication token from the 'Authorization' header.

    Based on API documentation, this might be the raw token without a "Bearer" prefix.

    Args:
        authorization: The content of the 'Authorization' header.
                       FastAPI injects this from the request. Defaults to None.

    Returns:
        The authentication token.

    Raises:
        HTTPException (401 Unauthorized): If the 'Authorization' header is missing.
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header is missing",
        )
    # The TodayPickup API documentation for agency endpoints implies the token is sent directly
    # without a "Bearer" prefix. If this understanding is incorrect, this function
    # should be updated to match the `get_mall_auth_token` structure.
    return authorization

async def get_agency_id(agencyId: Optional[str] = Header(None)) -> str:
    """
    Retrieves the Agency ID from the 'agencyId' header.

    Args:
        agencyId: The content of the 'agencyId' header.
                  FastAPI injects this from the request. Defaults to None.
                  Header name is case-insensitive, but 'agencyId' is used for clarity.

    Returns:
        The Agency ID.

    Raises:
        HTTPException (400 Bad Request): If the 'agencyId' header is missing.
                                        A 401 or 403 might also be appropriate depending
                                        on how strictly this is tied to authentication vs.
                                        just being a required parameter for agency operations.
                                        Using 400 as it's a missing required parameter here.
    """
    if not agencyId:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="agencyId header is missing",
        )
    return agencyId
