import uuid

from sqlalchemy import Column, String
from sqlalchemy.types import CHAR

from app.infrastructure.config.db_config import Base


class ProjectModel(Base):
    __tablename__ = "projects"

    project_id = Column(
        CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name = Column(String(100), nullable=False)
    description = Column(String(300))
    manager_id = Column(CHAR(36), nullable=True)
