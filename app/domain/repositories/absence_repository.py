from abc import ABC, abstractmethod
from uuid import UUID
from datetime import date
from typing import List, Optional
from app.domain.entities.absence import Absence

class AbsenceRepositoryInterface(ABC):
    @abstractmethod
    def get_by_user(self, user_id: UUID) -> List[Absence]:
        pass

    @abstractmethod
    def get_by_id(self, absence_id: UUID) -> Optional[Absence]:
        pass

    @abstractmethod
    def get_by_week(self, user_id: UUID, week_start: date) -> Optional[Absence]:
        pass

    @abstractmethod
    def save(self, absence: Absence) -> None:
        pass

    @abstractmethod
    def approve(self, absence_id: UUID, manager_id: UUID, description: str) -> None:
        pass

    @abstractmethod
    def decline(self, absence_id: UUID, manager_id: UUID, reason: str) -> None:
        pass

    @abstractmethod
    def get_by_project_and_week(self, project_id: UUID, week_start: date) -> List[Absence]:
        pass 