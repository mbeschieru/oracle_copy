from sqlalchemy import Column, String, Enum, DateTime,ForeignKey
from sqlalchemy.types import CHAR
from datetime import datetime
import uuid
from app.infrastructure.config.db_config import Base
from app.domain.enums import UserRole, UserGrade

class UserModel(Base):
    __tablename__ = "users"

    user_id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    grade = Column(Enum(UserGrade), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    project_id = Column(CHAR(36), ForeignKey("projects.project_id"), nullable = False)