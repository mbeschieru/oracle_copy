from enum import Enum

class UserRole (str,Enum) :
    EMPLOYEE = "employee"
    MANAGER = "manager"

class UserGrade (str,Enum):
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"