from pydantic import BaseModel, EmailStr, ConfigDict
from uuid import UUID
from datetime import datetime
from app.domain.enums import UserRole, UserGrade

class UserCreateDTO(BaseModel):
    name: str
    email: EmailStr
    role: UserRole
    grade: UserGrade

class UserReadDTO(BaseModel):
    user_id: UUID
    name: str
    email: EmailStr
    role: UserRole
    grade: UserGrade
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class UserLoginDTO(BaseModel):
    email: EmailStr
