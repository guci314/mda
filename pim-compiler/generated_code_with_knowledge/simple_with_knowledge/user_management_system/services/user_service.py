from typing import List, Optional

from fastapi import Depends
from sqlalchemy.orm import Session

from schemas.user import UserCreate, UserResponse, UserUpdate
from repositories.user_repository import UserRepository
from database.database import get_db

class UserService:
    def __init__(self, db: Session = Depends(get_db)):
        self.user_repository = UserRepository(db)

    def create_user(self, user: UserCreate) -> UserResponse:
        db_user = self.user_repository.create_user(user)
        return UserResponse.from_orm(db_user)

    def get_users(self, skip: int = 0, limit: int = 100) -> List[UserResponse]:
        users = self.user_repository.get_users(skip, limit)
        return [UserResponse.from_orm(user) for user in users]

    def get_user(self, user_id: int) -> Optional[UserResponse]:
        db_user = self.user_repository.get_user(user_id)
        return UserResponse.from_orm(db_user) if db_user else None

    def update_user(self, user_id: int, user: UserUpdate) -> Optional[UserResponse]:
        db_user = self.user_repository.update_user(user_id, user)
        return UserResponse.from_orm(db_user) if db_user else None

    def delete_user(self, user_id: int) -> Optional[UserResponse]:
        db_user = self.user_repository.delete_user(user_id)
        return UserResponse.from_orm(db_user) if db_user else None