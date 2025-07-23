import enum

class BookStatus(str, enum.Enum):
    ON_SHELF = "在架"
    REMOVED = "已下架"

class ReaderType(str, enum.Enum):
    STUDENT = "学生"
    TEACHER = "教师"
    STAFF = "社会人员"

class ReaderStatus(str, enum.Enum):
    NORMAL = "正常"
    FROZEN = "冻结"
    CANCELLED = "注销"

class BorrowStatus(str, enum.Enum):
    BORROWED = "借阅中"
    RETURNED = "已归还"
    OVERDUE = "已逾期"
    LOST = "已丢失"

class ReservationStatus(str, enum.Enum):
    WAITING = "等待中"
    AVAILABLE = "可借阅"
    CANCELLED = "已取消"
    COMPLETED = "已完成"
