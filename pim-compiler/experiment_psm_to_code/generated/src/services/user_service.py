from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError

from src.models.user import User
from src.schemas.user import UserCreate
from src.services.security import get_password_hash

class UserService:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Retrieves a user by their ID."""
        result = await self.db.execute(select(User).filter(User.id == user_id))
        return result.scalars().first()

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Retrieves a user by their email."""
        result = await self.db.execute(select(User).filter(User.email == email))
        return result.scalars().first()

    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Retrieves a user by their username."""
        result = await self.db.execute(select(User).filter(User.username == username))
        return result.scalars().first()

    async def create_user(self, user_data: UserCreate) -> User:
        """Creates a new user."""
        # Check for existing email or username
        if await self.get_user_by_email(user_data.email):
            raise IntegrityError("Email already registered", params=None, orig=None)
        if await self.get_user_by_username(user_data.username):
            raise IntegrityError("Username already taken", params=None, orig=None)

        hashed_password = get_password_hash(user_data.password)
        
        new_user = User(
            email=user_data.email,
            username=user_data.username,
            password_hash=hashed_password
        )
        
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        
        return new_user
