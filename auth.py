"""
Optional API key authentication.
When API_KEY env is set, protected routes require X-API-Key or Authorization: Bearer <key>.
Public routes: /health, /health/ready, /docs, /openapi.json, /redoc.
"""
from fastapi import Header, HTTPException, Request
from typing import Optional

from config import get_api_key


def require_api_key(
    request: Request,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    authorization: Optional[str] = Header(None),
) -> None:
    """Dependency: require API key when API_KEY env is set."""
    key = get_api_key()
    if not key:
        return
    # Accept X-API-Key: <key> or Authorization: Bearer <key>
    provided = None
    if x_api_key:
        provided = x_api_key
    elif authorization and authorization.startswith("Bearer "):
        provided = authorization[7:].strip()
    if provided != key:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
