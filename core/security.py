import os
from functools import lru_cache
from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


@lru_cache
def _get_key() -> str | None:
    return os.getenv("API_KEY")


async def get_api_key(api_key_header: str = Security(api_key_header)):
    expected = _get_key()
    if not expected:
        raise RuntimeError("API_KEY environment variable is not set")
    if api_key_header == expected:
        return api_key_header
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing API Key",
    )
