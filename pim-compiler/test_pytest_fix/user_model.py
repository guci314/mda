from pydantic import BaseModel, Field, EmailStr

class User(BaseModel):
    username: str = Field(..., pattern="^[a-zA-Z][a-zA-Z0-9_]*$")  # 错误：应该用 pattern
    email: EmailStr  # 需要 email-validator
    name: str
    
def create_user(username: str, email: str, name: str) -> User:
    """创建用户"""
    return User(username=username, email=email, name=name)
