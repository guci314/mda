#!/usr/bin/env python3
"""
测试新型 Gemini 编译器
"""
import os
import sys
import shutil
from pathlib import Path
from dotenv import load_dotenv

# 添加src到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# 加载环境变量
project_root = Path(__file__).parent.parent.parent
env_file = project_root / ".env"
if env_file.exists():
    load_dotenv(env_file)
    print(f"✓ 已加载环境变量文件: {env_file}")

from compiler.config import CompilerConfig
from compiler.compiler_factory import CompilerFactory


def test_basic_compilation():
    """测试基本编译功能"""
    print("\n" + "="*60)
    print("测试 Gemini 编译器 - 基本编译功能")
    print("="*60)
    
    # 创建测试 PIM 文件
    test_dir = Path("./test_output")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    test_dir.mkdir()
    
    pim_file = test_dir / "user_management.md"
    pim_content = """# 用户管理系统

## 业务实体

### 用户 (User)
用户是系统的核心实体，代表使用系统的人员。

属性：
- 邮箱：用户的电子邮件地址，必须唯一
- 用户名：用户的登录名，必须唯一
- 密码：用户的登录密码，需要加密存储
- 状态：用户账号状态（激活/未激活）
- 创建时间：账号创建的时间

## 业务服务

### 用户服务 (UserService)
负责用户相关的所有业务操作。

方法：
1. 注册用户
   - 输入：邮箱、用户名、密码
   - 验证：邮箱格式、用户名格式、密码强度
   - 业务规则：邮箱和用户名必须唯一
   - 输出：创建成功的用户信息

2. 用户登录
   - 输入：用户名/邮箱、密码
   - 验证：账号存在性、密码正确性
   - 业务规则：只有激活的用户才能登录
   - 输出：登录凭证

3. 查询用户
   - 输入：用户ID
   - 输出：用户信息（不包含密码）

## 业务流程

### 用户注册流程
1. 接收用户提交的注册信息
2. 验证邮箱格式是否正确
3. 验证用户名格式是否符合要求
4. 检查邮箱是否已被注册
5. 检查用户名是否已被占用
6. 加密用户密码
7. 创建用户账号
8. 发送激活邮件（可选）
9. 返回注册结果

### 用户登录流程
1. 接收用户提交的登录凭证
2. 查找对应的用户账号
3. 验证密码是否正确
4. 检查账号是否已激活
5. 生成登录令牌
6. 记录登录日志
7. 返回登录结果和令牌
"""
    
    with open(pim_file, 'w', encoding='utf-8') as f:
        f.write(pim_content)
    
    print(f"\n1. 创建测试 PIM 文件: {pim_file}")
    
    # 创建编译器配置
    config = CompilerConfig(
        target_platform="fastapi",
        output_dir=test_dir / "output",
        llm_provider="deepseek",
        auto_test=False,  # 先关闭自动测试
        verbose=True
    )
    
    print(f"\n2. 编译器配置:")
    for key, value in config.to_dict().items():
        print(f"   - {key}: {value}")
    
    # 创建编译器
    print(f"\n3. 创建编译器实例...")
    compiler = CompilerFactory.create_compiler(config)
    
    # 执行编译
    print(f"\n4. 开始编译...")
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
        print(f"   - 编译时间: {result.compilation_time:.2f} 秒")
    
    # 检查生成的文件
    if result.success and result.code_dir:
        print(f"\n6. 检查生成的文件:")
        
        # 统计文件
        all_files = list(result.code_dir.rglob("*"))
        py_files = [f for f in all_files if f.suffix == ".py"]
        
        print(f"   - 总文件数: {len(all_files)}")
        print(f"   - Python 文件数: {len(py_files)}")
        
        # 检查关键文件
        key_files = [
            "src/main.py",
            "src/models/user.py",
            "src/schemas/user.py",
            "src/api/users.py",
            "src/services/user_service.py",
            "requirements.txt",
            "README.md"
        ]
        
        print(f"\n   关键文件检查:")
        for key_file in key_files:
            file_path = result.code_dir / key_file
            if file_path.exists():
                size = file_path.stat().st_size
                print(f"   ✓ {key_file} ({size} 字节)")
            else:
                # 尝试其他可能的路径
                found = False
                for f in all_files:
                    if f.name == Path(key_file).name:
                        size = f.stat().st_size
                        print(f"   ✓ {f.relative_to(result.code_dir)} ({size} 字节)")
                        found = True
                        break
                if not found:
                    print(f"   ✗ {key_file} 未找到")
    
    return result


def test_with_auto_fix():
    """测试带自动修复的编译"""
    print("\n" + "="*60)
    print("测试 Gemini 编译器 - 自动修复功能")
    print("="*60)
    
    # 使用之前的 PIM 文件
    pim_file = Path("./test_output/user_management.md")
    if not pim_file.exists():
        print("请先运行基本编译测试")
        return None
    
    # 创建新的输出目录
    output_dir = Path("./test_output/output_with_fix")
    if output_dir.exists():
        shutil.rmtree(output_dir)
    
    # 创建编译器配置（启用自动修复）
    config = CompilerConfig(
        target_platform="fastapi",
        output_dir=output_dir,
        llm_provider="deepseek",
        auto_test=True,
        auto_fix_lint=True,
        auto_fix_tests=True,
        verbose=True
    )
    
    print(f"\n1. 编译器配置（启用自动修复）:")
    print(f"   - auto_test: {config.auto_test}")
    print(f"   - auto_fix_lint: {config.auto_fix_lint}")
    print(f"   - auto_fix_tests: {config.auto_fix_tests}")
    
    # 创建编译器并编译
    print(f"\n2. 开始编译（含自动修复）...")
    compiler = CompilerFactory.create_compiler(config)
    result = compiler.compile(pim_file)
    
    # 输出结果
    print(f"\n3. 编译结果:")
    print(f"   - 成功: {result.success}")
    if result.test_results:
        print(f"\n   测试结果:")
        print(f"   - Lint 通过: {result.test_results['lint']['passed']}")
        print(f"   - Lint 修复: {result.test_results['lint']['fixed']}")
        print(f"   - 测试通过: {result.test_results['tests']['passed']}")
        print(f"   - 测试修复: {result.test_results['tests']['fixed']}")
    
    return result


if __name__ == "__main__":
    # 运行基本测试
    print("开始测试新型 Gemini 编译器...")
    
    # 测试1：基本编译
    result1 = test_basic_compilation()
    
    if result1 and result1.success:
        # 测试2：带自动修复的编译
        # 注意：这个测试可能需要较长时间
        print("\n\n是否继续测试自动修复功能？这可能需要几分钟时间。")
        print("如果要测试，请手动调用 test_with_auto_fix()")
        # result2 = test_with_auto_fix()
    
    print("\n\n测试完成！")
    print("生成的代码位于: ./test_output/output/")