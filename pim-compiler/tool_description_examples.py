#!/usr/bin/env python3
"""展示 LangChain 中 Tool 描述的几种方式"""

from langchain_core.tools import tool, Tool, StructuredTool
from langchain.pydantic_v1 import BaseModel, Field
from typing import Type

# 方式1：使用 @tool 装饰器 + docstring
@tool
def search_weather(location: str) -> str:
    """查询指定地点的天气信息。
    
    这个工具可以获取任何城市的当前天气状况，
    包括温度、湿度、风速等信息。
    
    Args:
        location: 城市名称，如 "北京" 或 "Beijing"
    
    Returns:
        该地点的天气信息描述
    """
    return f"{location}的天气是晴天，温度25°C"

# 方式2：使用 @tool 装饰器 + 显式描述
@tool("calculate_area", description="计算矩形的面积。输入长和宽，返回面积值。")
def calculate_rectangle_area(length: float, width: float) -> float:
    """这个 docstring 会被 description 参数覆盖"""
    return length * width

# 方式3：使用 Pydantic Schema + Field 描述
class EmailInput(BaseModel):
    """发送邮件的输入参数"""
    recipient: str = Field(description="收件人邮箱地址")
    subject: str = Field(description="邮件主题")
    body: str = Field(description="邮件正文内容")
    cc: str = Field(default="", description="抄送地址（可选）")

@tool("send_email", args_schema=EmailInput)
def send_email(recipient: str, subject: str, body: str, cc: str = "") -> str:
    """发送电子邮件。
    
    可以发送带有主题和正文的邮件给指定收件人，
    支持抄送功能。
    """
    return f"邮件已发送给 {recipient}"

# 方式4：使用 Tool 类直接创建
def multiply_numbers(a: float, b: float) -> float:
    return a * b

multiply_tool = Tool(
    name="multiply",
    description="将两个数字相乘。用于数学计算。",
    func=multiply_numbers
)

# 方式5：使用 StructuredTool 创建复杂工具
class DatabaseQueryInput(BaseModel):
    """数据库查询参数"""
    query: str = Field(description="SQL查询语句")
    database: str = Field(description="数据库名称")
    limit: int = Field(default=10, description="返回结果数量限制")

def execute_query(query: str, database: str, limit: int = 10) -> str:
    return f"在 {database} 执行查询: {query} (限制 {limit} 条)"

database_tool = StructuredTool(
    name="execute_database_query",
    description="""执行数据库查询。
    
    这个工具可以在指定的数据库上执行 SQL 查询，
    并返回查询结果。支持 SELECT、INSERT、UPDATE 等操作。
    
    注意事项：
    - 查询结果默认限制为 10 条
    - 支持多种数据库类型
    - 自动处理连接和事务
    """,
    func=execute_query,
    args_schema=DatabaseQueryInput
)

# 展示工具信息
def show_tool_info():
    """展示工具如何被 Agent 理解"""
    
    tools = [
        search_weather,
        calculate_rectangle_area,
        send_email,
        multiply_tool,
        database_tool
    ]
    
    print("=== LangChain Tool 描述方式展示 ===\n")
    
    for tool in tools:
        print(f"工具名称: {tool.name}")
        print(f"工具描述: {tool.description}")
        if hasattr(tool, 'args_schema'):
            print(f"参数架构: {tool.args_schema}")
        print("-" * 50)
        print()

# Agent 如何理解 Tool？
def explain_tool_understanding():
    """解释 Agent 如何理解和选择工具"""
    
    print("\n=== Agent 如何理解 Tool ===\n")
    
    print("1. **名称识别**")
    print("   - Tool 的 name 属性提供唯一标识")
    print("   - 应该使用清晰、描述性的名称")
    print()
    
    print("2. **描述理解**")
    print("   - description 或 docstring 说明工具用途")
    print("   - Agent 通过描述理解何时使用该工具")
    print("   - 描述应包含：功能、适用场景、限制等")
    print()
    
    print("3. **参数推理**")
    print("   - args_schema 定义参数结构")
    print("   - Field descriptions 解释每个参数")
    print("   - Agent 可以理解必需/可选参数")
    print()
    
    print("4. **上下文匹配**")
    print("   - Agent 将用户需求与工具描述匹配")
    print("   - 选择最合适的工具执行任务")
    print()
    
    print("5. **返回值理解**")
    print("   - 通过描述了解返回值含义")
    print("   - 决定如何使用返回结果")

# 最佳实践
def best_practices():
    """Tool 描述的最佳实践"""
    
    print("\n=== Tool 描述最佳实践 ===\n")
    
    # 好的例子
    @tool
    def good_file_search(pattern: str, directory: str = ".") -> str:
        """在指定目录中搜索匹配模式的文件。
        
        功能：
        - 支持通配符模式（如 *.py, test_*.txt）
        - 递归搜索子目录
        - 返回匹配文件的完整路径列表
        
        使用场景：
        - 查找特定类型的文件
        - 定位项目中的源代码文件
        - 批量处理文件前的查找
        
        限制：
        - 不搜索隐藏目录（.开头）
        - 最多返回 100 个结果
        
        Args:
            pattern: 文件名模式，支持通配符
            directory: 搜索起始目录，默认当前目录
            
        Returns:
            匹配文件的路径列表，用换行符分隔
        """
        return "file1.py\nfile2.py"
    
    # 不好的例子
    @tool
    def bad_file_search(p: str, d: str = ".") -> str:
        """搜索文件"""  # 描述太简单
        return "files"
    
    print("✅ 好的 Tool 描述应该包含：")
    print("   1. 清晰的功能说明")
    print("   2. 适用场景描述")
    print("   3. 参数详细说明")
    print("   4. 返回值格式")
    print("   5. 使用限制或注意事项")
    print()
    
    print("❌ 避免：")
    print("   1. 过于简单的描述")
    print("   2. 参数名不清晰（如 p, d）")
    print("   3. 没有说明返回值格式")
    print("   4. 缺少使用场景")

if __name__ == "__main__":
    show_tool_info()
    explain_tool_understanding()
    best_practices()