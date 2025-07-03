from uuid import UUID
from datetime import date
from typing import List

class TimeEntry:
    def __init__(self, day: date, hours: float, project_id: UUID, description: str):
        self.day = day
        self.hours = hours
        self.project_id = project_id
        self.description = description

class Timesheet:
    def __init__(self, timesheet_id: UUID, user_id: UUID, week_start: date, entries: List[TimeEntry], approved: bool = False):
        self.timesheet_id = timesheet_id
        self.user_id = user_id
        self.week_start = week_start
        self.entries = entries
        self.approved = approved
