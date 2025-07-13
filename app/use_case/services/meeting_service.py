from uuid import UUID
from typing import List, Optional
from app.domain.repositories.meeting_repository import MeetingRepositoryInterface
from app.domain.repositories.attendance_repository import AttendanceRepositoryInterface
from app.domain.entities.calendar import Meeting
from app.domain.entities.user import User
from app.use_case.validators.role_validator import require_manager
from app.domain.dto.meeting_dto import MeetingReadDTO, AttendanceReadDTO, PaginatedAttendanceDTO, MeetingCreateDTO
import math
import uuid

class MeetingService:

    def __init__(self, meeting_repo: MeetingRepositoryInterface, attendance_repo: AttendanceRepositoryInterface):
        self.meeting_repo = meeting_repo
        self.attendance_repo = attendance_repo

    def get_all_meetings(self) -> List[MeetingReadDTO]:
        """Get all meetings for dropdown selection"""
        meetings = self.meeting_repo.get_all_meetings()
        return [
            MeetingReadDTO(
                meeting_id=meeting.meeting_id,
                title=meeting.title,
                datetime=meeting.datetime,
                duration_minutes=meeting.duration_minutes
            )
            for meeting in meetings
        ]

    def get_meeting_by_id(self, meeting_id: UUID) -> Optional[MeetingReadDTO]:
        """Get meeting details by ID"""
        meeting = self.meeting_repo.get_meeting_by_id(meeting_id)
        if not meeting:
            return None
        
        return MeetingReadDTO(
            meeting_id=meeting.meeting_id,
            title=meeting.title,
            datetime=meeting.datetime,
            duration_minutes=meeting.duration_minutes
        )

    def get_meeting_attendance(self, meeting_id: UUID, page: int = 1, page_size: int = 10) -> PaginatedAttendanceDTO:
        """Get paginated attendance for a specific meeting"""
        # Validate meeting exists
        meeting = self.meeting_repo.get_meeting_by_id(meeting_id)
        if not meeting:
            raise ValueError(f"Meeting with ID {meeting_id} not found")
        
        # Get paginated attendance data
        attendance_data, total_count = self.attendance_repo.get_attendance_for_meeting(
            meeting_id, page, page_size
        )
        
        # Convert to DTOs
        attendance_dtos = [
            AttendanceReadDTO(
                attendance_id=data['attendance_id'],
                meeting_id=data['meeting_id'],
                user_id=data['user_id'],
                user_name=data['user_name'],
                user_email=data['user_email'],
                day=data['day'],
                check_in=data['check_in'],
                check_out=data['check_out'],
                time_spent=data['time_spent']
            )
            for data in attendance_data
        ]
        
        # Calculate pagination info
        total_pages = math.ceil(total_count / page_size)
        has_next = page < total_pages
        has_previous = page > 1
        
        return PaginatedAttendanceDTO(
            attendances=attendance_dtos,
            total_count=total_count,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            has_next=has_next,
            has_previous=has_previous
        )

    def get_user_meetings(self, user_id: UUID):
        """Get meetings for a specific user"""
        return self.meeting_repo.get_meetings_for_user(user_id)

    def create_meeting(self, data: MeetingCreateDTO, user_id: UUID):
        """Create a new meeting"""
        from app.domain.repositories.user_repository import UserRepositoryInterface
        from app.infrastructure.db.repositories.user_repo_impl import UserRepository
        user_repo: UserRepositoryInterface = UserRepository()
        user = user_repo.get_by_id(user_id)
        print(f"[DEBUG] Creating meeting as user: {user.email}, role: {user.role}")
        require_manager(user)
        meeting = Meeting(
            meeting_id=uuid.uuid4(),  # generate new UUID
            title=data.title,
            datetime=data.datetime,
            duration_minutes=data.duration_minutes
        )
        self.meeting_repo.create_meeting(meeting)
        return {"status": "created"}
