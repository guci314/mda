"""
Tag (标签) Pydantic 模式定义。

这些模式用于 API 的数据验证、序列化和文档生成。
"""
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

class TagBase(BaseModel):
    """
    标签的基础模式，包含了所有标签共有的字段。
    """
    name: str = Field(..., min_length=1, max_length=50, description="标签名称")
    # 使用 Pydantic V2 的 'pattern' 字段来验证十六进制颜色代码
    color: str = Field(
        default="#FFFFFF", 
        pattern=r"^#[0-9a-fA-F]{6}$", 
        description="标签颜色 (Hex格式)"
    )
    description: Optional[str] = Field(None, max_length=255, description="标签描述")

class TagCreate(TagBase):
    """
    创建标签时使用的模式。
    目前与基础模式相同，但为了语义清晰和未来扩展而单独定义。
    """
    pass

class TagUpdate(TagBase):
    """
    更新标签时使用的模式。
    所有字段都是可选的。
    """
    name: Optional[str] = Field(None, min_length=1, max_length=50, description="标签名称")
    color: Optional[str] = Field(
        None, 
        pattern=r"^#[0-9a-fA-F]{6}$", 
        description="标签颜色 (Hex格式)"
    )
    description: Optional[str] = Field(None, max_length=255, description="标签描述")


class TagRead(TagBase):
    """
    从 API 读取（返回）标签数据时使用的模式。
    包含了数据库生成的 ID，并配置为可以从 ORM 模型实例转换。
    """
    id: int

    # ConfigDict 用于配置 Pydantic 的行为
    # from_attributes=True (在 Pydantic V1 中是 orm_mode=True)
    # 允许 Pydantic 模型从 ORM 对象的属性中读取数据。
    model_config = ConfigDict(from_attributes=True)
