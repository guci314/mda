from fastapi import HTTPException, status

class EmailAlreadyExistsException(HTTPException):
    """邮箱已存在异常"""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="该邮箱已被注册"
        )

class UserNotFoundException(HTTPException):
    """用户不存在异常"""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )