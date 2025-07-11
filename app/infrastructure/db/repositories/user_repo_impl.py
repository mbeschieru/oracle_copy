from uuid import UUID
from app.domain.repositories.user_repository import UserRepositoryInterface
from app.infrastructure.config.db_config import SessionLocal
from app.infrastructure.db.models.user_models import UserModel

class UserRepository(UserRepositoryInterface):

    def __init__(self):
        self.db = SessionLocal()

    def get_by_email(self, email: str):
        return self.db.query(UserModel).filter(UserModel.email == email).first()

    def get_by_id(self, user_id: UUID):
        return self.db.query(UserModel).filter(UserModel.user_id == user_id).first()

    def get_all_users(self, offset=0, limit=10):
        return self.db.query(UserModel).order_by(UserModel.created_at).offset(offset).limit(limit).all()

    def get_users_by_project(self, project_id, offset=0, limit=10):
        return self.db.query(UserModel).filter(UserModel.project_id == project_id, UserModel.role != 'manager').order_by(UserModel.created_at).offset(offset).limit(limit).all()
