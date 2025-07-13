from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from typing import List

from app.domain.dto.meeting_attendance_dto import (
    MeetingAttendanceCreateDTO, MeetingAttendanceReadDTO
)
from app.domain.enums.enums import AttendanceResponse
from app.use_case.services.meeting_attendance_service import MeetingAttendanceService
from app.infrastructure.dependencies import get_meeting_attendance_service
from app.presentation.dependencies.jwt_auth import get_current_user, get_current_user_id

router = APIRouter(prefix="/attendance", tags=["meeting-attendance"])

@router.post("/", response_model=MeetingAttendanceReadDTO, status_code=status.HTTP_201_CREATED)
def create_attendance(
    payload: MeetingAttendanceCreateDTO,
    user_id: UUID = Depends(get_current_user_id),
    svc: MeetingAttendanceService = Depends(get_meeting_attendance_service),
):
    return svc.create(payload, user_id)

@router.patch("/{attendance_id}", response_model=MeetingAttendanceReadDTO)
def respond_to_attendance(
    attendance_id: UUID,
    status: AttendanceResponse,
    svc: MeetingAttendanceService = Depends(get_meeting_attendance_service),
):
    updated = svc.respond(attendance_id, status)
    if not updated:
        raise HTTPException(status_code=404, detail="Attendance not found")
    return updated

@router.get("/meeting/{meeting_id}", response_model=List[MeetingAttendanceReadDTO])
def list_attendance(
    meeting_id: UUID,
    svc: MeetingAttendanceService = Depends(get_meeting_attendance_service),
):
    return svc.list_for_meeting(meeting_id)
