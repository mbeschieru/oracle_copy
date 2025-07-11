from fastapi import APIRouter, Depends, HTTPException, Query
from uuid import UUID
from app.domain.dto.user_dto import UserLoginDTO, UserReadDTO
from app.use_case.services.user_service import UserService
from app.infrastructure.dependencies import get_user_service  # we'll define this
from app.domain.exceptions.factory_user import user_not_found
from app.presentation.dependencies.header_user import get_authenticated_user_id


router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/login", response_model=UserReadDTO)
def login(data: UserLoginDTO, service: UserService = Depends(get_user_service)):
    try:
        user = service.login_by_email(data.email)
        return UserReadDTO.from_orm(user)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/{user_id}", response_model=UserReadDTO)
def get_user(user_id: UUID, service: UserService = Depends(get_user_service)):

    user = service.get_user_details(user_id)
    if not user:
        raise HTTPException(**user_not_found(str(user_id)).__dict__)
    return UserReadDTO.from_orm(user)


@router.get("/", response_model=list[UserReadDTO])
def get_all(
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    service: UserService = Depends(get_user_service)
):
    return [UserReadDTO.from_orm(u) for u in service.get_all_users(offset=offset, limit=limit)]

@router.get("/by_project/{project_id}", response_model=list[UserReadDTO])
def get_users_by_project(
    project_id: str,
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    service: UserService = Depends(get_user_service)
):
    return [UserReadDTO.from_orm(u) for u in service.get_users_by_project(project_id, offset=offset, limit=limit)]
