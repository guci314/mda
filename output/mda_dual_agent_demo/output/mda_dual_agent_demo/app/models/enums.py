"""
枚举定义模块
定义系统中使用的所有枚举类型
"""
from enum import Enum


class BookStatus(str, Enum):
    """图书状态枚举"""
    AVAILABLE = "在架"
    REMOVED = "已下架"


class ReaderType(str, Enum):
    """读者类型枚举"""
    STUDENT = "学生"
    TEACHER = "教师"
    SOCIAL = "社会人员"


class ReaderStatus(str, Enum):
    """读者状态枚举"""
    ACTIVE = "正常"
    FROZEN = "冻结"
    DELETED = "注销"


class BorrowStatus(str, Enum):
    """借阅状态枚举"""
    BORROWED = "借阅中"
    RETURNED = "已归还"
    OVERDUE = "已逾期"
    LOST = "已丢失"


class ReservationStatus(str, Enum):
    """预约状态枚举"""
    PENDING = "等待中"
    READY = "可借阅"
    CANCELLED = "已取消"
    COMPLETED = "已完成"