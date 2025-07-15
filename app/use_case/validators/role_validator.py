from app.domain.entities.user import User
from app.domain.enums import UserRole
from app.domain.exceptions.base import DomainException


def require_manager(user: User):
    if user.role != UserRole.MANAGER:
        raise DomainException(
            message="Permission denied",
            details="Only managers can perform this action",
            http_code=403,
        )
