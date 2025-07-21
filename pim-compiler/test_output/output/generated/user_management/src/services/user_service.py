"""
Business Logic for User Management.

This module contains the service layer for user-related operations.
It encapsulates the business logic and separates it from the API layer.
All database interactions for the User model are handled here.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status

from ..models.user import User
from ..schemas.user import UserCreate
from ..core.security import get_password_hash, verify_password


class UserService:
    """
    Service class for user-related business logic.
    """

    async def create_user(self, db: AsyncSession, user_in: UserCreate) -> User:
        """
        Creates a new user in the database.

        Args:
            db: The database session.
            user_in: The user creation data.

        Returns:
            The newly created user object.

        Raises:
            HTTPException: If the email or username already exists.
        """
        # Check for existing email
        stmt_email = select(User).where(User.email == user_in.email)
        existing_user_email = (await db.execute(stmt_email)).scalars().first()
        if existing_user_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this email already exists.",
            )

        # Check for existing username
        stmt_username = select(User).where(User.username == user_in.username)
        existing_user_username = (await db.execute(stmt_username)).scalars().first()
        if existing_user_username:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This username is already taken.",
            )

        hashed_password = get_password_hash(user_in.password)
        db_user = User(
            username=user_in.username,
            email=user_in.email,
            hashed_password=hashed_password,
        )

        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user

    async def authenticate_user(
        self, db: AsyncSession, username: str, password: str
    ) -> User | None:
        """
        Authenticates a user by username and password.

        Args:
            db: The database session.
            username: The username or email for authentication.
            password: The user's password.

        Returns:
            The authenticated user object, or None if authentication fails.
        """
        user = await self.get_user_by_username_or_email(db, username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    async def get_user_by_id(self, db: AsyncSession, user_id: int) -> User | None:
        """
        Retrieves a user by their ID.

        Args:
            db: The database session.
            user_id: The ID of the user to retrieve.

        Returns:
            The user object, or None if not found.
        """
        stmt = select(User).where(User.id == user_id)
        return (await db.execute(stmt)).scalars().first()

    async def get_user_by_username(self, db: AsyncSession, username: str) -> User | None:
        """
        Retrieves a user by their username.

        Args:
            db: The database session.
            username: The username to search for.

        Returns:
            The user object, or None if not found.
        """
        stmt = select(User).where(User.username == username)
        return (await db.execute(stmt)).scalars().first()
        
    async def get_user_by_username_or_email(self, db: AsyncSession, identifier: str) -> User | None:
        """
        Retrieves a user by their username or email.

        Args:
            db: The database session.
            identifier: The username or email to search for.

        Returns:
            The user object, or None if not found.
        """
        stmt = select(User).where((User.username == identifier) | (User.email == identifier))
        return (await db.execute(stmt)).scalars().first()


user_service = UserService()
