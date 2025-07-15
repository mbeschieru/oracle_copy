from datetime import datetime
from uuid import UUID


class Meeting:
    """
    Represents a meeting event.
    Attendance responses (accept/decline) are handled via MeetingAttendance
    """

    def __init__(
        self,
        meeting_id: UUID,
        title: str,
        datetime: datetime,
        duration_minutes: int,
    ):
        self.meeting_id = meeting_id
        self.title = title
        self.datetime = datetime
        self.duration_minutes = duration_minutes
