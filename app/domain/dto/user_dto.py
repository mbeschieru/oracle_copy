from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime
from app.domain.enums import UserRole, UserGrade

class UserCreateDTO(BaseModel):
    name: str
    email: EmailStr
    role: UserRole
    grade: UserGrade

class UserReadDTO(BaseModel):
    name: str
    email: EmailStr
    role: UserRole
    grade: UserGrade
    created_at: datetime
    project_id : UUID

    class Config:
        orm_mode = True

class UserLoginDTO(BaseModel):
    email: EmailStr
