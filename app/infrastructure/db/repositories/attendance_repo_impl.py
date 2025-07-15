from datetime import date
from typing import List, Optional, Tuple
from uuid import UUID

from app.domain.entities.attendance import Attendance
from app.domain.repositories.attendance_repository import (
    AttendanceRepositoryInterface,
)
from app.infrastructure.config.db_config import SessionLocal
from app.infrastructure.db.models.attendance_models import AttendanceModel
from app.infrastructure.db.models.user_models import UserModel


class AttendanceRepository(AttendanceRepositoryInterface):
    """
    Handles time tracking attendance, not meeting accept/decline responses.
    MeetingAttendanceRepository handles meeting responses.
    """

    def __init__(self):
        pass  # Don't create session in constructor

    def _get_session(self):
        """Get a new database session"""
        return SessionLocal()

    def get_attendance_for_user(self, user_id: UUID) -> List[Attendance]:
        """Get attendance logs for a specific user"""
        db = self._get_session()
        try:
            attendances = (
                db.query(AttendanceModel)
                .filter(AttendanceModel.user_id == str(user_id))
                .all()
            )

            return [
                Attendance(
                    attendance_id=UUID(attendance.attendance_id),
                    meeting_id=UUID(attendance.meeting_id),
                    user_id=UUID(attendance.user_id),
                    day=attendance.day,
                    check_in=attendance.check_in,
                    check_out=attendance.check_out,
                    time_spent=attendance.time_spent,
                )
                for attendance in attendances
            ]
        finally:
            db.close()

    def get_by_day(self, user_id: UUID, day: date) -> Optional[Attendance]:
        """Retrieve attendance for a particular day"""
        db = self._get_session()
        try:
            attendance = (
                db.query(AttendanceModel)
                .filter(
                    AttendanceModel.user_id == str(user_id),
                    AttendanceModel.day == day,
                )
                .first()
            )

            if not attendance:
                return None

            return Attendance(
                attendance_id=UUID(attendance.attendance_id),
                meeting_id=UUID(attendance.meeting_id),
                user_id=UUID(attendance.user_id),
                day=attendance.day,
                check_in=attendance.check_in,
                check_out=attendance.check_out,
                time_spent=attendance.time_spent,
            )
        finally:
            db.close()

    def get_attendance_for_meeting(
        self, meeting_id: UUID, page: int = 1, page_size: int = 10
    ) -> Tuple[List[dict], int]:
        """Get paginated attendance for a specific meeting with user details"""
        db = self._get_session()
        try:
            offset = (page - 1) * page_size

            # Get total count
            total_count = (
                db.query(AttendanceModel)
                .filter(AttendanceModel.meeting_id == str(meeting_id))
                .count()
            )

            # Get paginated attendance with user details
            # SQL Server requires ORDER BY when using OFFSET and LIMIT
            attendances = (
                db.query(AttendanceModel)
                .filter(AttendanceModel.meeting_id == str(meeting_id))
                .order_by(AttendanceModel.attendance_id)
                .offset(offset)
                .limit(page_size)
                .all()
            )

            # Return attendance data with user details for DTO conversion
            attendance_data = []
            for attendance in attendances:
                # Get user details separately to handle
                # potential relationship issues
                user = (
                    db.query(UserModel)
                    .filter(UserModel.user_id == attendance.user_id)
                    .first()
                )
                user_name = user.name if user else "Unknown User"
                user_email = user.email if user else "unknown@email.com"

                attendance_data.append(
                    {
                        "attendance_id": UUID(attendance.attendance_id),
                        "meeting_id": UUID(attendance.meeting_id),
                        "user_id": UUID(attendance.user_id),
                        "user_name": user_name,
                        "user_email": user_email,
                        "day": attendance.day,
                        "check_in": attendance.check_in,
                        "check_out": attendance.check_out,
                        "time_spent": attendance.time_spent,
                    }
                )

            return attendance_data, total_count

        except Exception as e:
            # Log the error for debugging
            print(f"Error in get_attendance_for_meeting: {str(e)}")
            # Return empty result instead of crashing
            return [], 0
        finally:
            db.close()

    def get_attendance_count_for_meeting(self, meeting_id: UUID) -> int:
        """Get total attendance count for a meeting"""
        db = self._get_session()
        try:
            return (
                db.query(AttendanceModel)
                .filter(AttendanceModel.meeting_id == str(meeting_id))
                .count()
            )
        except Exception as e:
            print(f"Error in get_attendance_count_for_meeting: {str(e)}")
            return 0
        finally:
            db.close()

    def create_attendance(self, attendance: Attendance) -> None:
        """Create a new attendance record"""
        db = self._get_session()
        try:
            attendance_model = AttendanceModel(
                attendance_id=str(attendance.attendance_id),
                meeting_id=str(attendance.meeting_id),
                user_id=str(attendance.user_id),
                day=attendance.day,
                check_in=attendance.check_in,
                check_out=attendance.check_out,
                time_spent=attendance.time_spent,
            )
            db.add(attendance_model)
            db.commit()
        except Exception as e:
            db.rollback()
            print(f"Error in create_attendance: {str(e)}")
            raise
        finally:
            db.close()
