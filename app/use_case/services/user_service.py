from uuid import UUID

from app.domain.dto.user_dto import UserReadDTO, UserWithTokenDTO
from app.domain.repositories.user_repository import UserRepositoryInterface


class UserService:

    def __init__(self, user_repo: UserRepositoryInterface):
        self.user_repo = user_repo

    def login_by_email_and_password(
        self, email: str, password: str
    ) -> UserWithTokenDTO:
        """Login user with email and password, return JWT token"""
        user = self.user_repo.authenticate_user(email, password)
        if not user:
            raise ValueError("Invalid email or password")

        # Create JWT token
        access_token = self.user_repo.create_jwt_token(user)

        # Convert to DTO
        user_dto = UserReadDTO(
            user_id=UUID(user.user_id),
            name=user.name,
            email=user.email,
            role=user.role,
            grade=user.grade,
            created_at=user.created_at,
            project_id=UUID(user.project_id) if user.project_id else None,
        )

        return UserWithTokenDTO(
            user=user_dto, access_token=access_token, token_type="bearer"
        )

    def login_by_email(self, email: str) -> UserReadDTO:
        """Legacy login method for backward compatibility"""
        user = self.user_repo.get_by_email(email)
        if not user:
            raise ValueError("User not found")

        return UserReadDTO(
            user_id=UUID(user.user_id),
            name=user.name,
            email=user.email,
            role=user.role,
            grade=user.grade,
            created_at=user.created_at,
            project_id=UUID(user.project_id) if user.project_id else None,
        )

    def get_user_details(self, user_id: UUID) -> UserReadDTO:
        """Get user details by ID"""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return None

        return UserReadDTO(
            user_id=UUID(user.user_id),
            name=user.name,
            email=user.email,
            role=user.role,
            grade=user.grade,
            created_at=user.created_at,
            project_id=UUID(user.project_id) if user.project_id else None,
        )

    def get_all_users(self, offset=0, limit=10):
        """Get all users with pagination"""
        users = self.user_repo.get_all_users(offset, limit)
        return [
            UserReadDTO(
                user_id=UUID(user.user_id),
                name=user.name,
                email=user.email,
                role=user.role,
                grade=user.grade,
                created_at=user.created_at,
                project_id=UUID(user.project_id) if user.project_id else None,
            )
            for user in users
        ]

    def get_users_by_project(self, project_id: str, offset=0, limit=10):
        """Get users by project with pagination"""
        users = self.user_repo.get_users_by_project(project_id, offset, limit)
        return [
            UserReadDTO(
                user_id=UUID(user.user_id),
                name=user.name,
                email=user.email,
                role=user.role,
                grade=user.grade,
                created_at=user.created_at,
                project_id=UUID(user.project_id) if user.project_id else None,
            )
            for user in users
        ]
