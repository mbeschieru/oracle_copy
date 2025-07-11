from fastapi import APIRouter, Depends, HTTPException, Body
from uuid import UUID
from datetime import date
from app.domain.dto.absence_dto import AbsenceCreateDTO, AbsenceReadDTO
from app.use_case.services.absence_service import AbsenceService
from app.infrastructure.dependencies import get_absence_service, get_user_service
from app.presentation.dependencies.header_user import get_authenticated_user_id
from pydantic import BaseModel

router = APIRouter(prefix="/absences", tags=["Absences"])

class AbsenceActionDTO(BaseModel):
    description: str | None = None

@router.post("/", response_model=dict)
def create_absence(
    data: AbsenceCreateDTO,
    user_id: UUID = Depends(get_authenticated_user_id),
    service: AbsenceService = Depends(get_absence_service)
):
    return service.create_absence(data, user_id)

@router.get("/", response_model=list[AbsenceReadDTO])
def get_user_absences(
    user_id: UUID = Depends(get_authenticated_user_id),
    service: AbsenceService = Depends(get_absence_service)
):
    return service.get_user_absences(user_id)

@router.get("/week", response_model=AbsenceReadDTO)
def get_absence_by_week(
    week_start: date,
    user_id: UUID = Depends(get_authenticated_user_id),
    service: AbsenceService = Depends(get_absence_service)
):
    return service.get_absence_by_week(user_id, week_start)

@router.get("/project/{project_id}/week", response_model=list[AbsenceReadDTO])
def get_project_absences_by_week(
    project_id: UUID,
    week_start: date,
    service: AbsenceService = Depends(get_absence_service)
):
    return service.get_project_absences_by_week(project_id, week_start)

@router.post("/approve/{absence_id}", response_model=dict)
def approve_absence(
    absence_id: UUID,
    data: AbsenceActionDTO = Body(...),
    user_id: UUID = Depends(get_authenticated_user_id),
    service: AbsenceService = Depends(get_absence_service)
):
    description = data.description or "All ok"
    return service.approve_absence(absence_id, user_id, description)

@router.post("/decline/{absence_id}", response_model=dict)
def decline_absence(
    absence_id: UUID,
    data: AbsenceActionDTO = Body(...),
    user_id: UUID = Depends(get_authenticated_user_id),
    service: AbsenceService = Depends(get_absence_service)
):
    if not data.description:
        raise HTTPException(status_code=400, detail="Decline reason is required.")
    return service.decline_absence(absence_id, user_id, data.description) 