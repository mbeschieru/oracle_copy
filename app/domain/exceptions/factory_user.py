from app.domain.exceptions.base import DomainException


def user_not_found(user_id: str) -> DomainException:
    return DomainException(
        message="User not found",
        details=f"No user found with ID {user_id}",
        http_code=404,
    )


def user_email_not_found(email: str) -> DomainException:
    return DomainException(
        message="User not found",
        details=f" User with email {email} was not found",
        http_code=404,
    )
