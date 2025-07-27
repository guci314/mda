from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from ..models.user import User
from ..schemas.user import UserCreate, UserUpdate, UserInDB, UserStatus
import uuid
from datetime import datetime


class UserService:
    def __init__(self, db: Session):
        self.db = db

    async def register_user(self, user_create: UserCreate) -> User:
        # Check email uniqueness
        if self.db.query(User).filter(User.email == user_create.email).first():
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )

        # Create user record
        db_user = User(
            id=str(uuid.uuid4()),
            name=user_create.name,
            email=user_create.email,
            phone=user_create.phone,
            status=user_create.status,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        self.db.add(db_user)
        try:
            self.db.commit()
            self.db.refresh(db_user)
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=500,
                detail="Failed to create user"
            )

        return db_user

    async def create_user(self, user_create: UserCreate) -> User:
        return await self.register_user(user_create)

    async def list_users(
        self,
        skip: int = 0,
        limit: int = 100,
        name: Optional[str] = None,
        email: Optional[str] = None,
        status: Optional[UserStatus] = None
    ) -> List[User]:
        query = self.db.query(User)

        if name:
            query = query.filter(User.name.ilike(f"%{name}%"))
        if email:
            query = query.filter(User.email == email)
        if status:
            query = query.filter(User.status == status)

        return query.offset(skip).limit(limit).all()

    async def get_user(self, user_id: str) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    async def update_user(self, user_id: str, user_update: UserUpdate) -> User:
        db_user = await self.get_user(user_id)
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")

        update_data = user_update.dict(exclude_unset=True)
        if "email" in update_data and update_data["email"] != db_user.email:
            if self.db.query(User).filter(User.email == update_data["email"]).first():
                raise HTTPException(
                    status_code=400,
                    detail="Email already registered"
                )

        for field, value in update_data.items():
            setattr(db_user, field, value)

        db_user.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    async def delete_user(self, user_id: str) -> None:
        db_user = await self.get_user(user_id)
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")

        db_user.status = UserStatus.INACTIVE
        db_user.updated_at = datetime.utcnow()

        self.db.commit()