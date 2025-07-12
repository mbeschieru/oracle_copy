from abc import ABC, abstractmethod
from uuid import UUID
from datetime import datetime
from typing import List, Optional
from app.domain.entities.calendar import Meeting

class MeetingRepositoryInterface(ABC):

    @abstractmethod
    def get_all_meetings(self) -> List[Meeting]:
        """Get all meetings"""
        pass

    @abstractmethod
    def get_meeting_by_id(self, meeting_id: UUID) -> Optional[Meeting]:
        """Get meeting by ID"""
        pass

    @abstractmethod
    def get_meetings_for_user(self, user_id: UUID) -> List[Meeting]:
        """Get meetings for a specific user"""
        pass

    @abstractmethod
    def create_meeting(self, meeting: Meeting) -> None:
        """Create a new meeting"""
        pass
