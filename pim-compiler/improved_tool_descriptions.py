#!/usr/bin/env python3
"""改进 ReactAgent 中的 Tool 描述示例"""

from pathlib import Path
from typing import Optional, List
from langchain_core.tools import tool
from pydantic import BaseModel, Field

# ========== 原版工具（简单描述） ==========

@tool("write_file_simple")
def write_file_simple(file_path: str, content: str) -> str:
    """写入文件"""
    # 实现...
    return f"Successfully wrote file: {file_path}"

@tool("run_tests_simple")  
def run_tests_simple(test_dir: str = "tests") -> str:
    """运行 pytest 测试"""
    # 实现...
    return "Tests passed"

# ========== 改进版工具（详细描述） ==========

class FileWriteInput(BaseModel):
    """文件写入参数"""
    file_path: str = Field(
        description="相对于输出目录的文件路径，如 'src/main.py' 或 'config/settings.json'"
    )
    content: str = Field(
        description="要写入的文件内容，支持任何文本格式"
    )
    encoding: str = Field(
        default="utf-8",
        description="文件编码格式，默认 utf-8"
    )
    create_dirs: bool = Field(
        default=True,
        description="如果目录不存在是否自动创建"
    )

@tool("write_file_improved", args_schema=FileWriteInput)
def write_file_improved(
    file_path: str, 
    content: str, 
    encoding: str = "utf-8",
    create_dirs: bool = True
) -> str:
    """智能写入文件到项目目录。
    
    功能特性：
    - 自动创建不存在的父目录
    - 支持多种编码格式
    - 覆盖已存在的文件
    - 返回详细的操作结果
    
    使用场景：
    - 生成源代码文件（.py, .js, .java 等）
    - 创建配置文件（.json, .yaml, .env 等）
    - 生成文档文件（.md, .rst, .txt 等）
    
    注意事项：
    - 文件路径相对于项目输出目录
    - 会覆盖已存在的文件，请谨慎使用
    - 大文件（>10MB）可能影响性能
    
    Returns:
        操作结果描述，包括文件大小和路径信息
    """
    # 实现...
    return f"Successfully wrote {len(content)} bytes to {file_path}"

class TestRunInput(BaseModel):
    """测试执行参数"""
    test_dir: str = Field(
        default="tests",
        description="测试目录路径，相对于项目根目录"
    )
    pattern: str = Field(
        default="test_*.py",
        description="测试文件匹配模式"
    )
    verbose: bool = Field(
        default=True,
        description="是否显示详细测试输出"
    )
    markers: Optional[str] = Field(
        default=None,
        description="pytest markers，如 'unit' 或 'not slow'"
    )
    coverage: bool = Field(
        default=False,
        description="是否生成代码覆盖率报告"
    )

@tool("run_tests_improved", args_schema=TestRunInput)
def run_tests_improved(
    test_dir: str = "tests",
    pattern: str = "test_*.py",
    verbose: bool = True,
    markers: Optional[str] = None,
    coverage: bool = False
) -> str:
    """执行项目测试套件并返回详细结果。
    
    功能说明：
    - 使用 pytest 框架运行测试
    - 自动发现匹配模式的测试文件
    - 支持按标记筛选测试
    - 可生成覆盖率报告
    
    执行流程：
    1. 定位测试目录和项目根目录
    2. 设置 PYTHONPATH 确保导入正常
    3. 构建并执行 pytest 命令
    4. 解析并返回测试结果
    
    常见用法：
    - 运行所有测试：run_tests()
    - 只运行单元测试：run_tests(markers='unit')
    - 生成覆盖率：run_tests(coverage=True)
    - 运行特定目录：run_tests(test_dir='tests/integration')
    
    错误处理：
    - 测试目录不存在时返回错误信息
    - 测试失败时返回失败详情
    - 导入错误时提供修复建议
    
    Returns:
        测试执行结果，包括通过/失败数量、错误信息、执行时间等
    """
    # 实现...
    return "Test results..."

# ========== 对比不同描述级别 ==========

def compare_descriptions():
    """对比不同描述级别的效果"""
    
    print("=== Tool 描述级别对比 ===\n")
    
    # 级别1：最简描述
    @tool
    def search_v1(query: str) -> str:
        """搜索"""
        return "results"
    
    # 级别2：基础描述
    @tool
    def search_v2(query: str) -> str:
        """在项目中搜索文本"""
        return "results"
    
    # 级别3：功能描述
    @tool
    def search_v3(query: str) -> str:
        """在项目文件中搜索指定文本。
        
        搜索所有文本文件，返回包含查询字符串的文件和行号。
        """
        return "results"
    
    # 级别4：完整描述
    class SearchInput(BaseModel):
        query: str = Field(description="搜索查询字符串，支持正则表达式")
        file_pattern: str = Field(default="*", description="文件名匹配模式，如 '*.py'")
        case_sensitive: bool = Field(default=True, description="是否区分大小写")
        max_results: int = Field(default=50, description="最大返回结果数")
    
    @tool("search_v4", args_schema=SearchInput)
    def search_v4(
        query: str,
        file_pattern: str = "*",
        case_sensitive: bool = True,
        max_results: int = 50
    ) -> str:
        """高级文本搜索工具。
        
        功能特性：
        - 支持正则表达式搜索
        - 可按文件类型过滤
        - 大小写敏感控制
        - 结果数量限制
        
        搜索范围：
        - 递归搜索所有子目录
        - 自动跳过二进制文件
        - 忽略 .git, node_modules 等目录
        
        返回格式：
        文件路径:行号: 匹配的行内容
        
        使用示例：
        - 搜索所有 Python 文件中的 'TODO'
        - 查找包含特定函数名的文件
        - 定位配置项的使用位置
        """
        return "results"
    
    # 打印对比
    tools = [
        ("最简描述", search_v1),
        ("基础描述", search_v2),
        ("功能描述", search_v3),
        ("完整描述", search_v4)
    ]
    
    for name, tool in tools:
        print(f"{name}:")
        print(f"  描述: {tool.description[:100]}...")
        print(f"  参数: {tool.args}")
        print()

# ========== 系统提示词的配合 ==========

def create_system_prompt_examples():
    """展示系统提示词如何引导工具使用"""
    
    # 简单版系统提示词
    simple_prompt = """
你是一个代码生成助手。使用提供的工具生成代码。
"""
    
    # 详细版系统提示词
    detailed_prompt = """
你是一个专业的 Python 项目生成专家。

## 工具使用指南

### 文件操作
- **write_file**: 用于创建所有项目文件
  - 源代码文件：确保包含适当的文件头注释
  - 配置文件：使用适合的格式（JSON/YAML/INI）
  - 文档文件：使用 Markdown 格式
  
### 测试执行
- **run_tests**: 在以下时机使用
  - 完成核心功能实现后
  - 修复错误后验证
  - 最终交付前的完整测试
  
### 工作流程
1. 分析需求，规划项目结构
2. 创建目录结构（使用 create_directory）
3. 生成代码文件（使用 write_file）
   - 先创建模型和架构
   - 再实现业务逻辑
   - 最后添加测试
4. 创建配置和文档
5. 运行测试验证（使用 run_tests）
6. 根据测试结果修复问题

### 质量标准
- 所有 Python 文件必须符合 PEP 8
- 测试覆盖率应达到 80% 以上
- 文档应包含使用示例
"""
    
    return simple_prompt, detailed_prompt

# ========== 实践建议 ==========

def best_practices_summary():
    """Tool 描述的最佳实践总结"""
    
    print("\n=== Tool 描述最佳实践总结 ===\n")
    
    print("1. **描述清晰度**")
    print("   ✅ 使用动词开头：'创建'、'执行'、'搜索'")
    print("   ✅ 说明主要功能和用途")
    print("   ❌ 避免模糊描述：'处理'、'操作'")
    print()
    
    print("2. **参数说明**")
    print("   ✅ 每个参数都有 Field description")
    print("   ✅ 说明格式要求和限制")
    print("   ✅ 提供默认值和示例")
    print()
    
    print("3. **使用场景**")
    print("   ✅ 列举典型使用场景")
    print("   ✅ 说明何时该用/不该用")
    print("   ✅ 提供具体示例")
    print()
    
    print("4. **返回值说明**")
    print("   ✅ 描述返回格式")
    print("   ✅ 说明成功/失败情况")
    print("   ✅ 包含可能的错误信息")
    print()
    
    print("5. **与系统提示词配合**")
    print("   ✅ 系统提示词中引用工具名")
    print("   ✅ 说明工具使用顺序")
    print("   ✅ 提供工作流程指导")

if __name__ == "__main__":
    compare_descriptions()
    best_practices_summary()
    
    # 展示改进效果
    print("\n=== 改进效果 ===")
    print("\n原版（简单）：")
    print(f"工具: {write_file_simple.name}")
    print(f"描述: {write_file_simple.description}")
    
    print("\n改进版（详细）：")
    print(f"工具: {write_file_improved.name}")
    print(f"描述: {write_file_improved.description[:200]}...")
    print(f"参数架构: {write_file_improved.args_schema.__fields__.keys()}")