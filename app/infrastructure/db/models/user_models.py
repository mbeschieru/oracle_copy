import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, ForeignKey, String
from sqlalchemy.types import CHAR

from app.domain.enums import UserGrade, UserRole
from app.infrastructure.config.db_config import Base


class UserModel(Base):
    __tablename__ = "users"

    user_id = Column(
        CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(
        String(255), nullable=False
    )  # Add password hash field
    role = Column(Enum(UserRole), nullable=False)
    grade = Column(Enum(UserGrade), nullable=False)
    created_at = Column(DateTime, default=datetime.now())
    project_id = Column(
        CHAR(36), ForeignKey("projects.project_id"), nullable=True
    )
