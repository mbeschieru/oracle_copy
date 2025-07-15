from datetime import date
from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException
from pydantic import BaseModel

from app.domain.dto.timesheet_dto import (
    TimeEntryDTO,
    TimesheetCreateDTO,
    TimesheetReadDTO,
)
from app.infrastructure.dependencies import get_timesheet_service
from app.presentation.dependencies.jwt_auth import get_current_user_id
from app.use_case.services.timesheet_service import TimesheetService

router = APIRouter(prefix="/timesheets", tags=["Timesheets"])


@router.get("/user/{target_user_id}", response_model=list[TimesheetReadDTO])
def get_user_timesheets(
    target_user_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    service: TimesheetService = Depends(get_timesheet_service),
):
    return service.get_timesheets_for_user(user_id, target_user_id)


@router.get("/user/{target_user_id}/week", response_model=TimesheetReadDTO)
def get_by_week(
    target_user_id: UUID,
    week_start: date,
    user_id: UUID = Depends(get_current_user_id),
    service: TimesheetService = Depends(get_timesheet_service),
):
    return service.get_timesheet_by_week(user_id, target_user_id, week_start)


@router.post("/", response_model=dict)
def submit_timesheet(
    data: TimesheetCreateDTO,
    user_id: UUID = Depends(get_current_user_id),
    service: TimesheetService = Depends(get_timesheet_service),
):
    return service.submit_timesheet(data, user_id)


@router.get("/timesheet/{timesheet_id}", response_model=list[TimeEntryDTO])
def get_entries_for_timesheet(
    timesheet_id: UUID,
    service: TimesheetService = Depends(get_timesheet_service),
):
    timesheet = service.get_timesheet_by_id(timesheet_id)
    # Convert entries to DTOs - entries are now eagerly loaded
    return [
        TimeEntryDTO(
            day=e.day,
            hours=e.hours,
            project_id=e.project_id,
            description=e.description,
        )
        for e in timesheet.entries
    ]


class TimesheetActionDTO(BaseModel):
    description: str | None = None


@router.post("/approve/{timesheet_id}", response_model=dict)
def approve_timesheet(
    timesheet_id: UUID,
    data: TimesheetActionDTO = Body(...),
    user_id: UUID = Depends(get_current_user_id),
    service: TimesheetService = Depends(get_timesheet_service),
):
    try:
        manager = service.user_repo.get_by_id(user_id)
        if not manager:
            raise HTTPException(status_code=404, detail="Manager not found")
        description = data.description or "All ok"
        result = service.approve_timesheet(timesheet_id, manager, description)
        return result
    except Exception as e:
        from app.domain.exceptions.factory_timsheet import (
            permission_denied,
            timesheet_already_approved,
            timesheet_not_found,
        )

        if isinstance(e, type(timesheet_not_found(""))):
            raise HTTPException(status_code=404, detail=str(e))
        if isinstance(e, type(timesheet_already_approved(""))):
            raise HTTPException(status_code=409, detail=str(e))
        if isinstance(e, type(permission_denied(""))):
            raise HTTPException(status_code=403, detail=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/decline/{timesheet_id}", response_model=dict)
def decline_timesheet(
    timesheet_id: UUID,
    data: TimesheetActionDTO = Body(...),
    user_id: UUID = Depends(get_current_user_id),
    service: TimesheetService = Depends(get_timesheet_service),
):
    try:
        manager = service.user_repo.get_by_id(user_id)
        if not manager:
            raise HTTPException(status_code=404, detail="Manager not found")
        reason = data.description
        if not reason:
            raise HTTPException(
                status_code=400, detail="Decline reason is required."
            )
        result = service.decline_timesheet(timesheet_id, manager, reason)
        return result
    except Exception as e:
        from app.domain.exceptions.factory_timsheet import (
            permission_denied,
            timesheet_not_found,
        )

        if isinstance(e, type(timesheet_not_found(""))):
            raise HTTPException(status_code=404, detail=str(e))
        if isinstance(e, type(permission_denied(""))):
            raise HTTPException(status_code=403, detail=str(e))
        raise HTTPException(status_code=500, detail=str(e))
