from typing import Optional
from pydantic import BaseModel
from .user import UserStatus

class UserQueryParams(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    status: Optional[UserStatus] = None
    skip: int = 0
    limit: int = 100