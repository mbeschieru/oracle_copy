from uuid import UUID

from fastapi import HTTPException

from app.domain.exceptions.base import DomainException
from app.domain.repositories.user_repository import UserRepositoryInterface
from app.use_case.validators.role_validator import require_manager


def assert_user_identity_matches(payload_user_id: str, header_user_id: str):
    if str(payload_user_id) != str(header_user_id):
        raise HTTPException(
            status_code=403,
            detail="User ID in request body does not match authenticated user",
        )


def assert_user_can_access_user(
    requester_id: UUID,
    target_user_id: UUID,
    user_repo: UserRepositoryInterface,
):
    if requester_id == target_user_id:
        return

    requester = user_repo.get_by_id(requester_id)
    target_user = user_repo.get_by_id(target_user_id)

    if not requester or not target_user:
        raise DomainException(
            message="Not Found",
            details="Requester or target user not found",
            http_code=404,
        )

    require_manager(requester)  # verifică dacă requester e manager

    if requester.project_id != target_user.project_id:
        raise DomainException(
            message="Permission denied",
            details="You may only view timesheets of users in your project.",
            http_code=403,
        )
