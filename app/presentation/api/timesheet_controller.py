from fastapi import APIRouter, Depends, HTTPException,Header
from uuid import UUID
from datetime import date
from app.domain.dto.timesheet_dto import TimesheetCreateDTO, TimesheetReadDTO
from app.use_case.services.timesheet_service import TimesheetService
from app.infrastructure.dependencies import get_timesheet_service
from app.domain.exceptions.factory_timsheet import timesheet_not_found
from app.use_case.validators.user_identity import assert_user_identity_matches


router = APIRouter(prefix="/timesheets", tags=["Timesheets"])

@router.get("/user/{user_id}", response_model=list[TimesheetReadDTO])
def get_user_timesheets(user_id: UUID, service: TimesheetService = Depends(get_timesheet_service)):
    try:
        timesheets = service.get_timesheets_for_user(user_id)
        return [TimesheetReadDTO.from_orm(ts) for ts in timesheets]
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/user/{user_id}/week", response_model=TimesheetReadDTO)
def get_timesheet_week(user_id: UUID, week_start: date, service: TimesheetService = Depends(get_timesheet_service)):
    try:
        timesheet = service.get_timesheet_by_week(user_id, week_start)
        return TimesheetReadDTO.from_orm(timesheet)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/", response_model=dict)
def submit_timesheet(
    data: TimesheetCreateDTO,
    x_user_id : str = Header(..., description = "User ID passed fron frontend"),
    service: TimesheetService = Depends(get_timesheet_service)):
    try:
        assert_user_identity_matches(data.user_id, x_user_id)
        return service.submit_timesheet(data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
