from uuid import UUID

from app.domain.entities.user import User
from app.domain.repositories.user_repository import UserRepositoryInterface
from app.infrastructure.config.db_config import SessionLocal
from app.infrastructure.config.jwt_config import (
    create_access_token,
    verify_password,
)
from app.infrastructure.db.models.user_models import UserModel


class UserRepository(UserRepositoryInterface):

    def get_by_email(self, email: str):
        with SessionLocal() as session:
            return (
                session.query(UserModel)
                .filter(UserModel.email == email)
                .first()
            )

    def get_by_id(self, user_id: UUID):
        with SessionLocal() as session:
            user_model = (
                session.query(UserModel)
                .filter(UserModel.user_id == str(user_id))
                .first()
            )
            if not user_model:
                return None
            return User(
                user_id=UUID(user_model.user_id),
                name=user_model.name,
                email=user_model.email,
                role=user_model.role,
                grade=user_model.grade,
                created_at=user_model.created_at,
                project_id=(
                    UUID(user_model.project_id)
                    if user_model.project_id
                    else None
                ),
            )

    def get_all_users(self, offset=0, limit=10):
        with SessionLocal() as session:
            return (
                session.query(UserModel)
                .order_by(UserModel.created_at)
                .offset(offset)
                .limit(limit)
                .all()
            )

    def get_users_by_project(self, project_id, offset=0, limit=10):
        with SessionLocal() as session:
            return (
                session.query(UserModel)
                .filter(UserModel.project_id == project_id)
                .order_by(UserModel.created_at)
                .offset(offset)
                .limit(limit)
                .all()
            )

    def authenticate_user(self, email: str, password: str):
        """Authenticate user with email and password"""
        user = self.get_by_email(email)
        if not user:
            return None

        if verify_password(password, user.password_hash):
            return user

        return None

    def create_jwt_token(self, user):
        """Create JWT token for user"""
        data = {"sub": str(user.user_id)}
        return create_access_token(data=data)
