from fastapi import HTTPException, status, Security
from fastapi.security.api_key import APIKeyHeader
from uuid import UUID

user_id_header = APIKeyHeader(name="X-User-Id", auto_error=False)

def get_authenticated_user_id(x_user_id: str = Security(user_id_header)) -> UUID:
    if not x_user_id:
        raise HTTPException(status_code=401, detail="Missing X-User-Id header")
    try:
        return UUID(x_user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")