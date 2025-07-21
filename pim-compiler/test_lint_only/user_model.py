from pydantic import BaseModel, Field


class User(BaseModel):
    username: str = Field(..., pattern="^[a-zA-Z][a-zA-Z0-9_]*$")
    name: str

    # 这是一个非常长的注释行，超过了79个字符的限制，
    # 会导致 flake8 报错 E501 line too long，
    # 这个注释真的很长


def create_user(username, name):
    """创建用户"""
    user = User(username=username, name=name)
    return user
