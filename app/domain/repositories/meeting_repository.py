from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from app.domain.entities.calendar import Meeting


class MeetingRepositoryInterface(ABC):

    @abstractmethod
    def get_all_meetings(self) -> List[Meeting]:
        """Get all meetings"""

    @abstractmethod
    def get_meeting_by_id(self, meeting_id: UUID) -> Optional[Meeting]:
        """Get meeting by ID"""

    @abstractmethod
    def get_meetings_for_user(self, user_id: UUID) -> List[Meeting]:
        """Get meetings for a specific user"""

    @abstractmethod
    def create_meeting(self, meeting: Meeting) -> None:
        """Create a new meeting"""
