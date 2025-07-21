from pydantic import BaseModel, Field

class User(BaseModel):
    username: str = Field(..., regex="^[a-zA-Z][a-zA-Z0-9_]*$")  # 应该用 pattern
    
def test():
    return undefined_var  # 未定义的变量
