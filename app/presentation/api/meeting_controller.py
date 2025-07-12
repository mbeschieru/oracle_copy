from fastapi import APIRouter, Depends, HTTPException, Query
from uuid import UUID
from typing import List
from app.domain.dto.meeting_dto import MeetingReadDTO, PaginatedAttendanceDTO
from app.use_case.services.meeting_service import MeetingService
from app.infrastructure.dependencies import get_meeting_service
from app.presentation.dependencies.jwt_auth import get_current_user_id

router = APIRouter(prefix="/meetings", tags=["meetings"])

@router.get("/", response_model=List[MeetingReadDTO])
async def get_all_meetings(
    user_id: UUID = Depends(get_current_user_id),
    meeting_service: MeetingService = Depends(get_meeting_service)
):
    """Get all meetings for dropdown selection"""
    try:
        meetings = meeting_service.get_all_meetings()
        return meetings
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching meetings: {str(e)}")

@router.get("/{meeting_id}", response_model=MeetingReadDTO)
async def get_meeting_by_id(
    meeting_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    meeting_service: MeetingService = Depends(get_meeting_service)
):
    """Get meeting details by ID"""
    try:
        meeting = meeting_service.get_meeting_by_id(meeting_id)
        if not meeting:
            raise HTTPException(status_code=404, detail="Meeting not found")
        return meeting
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching meeting: {str(e)}")

@router.get("/{meeting_id}/attendance", response_model=PaginatedAttendanceDTO)
async def get_meeting_attendance(
    meeting_id: UUID,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    user_id: UUID = Depends(get_current_user_id),
    meeting_service: MeetingService = Depends(get_meeting_service)
):
    """Get paginated attendance for a specific meeting"""
    try:
        attendance = meeting_service.get_meeting_attendance(meeting_id, page, page_size)
        return attendance
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching attendance: {str(e)}") 