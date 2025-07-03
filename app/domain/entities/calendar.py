from uuid import UUID
from datetime import datetime

class Meeting:
    def __init__(self, meeting_id: UUID, title: str, datetime: datetime, duration_minutes: int, created_by: UUID, project_id: UUID = None):
        self.meeting_id = meeting_id
        self.title = title
        self.datetime = datetime
        self.duration_minutes = duration_minutes
        self.created_by = created_by
        self.project_id = project_id
