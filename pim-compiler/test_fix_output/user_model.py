from pydantic import BaseModel, Field, EmailStr


class User(BaseModel):
    username: str = Field(..., regex="^[a-zA-Z][a-zA-Z0-9_]*$")  # 错误：应该用 pattern
    email: EmailStr  # 需要 email-validator
    name: str

    # 这是一个非常长的注释行，超过了79个字符的限制，会导致 flake8 报错 E501 line too long


def create_user(username, email, name):
    """创建用户"""
    user = User(username=username, email=email, name=name)
    return undefined_variable  # 错误：未定义的变量
