#!/usr/bin/env python3
"""修复生成代码的测试导入问题"""

import os
import sys
from pathlib import Path

def fix_test_imports(project_dir):
    """修复测试文件的导入问题"""
    project_dir = Path(project_dir)
    tests_dir = project_dir / "tests"
    
    if not tests_dir.exists():
        print(f"测试目录不存在: {tests_dir}")
        return
    
    # 查找所有测试文件
    test_files = list(tests_dir.glob("test_*.py"))
    
    for test_file in test_files:
        print(f"修复文件: {test_file}")
        
        # 读取文件内容
        content = test_file.read_text(encoding='utf-8')
        
        # 修复导入路径
        lines = content.split('\n')
        fixed_lines = []
        
        for line in lines:
            # 添加 sys.path 修复
            if line.strip().startswith('import pytest'):
                fixed_lines.append('import sys')
                fixed_lines.append('from pathlib import Path')
                fixed_lines.append('sys.path.insert(0, str(Path(__file__).parent.parent))')
                fixed_lines.append('')
                fixed_lines.append(line)
            else:
                fixed_lines.append(line)
        
        # 写回文件
        test_file.write_text('\n'.join(fixed_lines), encoding='utf-8')
        print(f"✅ 修复完成: {test_file}")

def run_tests_with_fix(project_dir):
    """修复并运行测试"""
    project_dir = Path(project_dir)
    
    # 先修复导入
    fix_test_imports(project_dir)
    
    # 运行测试
    os.chdir(project_dir)
    os.system("python -m pytest tests/ -v")

if __name__ == "__main__":
    # 修复最新生成的项目
    latest_project = "/home/guci/aiProjects/mda/pim-compiler/output/react_agent_with_test/用户管理_pim_react-agent/generated/user_management"
    
    if os.path.exists(latest_project):
        print(f"修复项目: {latest_project}")
        run_tests_with_fix(latest_project)
    else:
        print(f"项目不存在: {latest_project}")