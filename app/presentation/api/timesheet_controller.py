from fastapi import APIRouter, Depends, HTTPException, Header
from uuid import UUID
from datetime import date
from app.domain.dto.timesheet_dto import TimesheetCreateDTO, TimesheetReadDTO
from app.use_case.services.timesheet_service import TimesheetService
from app.infrastructure.dependencies import get_timesheet_service
from app.domain.exceptions.factory_timsheet import timesheet_not_found
from app.use_case.validators.user_identity import assert_user_identity_matches
from app.domain.dto.timesheet_dto import TimeEntryDTO


router = APIRouter(prefix="/timesheets", tags=["Timesheets"])

@router.get("/user/{target_user_id}", response_model=list[TimesheetReadDTO])
def get_user_timesheets(target_user_id: UUID, x_user_id: str = Header(...), service: TimesheetService = Depends(get_timesheet_service)):
   return service.get_timesheets_for_user(UUID(x_user_id), target_user_id)

@router.get("/user/{target_user_id}/week", response_model=TimesheetReadDTO)
def get_by_week(
    target_user_id: UUID,
    week_start: date,
    x_user_id: str = Header(...),
    service: TimesheetService = Depends(get_timesheet_service)
):
    return service.get_timesheet_by_week(UUID(x_user_id), target_user_id, week_start)


@router.post("/", response_model=dict)
def submit_timesheet(
    data: TimesheetCreateDTO,
    x_user_id: str = Header(..., description="User ID passed from frontend"),
    service: TimesheetService = Depends(get_timesheet_service)
):
     return service.submit_timesheet(data, UUID(x_user_id))


@router.get("/timesheet/{timesheet_id}", response_model= list[TimeEntryDTO])
def get_entries_for_timesheet(
    timesheet_id: UUID,
    service : TimesheetService = Depends(get_timesheet_service)
):
    return [TimeEntryDTO.from_orm(e) for e in service.get_timesheet_by_id(timesheet_id)]