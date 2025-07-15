from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from app.domain.entities.user import User


class UserRepositoryInterface(ABC):

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[User]:
        """Used for login and user lookup"""

    @abstractmethod
    def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user details by ID"""

    @abstractmethod
    def get_all_users(self) -> List[User]:
        """Get list of all users (for manager view, etc)"""
