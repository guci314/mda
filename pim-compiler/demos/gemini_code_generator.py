#!/usr/bin/env python3
"""
gemini_code_generator.py - 基于 Gemini CLI 的代码生成器
使用上下文管理实现多步骤代码生成工作流
"""

import subprocess
import json
import os
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path


class GeminiCodeGenerator:
    """Gemini 代码生成器 - 专门用于代码生成任务"""
    
    def __init__(self, project_name: str, output_dir: str = "."):
        self.project_name = project_name
        self.output_dir = Path(output_dir) / project_name
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.history: List[Dict[str, Any]] = []
        self.generated_files: Dict[str, str] = {}
        self.context_window = 8  # 保留最近的4轮对话
        
    def _build_context_prompt(self, message: str) -> str:
        """构建带上下文的提示"""
        if not self.history:
            return message
        
        # 获取最近的历史
        recent = self.history[-self.context_window:]
        
        context_parts = [
            f"项目：{self.project_name}",
            "之前的对话历史：\n"
        ]
        
        for item in recent:
            role = "开发者" if item['role'] == 'user' else "助手"
            # 截断过长的内容
            content = item['content']
            if len(content) > 500:
                content = content[:500] + "..."
            context_parts.append(f"{role}: {content}\n")
        
        if self.generated_files:
            context_parts.append("\n已生成的文件：")
            for filename in self.generated_files:
                context_parts.append(f"- {filename}")
        
        context_parts.append(f"\n当前任务: {message}")
        context_parts.append("\n请基于项目上下文完成任务。如果需要生成代码，请提供完整的代码。")
        
        return "\n".join(context_parts)
    
    def generate(self, task: str, save_as: Optional[str] = None) -> str:
        """执行代码生成任务"""
        prompt = self._build_context_prompt(task)
        
        try:
            result = subprocess.run(
                ['gemini', '-c', '-p', prompt],
                capture_output=True,
                text=True,
                check=True,
                timeout=60
            )
            
            response = result.stdout.strip()
            
            # 记录历史
            self.history.append({
                'timestamp': datetime.now().isoformat(),
                'role': 'user',
                'content': task
            })
            self.history.append({
                'timestamp': datetime.now().isoformat(),
                'role': 'assistant',
                'content': response
            })
            
            # 如果指定了文件名，保存代码
            if save_as and response:
                self.save_code(response, save_as)
            
            return response
            
        except subprocess.TimeoutExpired:
            return "错误: 请求超时"
        except subprocess.CalledProcessError as e:
            return f"错误: {e.stderr}"
        except Exception as e:
            return f"错误: {str(e)}"
    
    def save_code(self, content: str, filename: str):
        """从响应中提取代码并保存"""
        # 提取代码块
        code_blocks = self._extract_code_blocks(content)
        
        if code_blocks:
            # 如果有多个代码块，使用第一个主要的
            code = code_blocks[0]['code']
            
            # 保存文件
            file_path = self.output_dir / filename
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(code)
            
            self.generated_files[filename] = str(file_path)
            print(f"✅ 已保存: {file_path}")
        else:
            # 如果没有代码块，尝试保存整个内容
            if any(keyword in content.lower() for keyword in ['def ', 'class ', 'import ', 'function', '```']):
                file_path = self.output_dir / filename
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.generated_files[filename] = str(file_path)
                print(f"✅ 已保存: {file_path}")
    
    def _extract_code_blocks(self, content: str) -> List[Dict[str, str]]:
        """从响应中提取代码块"""
        import re
        
        code_blocks = []
        
        # 匹配 ```language\ncode\n``` 格式
        pattern = r'```(\w+)?\n(.*?)\n```'
        matches = re.findall(pattern, content, re.DOTALL)
        
        for lang, code in matches:
            code_blocks.append({
                'language': lang or 'plain',
                'code': code.strip()
            })
        
        return code_blocks
    
    def create_project(self, project_type: str = "fastapi"):
        """创建完整的项目"""
        print(f"🚀 创建 {project_type} 项目: {self.project_name}")
        print("=" * 60)
        
        if project_type == "fastapi":
            self._create_fastapi_project()
        elif project_type == "cli":
            self._create_cli_project()
        else:
            print(f"不支持的项目类型: {project_type}")
    
    def _create_fastapi_project(self):
        """创建 FastAPI 项目"""
        steps = [
            ("设计数据模型", "models.py"),
            ("创建 Pydantic schemas", "schemas.py"),
            ("实现 CRUD 操作", "crud.py"),
            ("创建 API 路由", "routers.py"),
            ("创建主应用", "main.py"),
            ("生成配置文件", "config.py"),
            ("创建 requirements.txt", "requirements.txt"),
            ("编写测试", "test_main.py"),
            ("创建 README", "README.md")
        ]
        
        # 步骤1: 项目规划
        print("\n[步骤1] 项目规划")
        self.generate(
            f"设计一个{self.project_name}的FastAPI项目结构，包括需要的模块和功能"
        )
        
        # 步骤2: 数据模型
        print("\n[步骤2] 创建数据模型")
        self.generate(
            "创建SQLAlchemy数据模型，包括User和相关的业务实体",
            save_as="models.py"
        )
        
        # 步骤3: Pydantic schemas
        print("\n[步骤3] 创建 Pydantic schemas")
        self.generate(
            "基于models.py中的SQLAlchemy模型，创建对应的Pydantic schemas",
            save_as="schemas.py"
        )
        
        # 步骤4: CRUD 操作
        print("\n[步骤4] 实现 CRUD 操作")
        self.generate(
            "基于models.py，创建CRUD操作函数，使用SQLAlchemy",
            save_as="crud.py"
        )
        
        # 步骤5: API 路由
        print("\n[步骤5] 创建 API 路由")
        self.generate(
            "基于schemas.py和crud.py，创建FastAPI路由，包括所有CRUD端点",
            save_as="routers.py"
        )
        
        # 步骤6: 主应用
        print("\n[步骤6] 创建主应用")
        self.generate(
            "创建FastAPI主应用文件，包括应用初始化、路由注册、CORS配置等",
            save_as="main.py"
        )
        
        # 步骤7: 配置文件
        print("\n[步骤7] 生成配置")
        self.generate(
            "创建配置文件，包括数据库连接、环境变量等配置",
            save_as="config.py"
        )
        
        # 步骤8: 依赖文件
        print("\n[步骤8] 生成 requirements.txt")
        self.generate(
            "基于项目使用的所有库，生成requirements.txt文件",
            save_as="requirements.txt"
        )
        
        # 步骤9: 测试文件
        print("\n[步骤9] 编写测试")
        self.generate(
            "为main.py创建pytest测试文件，测试主要的API端点",
            save_as="test_main.py"
        )
        
        # 步骤10: 文档
        print("\n[步骤10] 创建 README")
        self.generate(
            "创建项目README.md，包括项目介绍、安装说明、API文档链接等",
            save_as="README.md"
        )
        
        # 保存项目信息
        self.save_project_info()
    
    def _create_cli_project(self):
        """创建 CLI 项目"""
        print("\n[步骤1] 项目规划")
        self.generate(
            f"设计一个{self.project_name}的Python CLI工具项目结构"
        )
        
        print("\n[步骤2] 创建主程序")
        self.generate(
            "创建CLI主程序，使用argparse处理命令行参数",
            save_as="cli.py"
        )
        
        print("\n[步骤3] 创建核心模块")
        self.generate(
            "基于CLI功能，创建核心业务逻辑模块",
            save_as="core.py"
        )
        
        print("\n[步骤4] 创建工具模块")
        self.generate(
            "创建工具函数模块",
            save_as="utils.py"
        )
        
        print("\n[步骤5] 生成配置")
        self.generate(
            "创建setup.py文件，使项目可安装",
            save_as="setup.py"
        )
        
        print("\n[步骤6] 创建测试")
        self.generate(
            "创建pytest测试文件",
            save_as="test_cli.py"
        )
        
        print("\n[步骤7] 创建文档")
        self.generate(
            "创建README.md文档",
            save_as="README.md"
        )
        
        self.save_project_info()
    
    def save_project_info(self):
        """保存项目信息"""
        project_info = {
            'project_name': self.project_name,
            'created_at': datetime.now().isoformat(),
            'files': self.generated_files,
            'total_interactions': len(self.history) // 2
        }
        
        info_file = self.output_dir / 'project_info.json'
        with open(info_file, 'w', encoding='utf-8') as f:
            json.dump(project_info, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 项目创建完成！")
        print(f"📁 项目位置: {self.output_dir}")
        print(f"📄 生成文件: {len(self.generated_files)} 个")
        
        # 保存完整历史
        history_file = self.output_dir / 'generation_history.json'
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)


def main():
    """主函数"""
    import sys
    import random
    
    print("Gemini 代码生成器")
    print("=" * 60)
    
    # 预定义的项目示例
    demo_projects = [
        ("task_manager_api", "fastapi", "任务管理系统 API"),
        ("blog_platform", "fastapi", "博客平台后端"),
        ("ecommerce_api", "fastapi", "电商系统 API"),
        ("file_organizer", "cli", "文件整理工具"),
        ("log_analyzer", "cli", "日志分析工具"),
        ("backup_tool", "cli", "备份管理工具")
    ]
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--help":
            print("\n使用方法:")
            print("  # 交互式使用")
            print("  python3 gemini_code_generator.py")
            print()
            print("  # 命令行使用")
            print("  python3 gemini_code_generator.py my_blog_api fastapi")
            print("  python3 gemini_code_generator.py my_cli_tool cli")
            print()
            print("  # 使用演示项目")
            print("  python3 gemini_code_generator.py --demo")
            return
        elif sys.argv[1] == "--demo":
            # 随机选择一个演示项目
            project_name, project_type, description = random.choice(demo_projects)
            print(f"\n🎲 随机选择演示项目: {description}")
            print(f"   项目名称: {project_name}")
            print(f"   项目类型: {project_type}")
        else:
            project_name = sys.argv[1]
            project_type = sys.argv[2] if len(sys.argv) > 2 else "fastapi"
    else:
        # 自动选择一个演示项目，无需用户输入
        project_name, project_type, description = random.choice(demo_projects)
        print(f"\n🚀 自动生成演示项目: {description}")
        print(f"   项目名称: {project_name}")
        print(f"   项目类型: {project_type}")
        print("\n提示: 使用 'python3 gemini_code_generator.py --help' 查看更多选项")
    
    print("\n开始生成项目...")
    print("-" * 60)
    
    generator = GeminiCodeGenerator(project_name)
    generator.create_project(project_type)


if __name__ == "__main__":
    main()