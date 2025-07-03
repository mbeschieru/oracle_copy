from sqlalchemy import Column, String, Enum, DateTime
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from app.infrastructure.config.db_config import Base
from app.domain.enums import UserRole, UserGrade

class UserModel(Base):
    __tablename__ = "users"

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    grade = Column(Enum(UserGrade), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
