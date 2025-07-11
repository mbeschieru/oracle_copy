from fastapi import HTTPException, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from uuid import UUID

security = HTTPBearer()

def get_authenticated_user_id(credentials: HTTPAuthorizationCredentials = Security(security)) -> UUID:
    if not credentials or not credentials.credentials:
        raise HTTPException(status_code=401, detail="Missing Bearer token")
    try:
        return UUID(credentials.credentials)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format in Bearer token")