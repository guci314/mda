from pydantic import BaseModel, Field, EmailStr

class User(BaseModel):
    username: str = Field(..., regex="^[a-zA-Z][a-zA-Z0-9_]*$")  # 应该用 pattern
    email: EmailStr
    name: str
    
    # 这是一个非常长的注释行，超过了79个字符的限制，会导致 flake8 报错 E501 line too long

def create_user(username, email, name):
    """创建用户"""
    user = User(username=username, email=email, name=name)  # F841: 未使用的变量
    return undefined_variable  # F821: 未定义的变量
