from app.domain.repositories.user_repository import UserRepositoryInterface
from app.infrastructure.config.db_config import SessionLocal
from app.infrastructure.db.models.user_models import UserModel

class UserRepository(UserRepositoryInterface):

    def __init__(self):
        self.db = SessionLocal()

    def get_by_email(self, email: str):
        return self.db.query(UserModel).filter(UserModel.email == email).first()

    def get_by_id(self, user_id):
        return self.db.query(UserModel).filter(UserModel.user_id == user_id).first()

    def get_all_users(self):
        return self.db.query(UserModel).all()
