from abc import ABC, abstractmethod
from uuid import UUID
from typing import List, Optional
from app.domain.entities.timesheet import Timesheet

class TimesheetRepositoryInterface(ABC):

    @abstractmethod
    def get_by_user(self, user_id: UUID) -> List[Timesheet]:
        """Get all timesheets for a user"""
        pass

    @abstractmethod
    def get_by_id (self , timesheet_id : id ) -> Timesheet:
        """Get timesheet by id"""
        pass

    @abstractmethod
    def get_by_user_and_week(self, user_id: UUID, week_start: str) -> Optional[Timesheet]:
        """Get a specific timesheet for a given week"""
        pass

    @abstractmethod
    def save(self, timesheet: Timesheet) -> None:
        """Submit or update a timesheet"""
        pass

    @abstractmethod
    def approve(self, timesheet_id: UUID, manager_id: UUID) -> None:
        """Approve a timesheet by a manager"""
        pass
