from uuid import UUID
from app.domain.repositories.user_repository import UserRepositoryInterface
from app.infrastructure.config.db_config import SessionLocal
from app.infrastructure.db.models.user_models import UserModel
from app.infrastructure.config.jwt_config import verify_password, create_access_token
from app.domain.entities.user import User
from app.domain.enums import UserRole, UserGrade

class UserRepository(UserRepositoryInterface):

    def get_by_email(self, email: str):
        with SessionLocal() as session:
            return session.query(UserModel).filter(UserModel.email == email).first()

    def get_by_id(self, user_id: UUID):
        with SessionLocal() as session:
            return session.query(UserModel).filter(UserModel.user_id == str(user_id)).first()

    def get_all_users(self, offset=0, limit=10):
        with SessionLocal() as session:
            return session.query(UserModel).order_by(UserModel.created_at).offset(offset).limit(limit).all()

    def get_users_by_project(self, project_id, offset=0, limit=10):
        with SessionLocal() as session:
            return session.query(UserModel).filter(UserModel.project_id == project_id).order_by(UserModel.created_at).offset(offset).limit(limit).all()

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
