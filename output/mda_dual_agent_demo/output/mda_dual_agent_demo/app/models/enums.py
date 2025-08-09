from enum import Enum


class BookStatus(str, Enum):
    AVAILABLE = "在架"
    REMOVED = "已下架"


class ReaderType(str, Enum):
    STUDENT = "学生"
    TEACHER = "教师"
    SOCIAL = "社会人员"


class ReaderStatus(str, Enum):
    ACTIVE = "正常"
    FROZEN = "冻结"
    DELETED = "注销"


class BorrowStatus(str, Enum):
    BORROWED = "借阅中"
    RETURNED = "已归还"
    OVERDUE = "已逾期"
    LOST = "已丢失"


class ReservationStatus(str, Enum):
    PENDING = "等待中"
    READY = "可借阅"
    CANCELLED = "已取消"
    COMPLETED = "已完成"