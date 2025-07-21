"""
定义数据模型中使用的枚举类型。

使用 Python 内置的 enum 模块可以确保数据的一致性和可维护性。
将字符串和枚举类结合，使得在数据库中存储字符串值，而在代码中使用枚举成员。
"""
import enum

class TaskStatus(str, enum.Enum):
    """任务状态枚举"""
    TODO = "待办"
    IN_PROGRESS = "进行中"
    DONE = "已完成"
    CANCELED = "已取消"

class TaskPriority(str, enum.Enum):
    """任务优先级枚举"""
    LOW = "低"
    MEDIUM = "中"
    HIGH = "高"
