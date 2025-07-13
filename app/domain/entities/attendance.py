from uuid import UUID
from datetime import date, time

class Attendance:
    def __init__(self, attendance_id: UUID, meeting_id: UUID, user_id: UUID, day: date, check_in: time, check_out: time, time_spent: int):
        self.attendance_id = attendance_id
        self.meeting_id = meeting_id
        self.user_id = user_id
        self.day = day
        self.check_in = check_in
        self.check_out = check_out
        self.time_spent = time_spent
