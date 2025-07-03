from uuid import UUID
from datetime import date

class Absence:
    def __init__(self, absence_id: UUID, user_id: UUID, start_date: date, end_date: date, reason: str):
        self.absence_id = absence_id
        self.user_id = user_id
        self.start_date = start_date
        self.end_date = end_date
        self.reason = reason
