import pytest
from user_model import User, create_user

def test_create_user():
    """测试创建用户"""
    user = create_user("john_doe", "john@example.com", "John Doe")
    assert user.username == "john_doe"
    assert user.email == "john@example.com"
    assert user.name == "John Doe"

def test_invalid_email():
    """测试无效邮箱"""
    with pytest.raises(ValueError):
        create_user("john_doe", "invalid-email", "John Doe")
        
def test_invalid_username():
    """测试无效用户名"""
    with pytest.raises(ValueError):
        User(username="123invalid", email="test@example.com", name="Test")
