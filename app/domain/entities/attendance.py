from uuid import UUID
from datetime import date, time

class Attendance:
    def __init__(self, attendance_id: UUID, user_id: UUID, day: date, check_in: time, check_out: time):
        self.attendance_id = attendance_id
        self.user_id = user_id
        self.day = day
        self.check_in = check_in
        self.check_out = check_out
