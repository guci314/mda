#!/usr/bin/env python3
"""
测试改进后的 Gemini 编译器 - 带进程监控和超时处理
"""
import os
import sys
import shutil
from pathlib import Path
from dotenv import load_dotenv

# 添加src到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

# 加载环境变量
project_root = Path(__file__).parent.parent
env_file = project_root / ".env"
if env_file.exists():
    load_dotenv(env_file)
    print(f"✓ 已加载环境变量文件: {env_file}")

from compiler.config import CompilerConfig
from compiler.compiler_factory import CompilerFactory


def test_improved_compiler():
    """测试改进后的编译器"""
    print("\n" + "="*60)
    print("测试改进后的 Gemini 编译器")
    print("="*60)
    
    # 创建测试目录
    test_dir = Path("./test_improved")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    test_dir.mkdir()
    
    # 创建简单的 PIM 文件
    pim_file = test_dir / "simple_todo.md"
    pim_content = """# 简单待办事项系统

## 业务实体

### 待办事项 (Todo)
代表用户的一个待办任务。

属性：
- 标题：任务的简短描述
- 描述：任务的详细说明（可选）
- 状态：待办/完成
- 创建时间：任务创建的时间
- 完成时间：任务完成的时间（可选）

## 业务服务

### 待办事项服务 (TodoService)
管理待办事项的业务操作。

方法：
1. 创建待办事项
   - 输入：标题、描述
   - 输出：创建的待办事项

2. 获取所有待办事项
   - 输出：待办事项列表

3. 更新待办事项状态
   - 输入：待办事项ID、新状态
   - 输出：更新后的待办事项

4. 删除待办事项
   - 输入：待办事项ID
   - 输出：删除成功/失败
"""
    
    with open(pim_file, 'w', encoding='utf-8') as f:
        f.write(pim_content)
    
    print(f"\n1. 创建测试 PIM 文件: {pim_file}")
    
    # 创建编译器配置
    config = CompilerConfig(
        target_platform="fastapi",
        output_dir=test_dir / "output",
        llm_provider="deepseek",
        auto_test=False,  # 先不测试自动修复
        verbose=True
    )
    
    print(f"\n2. 创建编译器...")
    compiler = CompilerFactory.create_compiler(config)
    
    # 执行编译
    print(f"\n3. 开始编译（带进程监控）...")
    result = compiler.compile(pim_file)
    
    # 输出结果
    print(f"\n4. 编译结果:")
    print(f"   - 成功: {result.success}")
    print(f"   - PIM 文件: {result.pim_file}")
    print(f"   - PSM 文件: {result.psm_file}")
    print(f"   - 代码目录: {result.code_dir}")
    if result.error:
        print(f"   - 错误: {result.error}")
    if result.compilation_time:
        print(f"   - 编译时间: {result.compilation_time:.2f} 秒")
    
    # 检查生成的文件
    if result.success and result.code_dir:
        print(f"\n5. 检查生成的文件:")
        
        # 统计文件
        all_files = list(result.code_dir.rglob("*"))
        py_files = [f for f in all_files if f.suffix == ".py" and f.is_file()]
        
        print(f"   - 总文件数: {len([f for f in all_files if f.is_file()])}")
        print(f"   - Python 文件数: {len(py_files)}")
        
        # 检查关键文件
        key_files_to_check = [
            "requirements.txt",
            "src/main.py",
            "src/models/todo.py",
            "src/schemas/todo.py",
            "src/api/todos.py",
            "src/services/todo_service.py"
        ]
        
        print(f"\n   关键文件检查:")
        for key_file in key_files_to_check:
            found = False
            for f in all_files:
                if key_file in str(f.relative_to(result.code_dir)):
                    size = f.stat().st_size if f.is_file() else 0
                    print(f"   ✓ {key_file} ({size} 字节)")
                    found = True
                    break
            if not found:
                print(f"   ✗ {key_file} 未找到")
        
        # 显示 requirements.txt
        req_file = result.code_dir / "requirements.txt"
        if req_file.exists():
            print(f"\n   requirements.txt 内容:")
            print("   " + "-" * 40)
            with open(req_file, 'r') as f:
                for line in f:
                    print(f"   {line.rstrip()}")
            print("   " + "-" * 40)
    
    return result


if __name__ == "__main__":
    print("开始测试改进后的编译器...")
    print("此测试将监控 Gemini CLI 进程，如果长时间没有进展会自动终止")
    
    result = test_improved_compiler()
    
    if result.success:
        print("\n✅ 编译成功完成！")
        print(f"生成的代码位于: {result.code_dir}")
    else:
        print("\n❌ 编译失败")
        if result.error:
            print(f"错误: {result.error}")
    
    print("\n测试完成。")