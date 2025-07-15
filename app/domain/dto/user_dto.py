from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr

from app.domain.enums import UserGrade, UserRole


class UserCreateDTO(BaseModel):
    name: str
    email: EmailStr
    role: UserRole
    grade: UserGrade


class UserLoginDTO(BaseModel):
    email: EmailStr
    password: str


class UserReadDTO(BaseModel):
    user_id: UUID
    name: str
    email: EmailStr
    role: UserRole
    grade: UserGrade
    created_at: datetime
    project_id: UUID | None = None
    model_config = ConfigDict(from_attributes=True)


class UserWithTokenDTO(BaseModel):
    user: UserReadDTO
    access_token: str
    token_type: str = "bearer"
