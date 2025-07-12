from fastapi import APIRouter, Depends, HTTPException, Query
from uuid import UUID
from app.domain.dto.user_dto import UserLoginDTO, UserReadDTO, UserWithTokenDTO
from app.use_case.services.user_service import UserService
from app.infrastructure.dependencies import get_user_service
from app.presentation.dependencies.jwt_auth import get_current_user, get_current_user_id

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/login", response_model=UserWithTokenDTO)
def login(data: UserLoginDTO, service: UserService = Depends(get_user_service)):
    """Login with email and password, return JWT token"""
    try:
        result = service.login_by_email_and_password(data.email, data.password)
        return result
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

@router.get("/me", response_model=UserReadDTO)
def get_current_user_info(current_user = Depends(get_current_user)):
    """Get current user information from JWT token"""
    return UserReadDTO(
        user_id=UUID(current_user.user_id),
        name=current_user.name,
        email=current_user.email,
        role=current_user.role,
        grade=current_user.grade,
        created_at=current_user.created_at,
        project_id=UUID(current_user.project_id) if current_user.project_id else None
    )

@router.get("/{user_id}", response_model=UserReadDTO)
def get_user(user_id: UUID, service: UserService = Depends(get_user_service)):
    """Get user details by ID"""
    user = service.get_user_details(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/", response_model=list[UserReadDTO])
def get_all(
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    service: UserService = Depends(get_user_service)
):
    """Get all users with pagination"""
    return service.get_all_users(offset=offset, limit=limit)

@router.get("/by_project/{project_id}", response_model=list[UserReadDTO])
def get_users_by_project(
    project_id: str,
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    service: UserService = Depends(get_user_service)
):
    """Get users by project with pagination"""
    return service.get_users_by_project(project_id, offset=offset, limit=limit)
