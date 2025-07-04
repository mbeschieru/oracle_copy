from uuid import UUID
from datetime import datetime
from app.domain.enums import UserRole , UserGrade

class User :
    def __init__(self, user_id : UUID, name: str , email: str, role: UserRole, grade: UserGrade, created_at : datetime, project_id : UUID):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.role = role
        self.grade = grade
        self.project_id = project_id
        self.created_at = created_at