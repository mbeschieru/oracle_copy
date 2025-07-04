from app.domain.repositories.user_repository import UserRepositoryInterface
from app.domain.entities.user import User
from app.domain.dto.user_dto import UserReadDTO
from app.domain.exceptions.factory_user import (
    user_email_not_found,
    user_not_found
)
class UserService:

    def __init__(self, user_repo: UserRepositoryInterface):
        self.user_repo = user_repo

    def login_by_email(self, email: str) -> User:
        user = self.user_repo.get_by_email(email)
        if not user:
            raise user_email_not_found(email)
        return UserReadDTO.from_orm(user)

    def get_user_details(self, user_id):
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise user_not_found(str(user_id))
        return UserReadDTO.from_orm(user)

    def get_all_users(self):
        users = self.user_repo.get_all_users()
        return UserReadDTO.from_orm(users)
