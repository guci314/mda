#!/usr/bin/env python3
"""
Agent Builder Demo - 构建一个Debug Agent
通过迭代优化知识文件，从零开始构建一个能够修复测试的Debug Agent
"""

import os
import sys
from pathlib import Path
import time
import json

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from core.react_agent_minimal import ReactAgentMinimal


class AgentBuilder:
    """Agent Builder - 用于构建和优化Agent的元工具"""
    
    def __init__(self, work_dir: str, target_task: str):
        """
        初始化Agent Builder
        
        Args:
            work_dir: 工作目录
            target_task: 目标任务描述
        """
        self.work_dir = Path(work_dir)
        self.work_dir.mkdir(parents=True, exist_ok=True)
        self.target_task = target_task
        self.iteration = 0
        self.knowledge_dir = self.work_dir / "knowledge_iterations"
        self.knowledge_dir.mkdir(exist_ok=True)
        
    def create_test_environment(self):
        """创建测试环境 - 一个有bug的Python项目"""
        print("\n📦 创建测试环境...")
        
        # 创建一个简单的计算器模块
        calculator_code = '''"""简单计算器模块"""

def add(a, b):
    """加法"""
    return a + b

def subtract(a, b):
    """减法"""
    return a - b

def multiply(a, b):
    """乘法"""
    return a * b

def divide(a, b):
    """除法"""
    if b = 0:  # Bug: 应该是 ==
        raise ValueError("Cannot divide by zero")
    return a / b

def power(base, exp):
    """幂运算"""
    return base ^ exp  # Bug: 应该是 **
'''
        
        # 创建测试文件
        test_code = '''"""计算器测试"""
import pytest
from calculator import add, subtract, multiply, divide, power

def test_add():
    assert add(2, 3) == 5
    assert add(-1, 1) == 0

def test_subtract():
    assert subtract(5, 3) == 2
    assert subtract(0, 5) == -5

def test_multiply():
    assert multiply(3, 4) == 12
    assert multiply(-2, 3) == -6

def test_divide():
    assert divide(10, 2) == 5
    assert divide(7, 2) == 3.5
    with pytest.raises(ValueError):
        divide(10, 0)

def test_power():
    assert power(2, 3) == 8  # 这个测试会失败
    assert power(5, 0) == 1
'''
        
        # 写入文件
        (self.work_dir / "calculator.py").write_text(calculator_code)
        (self.work_dir / "test_calculator.py").write_text(test_code)
        print("  ✅ 创建了calculator.py (包含2个bug)")
        print("  ✅ 创建了test_calculator.py")
        
    def write_knowledge_iteration(self, version: int, content: str):
        """写入知识文件的某个版本"""
        knowledge_file = self.knowledge_dir / f"debug_knowledge_v{version}.md"
        knowledge_file.write_text(content)
        return knowledge_file
        
    def create_initial_knowledge(self):
        """创建初始的（简单的）debug知识文件"""
        print(f"\n📝 迭代 {self.iteration}: 创建初始知识文件")
        
        initial_knowledge = """# Debug Agent 知识文件 v0

## 任务：修复测试错误

当需要修复测试时：
1. 运行pytest
2. 查看错误
3. 修复代码
"""
        
        knowledge_file = self.write_knowledge_iteration(0, initial_knowledge)
        print(f"  ✅ 创建了 {knowledge_file.name}")
        return knowledge_file
        
    def test_agent(self, knowledge_file: Path) -> dict:
        """测试Agent的表现"""
        print(f"\n🧪 测试Agent (使用 {knowledge_file.name})")
        
        # 创建Agent并加载知识文件
        agent = ReactAgentMinimal(
            work_dir=str(self.work_dir),
            model="deepseek-chat",  # 使用便宜的模型做测试
            knowledge_files=[str(knowledge_file)],
            max_rounds=30  # 限制轮数避免无限循环
        )
        
        # 执行任务
        start_time = time.time()
        try:
            result = agent.execute(task=self.target_task)
            success = "所有测试通过" in result or "All tests passed" in result
        except Exception as e:
            result = str(e)
            success = False
        
        elapsed = time.time() - start_time
        
        # 记录结果
        # 计算执行轮数（通过messages列表中assistant消息的数量）
        rounds = len([m for m in agent.messages if m["role"] == "assistant"])
        
        test_result = {
            "version": knowledge_file.name,
            "success": success,
            "rounds": rounds,
            "time": f"{elapsed:.1f}秒",
            "issues": []
        }
        
        # 分析问题
        if not success:
            if rounds >= 30:
                test_result["issues"].append("超过最大轮数限制")
            if "不知道" in result or "unclear" in result.lower():
                test_result["issues"].append("Agent不理解任务")
            if "重复" in result or "loop" in result.lower():
                test_result["issues"].append("Agent陷入循环")
                
        return test_result
        
    def analyze_and_improve(self, test_result: dict) -> Path:
        """分析测试结果并改进知识文件"""
        self.iteration += 1
        print(f"\n🔄 迭代 {self.iteration}: 分析问题并优化知识文件")
        
        issues = test_result.get("issues", [])
        
        if not issues:
            print("  ✅ 没有发现问题！")
            return None
            
        print(f"  发现问题: {', '.join(issues)}")
        
        # 根据不同的迭代次数，逐步改进知识文件
        if self.iteration == 1:
            improved_knowledge = """# Debug Agent 知识文件 v1

## 任务：修复Python测试错误

### 执行流程

1. **运行测试查看具体错误**
   ```bash
   pytest -v
   ```

2. **分析错误信息**
   - 查看失败的测试名称
   - 查看错误类型（SyntaxError, AssertionError等）
   - 记录错误位置（文件名和行号）

3. **读取相关代码**
   使用read_file读取：
   - 测试文件（查看预期行为）
   - 源代码文件（查看实际实现）

4. **修复错误**
   根据错误类型采取相应措施：
   - SyntaxError：修复语法错误
   - AssertionError：修复逻辑错误

5. **验证修复**
   再次运行pytest确认所有测试通过
"""
            
        elif self.iteration == 2:
            improved_knowledge = """# Debug Agent 知识文件 v2

## 任务：修复Python测试错误

### 核心原则
- 先理解错误，再修复
- 一次修复一个问题
- 每次修复后都要验证

### 详细执行流程

1. **初始诊断**
   ```bash
   pytest -v
   ```
   记录所有失败的测试和错误类型

2. **处理SyntaxError（优先级最高）**
   - 错误信息会显示具体位置，如 "calculator.py:14: SyntaxError"
   - 读取该文件的对应行
   - 常见语法错误：
     * `=` vs `==` (赋值vs比较)
     * 缺少冒号
     * 缩进错误
   - 修复后立即测试

3. **处理AssertionError**
   - 查看测试的期望值和实际值
   - 读取被测试的函数实现
   - 常见逻辑错误：
     * 错误的运算符（如 `^` vs `**`）
     * 错误的返回值
     * 边界条件处理不当

4. **逐个修复**
   - 先修复所有SyntaxError
   - 再修复AssertionError
   - 每修复一个错误就运行一次pytest

5. **最终验证**
   ```bash
   pytest -v
   ```
   确保输出显示 "all tests passed" 或所有测试都是绿色的

### 注意事项
- 使用search_replace而不是重写整个文件
- 修复时保持代码的其他部分不变
- 如果不确定，先读取更多上下文
"""
            
        elif self.iteration >= 3:
            improved_knowledge = """# Debug Agent 知识文件 v3 (完整版)

## 任务：修复Python测试错误

### 核心原则
- 系统化诊断，精确修复
- 理解错误本质，不盲目尝试
- 保持代码最小改动

### 标准操作流程（SOP）

#### 阶段1：全面诊断
```bash
pytest -v --tb=short
```
收集所有错误信息，按优先级分类：
1. SyntaxError（语法错误）- 最高优先级
2. ImportError（导入错误）- 高优先级  
3. AssertionError（断言错误）- 中优先级
4. 其他运行时错误 - 低优先级

#### 阶段2：修复SyntaxError
对于每个SyntaxError：

1. **定位错误**
   错误信息格式：`File "calculator.py", line 14`
   
2. **读取上下文**
   ```python
   read_file("calculator.py", offset=10, limit=10)  # 读取14行附近
   ```

3. **识别并修复**
   常见Python语法错误模式：
   - `if b = 0:` → `if b == 0:`（赋值vs比较）
   - `def func()` → `def func():`（缺少冒号）
   - 缩进错误 → 确保使用4个空格
   
4. **精确替换**
   ```python
   search_replace(
       file_path="calculator.py",
       old_text="if b = 0:",
       new_text="if b == 0:"
   )
   ```

#### 阶段3：修复逻辑错误
对于AssertionError：

1. **理解测试意图**
   读取失败的测试函数，理解预期行为
   
2. **检查实现**
   读取被测试的函数实现
   
3. **常见逻辑错误**
   - `^`（按位异或）vs `**`（幂运算）
   - `/`（浮点除法）vs `//`（整数除法）
   - 边界条件处理

4. **验证修复**
   ```bash
   pytest test_calculator.py::test_power -v  # 单独测试修复的函数
   ```

#### 阶段4：最终验证
```bash
pytest -v
```
成功标志：
- 所有测试名称前有绿色的PASSED
- 输出包含 "5 passed" 或类似信息
- 没有红色的FAILED

### 错误修复速查表

| 错误类型 | 常见原因 | 修复方法 |
|---------|---------|---------|
| `SyntaxError: invalid syntax` | 使用`=`而非`==` | 替换为比较运算符 |
| `TypeError: unsupported operand` | 错误的运算符 | `^`改为`**`（幂运算） |
| `ZeroDivisionError` | 除零检查错误 | 添加`if b == 0`检查 |
| `AssertionError` | 计算结果错误 | 检查运算符和逻辑 |

### 调试技巧
1. 如果错误信息不清晰，使用`pytest -vv`获取更详细输出
2. 对于复杂错误，可以添加print语句临时调试
3. 修复后立即测试，不要累积多个修改

### 记住
- 每个错误都有明确的原因
- 系统化方法比随机尝试更高效
- 保持耐心，逐个解决问题
"""
        
        # 写入改进的知识文件
        knowledge_file = self.write_knowledge_iteration(self.iteration, improved_knowledge)
        print(f"  ✅ 创建了改进版本 {knowledge_file.name}")
        
        return knowledge_file
        
    def run_builder_loop(self, max_iterations: int = 5):
        """运行Agent Builder的主循环"""
        print("\n" + "="*60)
        print("🚀 Agent Builder - 构建Debug Agent")
        print("="*60)
        
        # 创建测试环境
        self.create_test_environment()
        
        # 初始知识文件
        current_knowledge = self.create_initial_knowledge()
        
        # 迭代优化循环
        for i in range(max_iterations):
            # 测试当前Agent
            test_result = self.test_agent(current_knowledge)
            
            # 打印测试结果
            print(f"\n📊 测试结果:")
            print(f"  - 成功: {'✅ 是' if test_result['success'] else '❌ 否'}")
            print(f"  - 轮数: {test_result['rounds']}")
            print(f"  - 耗时: {test_result['time']}")
            if test_result['issues']:
                print(f"  - 问题: {', '.join(test_result['issues'])}")
            
            # 如果成功，结束循环
            if test_result['success']:
                print("\n🎉 成功！Agent已经能够完成任务")
                self.print_summary()
                break
                
            # 分析并改进
            improved_knowledge = self.analyze_and_improve(test_result)
            if improved_knowledge:
                current_knowledge = improved_knowledge
            else:
                print("\n⚠️ 无法继续优化")
                break
        else:
            print(f"\n⚠️ 达到最大迭代次数 {max_iterations}")
            
    def print_summary(self):
        """打印构建总结"""
        print("\n" + "="*60)
        print("📈 Agent Builder 总结")
        print("="*60)
        
        print(f"\n迭代次数: {self.iteration + 1}")
        print("\n知识文件演化:")
        
        for i in range(self.iteration + 1):
            knowledge_file = self.knowledge_dir / f"debug_knowledge_v{i}.md"
            if knowledge_file.exists():
                lines = knowledge_file.read_text().count('\n')
                print(f"  v{i}: {lines} 行")
        
        print("\n关键改进:")
        print("  v0 → v1: 添加具体命令和基本流程")
        print("  v1 → v2: 增加错误分类和处理策略")
        print("  v2 → v3: 完整SOP、错误速查表、调试技巧")
        
        print("\n💡 核心洞察:")
        print("  1. 知识文件需要具体、可执行的指令")
        print("  2. 错误处理需要系统化的方法")
        print("  3. 提供示例和模式识别很重要")
        print("  4. 逐步细化比一次完美更有效")


def main():
    """主函数"""
    # 设置工作目录
    work_dir = "/tmp/agent_builder_demo"
    
    # 目标任务
    target_task = "修复calculator.py中的所有测试错误，确保pytest全部通过"
    
    # 创建Builder并运行
    builder = AgentBuilder(work_dir, target_task)
    builder.run_builder_loop(max_iterations=4)
    
    print("\n✨ Agent Builder演示完成！")
    print(f"💾 知识文件保存在: {builder.knowledge_dir}")
    print(f"🔧 测试项目位于: {work_dir}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断")
    except Exception as e:
        print(f"\n\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()