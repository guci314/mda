#!/usr/bin/env python3
"""改进版ReactAgentGenerator v3，包含正确的Python包结构指导"""

import os
import sys
import time
import logging
from pathlib import Path
from datetime import datetime

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 手动导入必要的内容
from dotenv import load_dotenv
load_dotenv()

# 处理代理设置问题 - 临时禁用
os.environ.pop('http_proxy', None)
os.environ.pop('https_proxy', None)
os.environ.pop('all_proxy', None)

# 直接复制ReactAgentGenerator的代码，避免导入问题
from typing import Dict, Any, List, Optional
from enum import Enum
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain_community.cache import SQLiteCache
from langchain_core.globals import set_llm_cache
from langchain.memory import (
    ConversationBufferMemory,
    ConversationSummaryBufferMemory,
    ConversationBufferWindowMemory,
)
from langchain_community.chat_message_histories import (
    SQLChatMessageHistory,
)
from pydantic import BaseModel, Field

# 导入 DeepSeek token 计数修复
try:
    from deepseek_token_counter import patch_deepseek_token_counting
except ImportError:
    logger.warning("deepseek_token_counter not found, token counting may fail")
    patch_deepseek_token_counting = None

# 设置缓存 - 使用绝对路径确保缓存生效
cache_path = os.path.join(os.path.dirname(__file__), ".langchain.db")
set_llm_cache(SQLiteCache(database_path=cache_path))

# 记忆级别枚举
class MemoryLevel(str, Enum):
    """记忆级别"""
    NONE = "none"              # 无记忆 - 快速简单
    SMART = "summary_buffer"   # 智能缓冲 - 平衡方案
    PRO = "sqlite"            # 持久存储 - 专业项目

# 工具定义
class FileInput(BaseModel):
    file_path: str = Field(description="文件路径")
    content: str = Field(description="文件内容")

class DirectoryInput(BaseModel):
    directory_path: str = Field(description="目录路径")

class TestInput(BaseModel):
    test_dir: Optional[str] = Field(default="tests", description="测试目录")
    verbose: bool = Field(default=True, description="是否显示详细输出")

class InstallInput(BaseModel):
    requirements_file: str = Field(default="requirements.txt", description="依赖文件路径")

class GeneratorConfig:
    def __init__(self, platform, output_dir, additional_config=None, 
                 memory_level=MemoryLevel.SMART, session_id=None, 
                 max_token_limit=30000, db_path=None,
                 knowledge_file="先验知识.md"):  # 增加到 30K tokens
        self.platform = platform
        self.output_dir = output_dir
        self.additional_config = additional_config or {}
        # 记忆配置
        self.memory_level = memory_level
        self.session_id = session_id or f"session_{int(time.time())}"
        self.max_token_limit = max_token_limit  # 默认 30K，约占用一半的上下文窗口
        self.db_path = db_path or os.path.join(os.path.dirname(__file__), "memory.db")
        # 知识文件路径
        self.knowledge_file = knowledge_file

class ReactAgentGenerator:
    """React Agent 代码生成器 - 支持三级记忆"""
    
    def __init__(self, config: GeneratorConfig):
        self.config = config
        self.output_dir = Path(config.output_dir)
        self.llm = self._create_llm()
        self.memory = self._create_memory()
        self.prior_knowledge = self._load_prior_knowledge()
        logger.info(f"ReactAgent initialized with memory level: {config.memory_level}")
        if self.prior_knowledge:
            logger.info(f"Loaded prior knowledge from: {config.knowledge_file}")
        
    def _create_llm(self):
        """创建语言模型"""
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError("DEEPSEEK_API_KEY not set")
        
        # 创建ChatOpenAI实例  
        llm = ChatOpenAI(
            model="deepseek-chat",
            api_key=api_key,
            base_url="https://api.deepseek.com/v1",
            temperature=0,  # 设置为0以确保输出一致，充分利用缓存
            max_tokens=4000
        )
        
        # 应用 DeepSeek token 计数修复（可通过环境变量禁用）
        if patch_deepseek_token_counting and not os.environ.get('DISABLE_TOKEN_PATCH'):
            try:
                llm = patch_deepseek_token_counting(llm)
                logger.info("Applied DeepSeek token counting patch")
            except Exception as e:
                logger.warning(f"Failed to apply token counting patch: {e}")
        
        return llm
    
    def _create_memory(self):
        """根据配置创建记忆系统"""
        if self.config.memory_level == MemoryLevel.NONE:
            logger.info("Memory disabled - using stateless mode")
            return None
            
        elif self.config.memory_level == MemoryLevel.SMART:
            # 在虚拟环境中使用窗口记忆避免token计数问题
            k = min(50, self.config.max_token_limit // 600)  # 大约每条消息600 tokens
            logger.info(f"Using smart memory (window buffer) with k={k} messages")
            return ConversationBufferWindowMemory(
                k=k,
                memory_key="chat_history",
                return_messages=True
            )
            
        elif self.config.memory_level == MemoryLevel.PRO:
            logger.info(f"Using persistent memory (SQLite) - session: {self.config.session_id}")
            # 确保数据库目录存在
            db_dir = os.path.dirname(self.config.db_path)
            if db_dir:
                os.makedirs(db_dir, exist_ok=True)
                
            message_history = SQLChatMessageHistory(
                session_id=self.config.session_id,
                connection_string=f"sqlite:///{self.config.db_path}"
            )
            return ConversationBufferMemory(
                memory_key="chat_history",
                chat_memory=message_history,
                return_messages=True
            )
    
    def _load_prior_knowledge(self) -> str:
        """加载先验知识"""
        knowledge_path = Path(self.config.knowledge_file)
        if knowledge_path.exists():
            try:
                content = knowledge_path.read_text(encoding='utf-8')
                # 转义单个大括号以避免被误认为是模板变量
                # 只转义未成对的大括号
                import re
                # 先保护已经转义的大括号
                content = content.replace('{{', '\x00DOUBLE_OPEN\x00')
                content = content.replace('}}', '\x00DOUBLE_CLOSE\x00')
                # 转义单个大括号
                content = content.replace('{', '{{')
                content = content.replace('}', '}}')
                # 恢复已经转义的大括号
                content = content.replace('\x00DOUBLE_OPEN\x00', '{{')
                content = content.replace('\x00DOUBLE_CLOSE\x00', '}}')
                return content
            except Exception as e:
                logger.warning(f"Failed to load prior knowledge: {e}")
                return ""
        else:
            logger.info(f"No prior knowledge file found at: {knowledge_path}")
            return ""
    
    def generate_psm(self, pim_content: str) -> str:
        """生成PSM"""
        prompt = f"""你是一个专业的软件架构师，负责生成 PSM（Platform Specific Model）。

目标平台: {self.config.platform}

请根据以下PIM生成详细的PSM文档：

{pim_content}

要求：
1. 包含详细的数据模型定义（字段类型、约束等）
2. API端点设计（RESTful）  
3. 服务层方法定义
4. 认证和权限控制
5. 数据库设计

请使用Markdown格式输出。"""

        response = self.llm.invoke(prompt)
        return response.content
    
    def generate_code(self, psm_content: str, output_dir: str):
        """使用React Agent生成代码"""
        # 创建工具
        @tool("write_file", args_schema=FileInput)
        def write_file(file_path: str, content: str) -> str:
            """写入文件"""
            try:
                file_full_path = Path(output_dir) / file_path
                file_full_path.parent.mkdir(parents=True, exist_ok=True)
                file_full_path.write_text(content, encoding='utf-8')
                return f"Successfully wrote file: {file_path}"
            except Exception as e:
                return f"Error writing file: {str(e)}"

        class ReadFileInput(BaseModel):
            file_path: str = Field(description="文件路径")
        
        @tool("read_file", args_schema=ReadFileInput)
        def read_file(file_path: str) -> str:
            """读取文件"""
            try:
                file_full_path = Path(output_dir) / file_path
                if not file_full_path.exists():
                    return f"File not found: {file_path}"
                content = file_full_path.read_text(encoding='utf-8')
                return content
            except Exception as e:
                return f"Error reading file: {str(e)}"

        @tool("create_directory", args_schema=DirectoryInput)
        def create_directory(directory_path: str) -> str:
            """创建目录"""
            try:
                dir_full_path = Path(output_dir) / directory_path
                dir_full_path.mkdir(parents=True, exist_ok=True)
                return f"Successfully created directory: {directory_path}"
            except Exception as e:
                return f"Error creating directory: {str(e)}"

        @tool("list_directory", args_schema=DirectoryInput)
        def list_directory(directory_path: str = ".") -> str:
            """列出目录内容"""
            try:
                dir_full_path = Path(output_dir) / directory_path
                if not dir_full_path.exists():
                    return f"Directory not found: {directory_path}"
                items = []
                for item in dir_full_path.iterdir():
                    if item.is_dir():
                        items.append(f"[DIR] {item.name}")
                    else:
                        items.append(f"[FILE] {item.name}")
                return "\n".join(items) if items else "Empty directory"
            except Exception as e:
                return f"Error listing directory: {str(e)}"

        @tool("install_dependencies", args_schema=InstallInput)
        def install_dependencies(requirements_file: str = "requirements.txt") -> str:
            """安装Python依赖包"""
            try:
                import subprocess
                
                # 查找requirements文件
                req_path = Path(output_dir) / requirements_file
                if not req_path.exists():
                    # 尝试在子目录中查找
                    for subdir in Path(output_dir).iterdir():
                        if subdir.is_dir():
                            temp_path = subdir / requirements_file
                            if temp_path.exists():
                                req_path = temp_path
                                break
                    else:
                        return f"Requirements file not found: {requirements_file}"
                
                # 获取当前Python解释器
                python_exe = sys.executable
                
                # 运行pip install
                result = subprocess.run(
                    [python_exe, "-m", "pip", "install", "-r", str(req_path)],
                    capture_output=True,
                    text=True,
                    timeout=300  # 5分钟超时
                )
                
                output = f"Exit code: {result.returncode}\n"
                if result.stdout:
                    output += f"STDOUT:\n{result.stdout}\n"
                if result.stderr:
                    output += f"STDERR:\n{result.stderr}\n"
                
                if result.returncode == 0:
                    output += f"\nSuccessfully installed dependencies from {req_path}"
                else:
                    output += f"\nFailed to install dependencies"
                    
                return output
                
            except subprocess.TimeoutExpired:
                return "Installation timed out after 5 minutes"
            except Exception as e:
                return f"Error installing dependencies: {str(e)}"

        @tool("run_tests", args_schema=TestInput)  
        def run_tests(test_dir: Optional[str] = "tests", verbose: bool = True) -> str:
            """运行 pytest 测试"""
            try:
                import subprocess
                
                # 查找项目根目录（包含tests目录的目录）
                project_root = None
                
                # 首先在输出目录直接查找
                if (Path(output_dir) / test_dir).exists():
                    project_root = Path(output_dir)
                else:
                    # 在子目录中查找
                    for subdir in Path(output_dir).iterdir():
                        if subdir.is_dir() and (subdir / test_dir).exists():
                            project_root = subdir
                            break
                
                if not project_root:
                    return f"Test directory not found: {test_dir}. Searched in {output_dir} and subdirectories."
                
                # 获取当前Python解释器
                python_exe = sys.executable
                
                # 设置环境变量 - 添加项目根目录到PYTHONPATH
                env = os.environ.copy()
                env["PYTHONPATH"] = str(project_root) + ":" + env.get("PYTHONPATH", "")
                
                # 构建命令 - 从项目根目录运行pytest
                cmd = [python_exe, "-m", "pytest", test_dir, "-v", "-s", "--tb=short", "-x"]
                
                # 执行测试
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    env=env,
                    cwd=str(project_root),  # 在项目根目录运行
                    timeout=180  # 3分钟超时
                )
                
                output = f"Working directory: {project_root}\n"
                output += f"Test directory: {test_dir}\n"
                output += f"Python executable: {python_exe}\n"
                output += f"PYTHONPATH: {env['PYTHONPATH']}\n"
                output += f"Command: {' '.join(cmd)}\n"
                output += f"Exit code: {result.returncode}\n"
                if result.stdout:
                    output += f"STDOUT:\n{result.stdout}\n"
                if result.stderr:
                    output += f"STDERR:\n{result.stderr}\n"
                    
                return output
                
            except subprocess.TimeoutExpired:
                return "Test execution timed out after 3 minutes"
            except Exception as e:
                return f"Error running tests: {str(e)}"

        # 工具列表
        tools = [
            write_file,
            read_file,
            create_directory,
            list_directory,
            install_dependencies,
            run_tests
        ]
        
        # 系统提示词 - 领域无关的通用提示
        system_prompt = f"""你是一个专业的软件开发助手。

你的任务是根据提供的规范生成高质量的代码。

## 可用工具

你可以使用以下工具来完成任务：
- write_file: 创建或修改文件
- read_file: 读取文件内容  
- create_directory: 创建目录结构
- list_directory: 查看目录内容
- install_dependencies: 安装项目依赖
- run_tests: 执行测试验证

## 工作原则

1. 仔细理解任务要求
2. 按照最佳实践生成代码
3. 确保代码结构清晰、可维护
4. 编写必要的测试用例
5. 验证生成的代码正确性

## 输出目录

所有文件操作都相对于: {self.output_dir}
"""

        # 如果有先验知识，添加到系统提示词中
        if self.prior_knowledge:
            system_prompt += f"""

## 领域知识

以下是相关的领域知识和最佳实践，请在生成代码时严格遵循：

{self.prior_knowledge}
"""

        # 创建prompt - 根据是否有记忆调整
        messages = [("system", system_prompt)]
        
        # 如果启用了记忆，添加记忆占位符
        if self.memory is not None:
            messages.append(MessagesPlaceholder(variable_name="chat_history"))
            
        messages.extend([
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}")
        ])
        
        prompt = ChatPromptTemplate.from_messages(messages)
        
        # 创建agent
        agent = create_tool_calling_agent(self.llm, tools, prompt)
        
        # 创建executor - 根据是否有记忆配置
        executor_config = {
            "agent": agent,
            "tools": tools,
            "verbose": True,
            "max_iterations": 50,  # 增加迭代次数
            "handle_parsing_errors": True
        }
        
        # 如果有记忆，添加到executor
        if self.memory is not None:
            executor_config["memory"] = self.memory
            
        executor = AgentExecutor(**executor_config)
        
        # 执行生成
        input_prompt = f"""请根据以下PSM生成完整的{self.config.platform}应用代码：

{psm_content}

请创建完整的项目结构，包括所有必要的文件。

重要提醒：
1. 每个Python目录都需要 __init__.py 文件
2. 测试文件需要能够正确导入应用代码
3. 生成代码后必须安装依赖并运行测试
4. 只有所有测试通过，任务才算完成"""

        executor.invoke({"input": input_prompt})


def main():
    """主函数 - 支持三级记忆配置"""
    import argparse
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="ReactAgent Generator with Memory Support")
    parser.add_argument("--memory", choices=["none", "smart", "pro"], 
                       default="smart", help="Memory level: none, smart, or pro")
    parser.add_argument("--session-id", type=str, help="Session ID for persistent memory")
    parser.add_argument("--max-tokens", type=int, default=30000,
                       help="Max token limit for smart memory (default: 30000, max: ~50000)")
    parser.add_argument("--pim-file", type=str, 
                       default="../models/domain/用户管理_pim.md", 
                       help="Path to PIM file")
    parser.add_argument("--output-dir", type=str, 
                       default="output/react_agent_v3", 
                       help="Output directory")
    parser.add_argument("--knowledge-file", type=str,
                       default="先验知识.md",
                       help="Path to prior knowledge file")
    args = parser.parse_args()
    
    # 配置
    pim_file = Path(args.pim_file)
    output_dir = Path(args.output_dir)
    
    # 根据memory参数映射到MemoryLevel
    memory_mapping = {
        "none": MemoryLevel.NONE,
        "smart": MemoryLevel.SMART,
        "pro": MemoryLevel.PRO
    }
    memory_level = memory_mapping[args.memory]
    
    logger.info(f"Using generator: react-agent (v3)")
    logger.info(f"Memory level: {args.memory}")
    logger.info(f"Target platform: fastapi")
    logger.info(f"Output directory: {output_dir}")
    logger.info(f"Knowledge file: {args.knowledge_file}")
    
    # 检查PIM文件
    if not pim_file.exists():
        logger.error(f"PIM file not found: {pim_file}")
        return 1
    
    # 读取PIM内容
    pim_content = pim_file.read_text(encoding='utf-8')
    
    # 创建输出目录
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 创建配置 - 包含记忆配置和知识文件
    config = GeneratorConfig(
        platform="fastapi",
        output_dir=str(output_dir),
        additional_config={},
        memory_level=memory_level,
        session_id=args.session_id,
        max_token_limit=args.max_tokens,
        knowledge_file=args.knowledge_file
    )
    
    try:
        # 创建生成器
        generator = ReactAgentGenerator(config)
        logger.info("Initialized ReactAgentGenerator v3 with proper Python package guidance")
        logger.info(f"Starting compilation of {pim_file}")
        
        # 步骤1：生成PSM
        logger.info("Step 1: Generating PSM...")
        start_time = time.time()
        psm_content = generator.generate_psm(pim_content)
        psm_time = time.time() - start_time
        logger.info(f"PSM generated in {psm_time:.2f} seconds")
        
        # 保存PSM
        psm_file = output_dir / "user_management_psm.md"
        psm_file.write_text(psm_content, encoding='utf-8')
        
        # 步骤2：生成代码
        logger.info("Step 2: Generating code with proper package structure...")
        print("\n[1m> Entering new AgentExecutor chain...[0m")
        
        start_time = time.time()
        generator.generate_code(psm_content, str(output_dir))
        code_time = time.time() - start_time
        
        print("[1m> Finished chain.[0m")
        logger.info(f"Code generated and tested in {code_time:.2f} seconds")
        
        # 统计
        python_files = list(output_dir.rglob("*.py"))
        total_files = list(output_dir.rglob("*.*"))
        
        print("\n" + "=" * 50)
        print("✅ Compilation Successful!")
        print("=" * 50)
        print(f"Generator: react-agent v3")
        print(f"Platform: fastapi")
        print(f"Output: {output_dir}")
        print(f"\nMemory Configuration:")
        print(f"  - Level: {args.memory}")
        if args.memory == "smart":
            print(f"  - Token limit: {config.max_token_limit}")
        elif args.memory == "pro":
            print(f"  - Session ID: {config.session_id}")
            print(f"  - Database: {config.db_path}")
        print(f"\nStatistics:")
        print(f"  - PSM generation: {psm_time:.2f}s")
        print(f"  - Code generation & testing: {code_time:.2f}s")
        print(f"  - Total time: {psm_time + code_time:.2f}s")
        print(f"  - Files generated: {len(total_files)}")
        print(f"  - Python files: {len(python_files)}")
        
        # 保存日志
        log_file = output_dir / "compile_output.log"
        with open(log_file, 'a') as f:
            f.write(f"\n{'='*50}\n")
            f.write(f"Compilation completed at {datetime.now()}\n")
            f.write(f"Total time: {psm_time + code_time:.2f}s\n")
            f.write(f"Files generated: {len(total_files)}\n")
        
        print("\nNext steps:")
        print(f"  cd {output_dir}")
        print("  python -m uvicorn <app_name>.main:app --reload")
        
        return 0
        
    except Exception as e:
        logger.error(f"Compilation failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())