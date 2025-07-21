#!/usr/bin/env python3
"""
测试纯 Gemini 编译器
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


def test_pure_gemini_compiler():
    """测试纯 Gemini 编译器"""
    print("\n" + "="*60)
    print("测试纯 Gemini 编译器 (v3.0)")
    print("="*60)
    
    # 创建测试目录
    test_dir = Path("./test_pure_gemini")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    test_dir.mkdir()
    
    # 创建 PIM 文件
    pim_file = test_dir / "task_manager.md"
    pim_content = """# 任务管理系统

## 业务描述
一个简单但功能完整的任务管理系统，允许用户创建、管理和跟踪任务的完成情况。

## 业务实体

### 任务 (Task)
代表需要完成的一项工作。

属性：
- 标题：任务的简短描述（必填）
- 描述：任务的详细说明（可选）
- 优先级：高/中/低
- 状态：待办/进行中/已完成/已取消
- 截止日期：任务应完成的日期（可选）
- 创建时间：任务创建的时间
- 更新时间：最后修改时间
- 完成时间：任务完成的时间（可选）

### 标签 (Tag)
用于分类和组织任务。

属性：
- 名称：标签名（唯一）
- 颜色：标签的显示颜色（十六进制）
- 描述：标签的说明（可选）

### 任务标签关系
任务可以有多个标签，标签可以用于多个任务（多对多关系）。

## 业务服务

### 任务服务 (TaskService)
管理任务的核心业务逻辑。

方法：
1. 创建任务
   - 输入：标题、描述、优先级、截止日期、标签列表
   - 验证：标题不能为空，截止日期必须是未来时间
   - 输出：创建的任务

2. 更新任务
   - 输入：任务ID、更新的字段
   - 验证：只能更新存在的任务
   - 输出：更新后的任务

3. 更改任务状态
   - 输入：任务ID、新状态
   - 业务规则：
     - 已取消的任务不能再更改状态
     - 完成任务时记录完成时间
   - 输出：更新后的任务

4. 查询任务
   - 支持按状态、优先级、标签筛选
   - 支持按创建时间、截止日期排序
   - 支持分页

5. 删除任务
   - 只能删除已完成或已取消的任务

### 标签服务 (TagService)
管理标签。

方法：
1. 创建标签
2. 更新标签
3. 删除标签（只能删除未被使用的标签）
4. 获取所有标签
5. 获取任务的标签
"""
    
    with open(pim_file, 'w', encoding='utf-8') as f:
        f.write(pim_content)
    
    print(f"\n1. 创建测试 PIM 文件: {pim_file}")
    
    # 创建编译器配置
    config = CompilerConfig(
        target_platform="fastapi",
        output_dir=test_dir / "output",
        auto_test=False,  # 先关闭自动测试
        verbose=True
    )
    
    print(f"\n2. 编译器配置:")
    for key, value in config.to_dict().items():
        print(f"   - {key}: {value}")
    
    # 创建编译器
    print(f"\n3. 创建纯 Gemini 编译器...")
    compiler = CompilerFactory.create_compiler(config)
    
    # 执行编译
    print(f"\n4. 开始编译（PIM → PSM → Code）...")
    print("   这将使用 Gemini CLI 完成整个流程")
    result = compiler.compile(pim_file)
    
    # 输出结果
    print(f"\n5. 编译结果:")
    print(f"   - 成功: {result.success}")
    print(f"   - PIM 文件: {result.pim_file}")
    print(f"   - PSM 文件: {result.psm_file}")
    print(f"   - 代码目录: {result.code_dir}")
    if result.error:
        print(f"   - 错误: {result.error}")
    if result.compilation_time:
        print(f"   - 总编译时间: {result.compilation_time:.2f} 秒")
    
    if result.statistics:
        print(f"\n   时间统计:")
        print(f"   - PSM 生成: {result.statistics['psm_generation_time']} 秒")
        print(f"   - 代码生成: {result.statistics['code_generation_time']} 秒")
        print(f"   - 文件统计: {result.statistics['total_files']} 个文件 ({result.statistics['python_files']} 个 Python 文件)")
    
    # 检查生成的文件
    if result.success and result.code_dir:
        print(f"\n6. 检查生成的关键文件:")
        
        key_files = [
            "requirements.txt",
            "README.md",
            ".env.example",
            "main.py",
            "app/main.py",
            "src/main.py",
            "tests",
            "alembic.ini"
        ]
        
        for key_file in key_files:
            found = False
            # 搜索文件
            for f in result.code_dir.rglob("*"):
                if key_file in str(f):
                    if f.is_file():
                        size = f.stat().st_size
                        print(f"   ✓ {key_file} ({size} 字节)")
                    else:
                        print(f"   ✓ {key_file} (目录)")
                    found = True
                    break
            if not found:
                print(f"   - {key_file} 未找到")
    
    return result


if __name__ == "__main__":
    print("开始测试纯 Gemini 编译器...")
    print("此版本完全使用 Gemini CLI，不依赖其他 LLM")
    
    result = test_pure_gemini_compiler()
    
    if result.success:
        print("\n✅ 编译成功完成！")
        print(f"生成的代码位于: {result.code_dir}")
        print("\n相比之前的版本：")
        print("- 更快的编译速度")
        print("- 更简单的配置")
        print("- 更好的一致性")
        print("- 只需要 Gemini API")
    else:
        print("\n❌ 编译失败")
        if result.error:
            print(f"错误: {result.error}")
    
    print("\n测试完成。")