from uuid import UUID
from datetime import date
from typing import List

class Absence:
    def __init__(self, absence_id: UUID, user_id: UUID, week_start: date, days: List[date], reason: str, status: str = 'pending', status_description: str = None):
        self.absence_id = absence_id
        self.user_id = user_id
        self.week_start = week_start
        self.days = days
        self.reason = reason
        self.status = status
        self.status_description = status_description
