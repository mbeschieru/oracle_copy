from fastapi import HTTPException

def assert_user_identity_matches(payload_user_id: str, header_user_id: str):
    if str(payload_user_id) != str(header_user_id):
        raise HTTPException(
            status_code=403,
            detail="User ID in request body does not match authenticated user"
        )
