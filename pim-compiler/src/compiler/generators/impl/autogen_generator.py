"""
Autogen 代码生成器实现
使用 Microsoft Autogen 框架进行多 Agent 协作代码生成
"""

import os
import time
from pathlib import Path
from typing import Optional, Dict, List, Any
import logging
import json

try:
    import autogen
    from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager
except ImportError:
    raise ImportError("Please install autogen: pip install pyautogen")

from ..base_generator import BaseGenerator, GeneratorConfig, GenerationResult


class AutogenGenerator(BaseGenerator):
    """Autogen 代码生成器
    
    使用多个专门的 Agent 协作完成代码生成任务：
    - Architect Agent: 负责系统架构设计
    - Model Agent: 负责数据模型设计
    - API Agent: 负责 API 接口设计
    - Code Agent: 负责具体代码实现
    - Review Agent: 负责代码审查和优化
    """
    
    def setup(self):
        """初始化设置"""
        # 设置 LLM 配置
        api_key = self.config.api_key or os.getenv("DEEPSEEK_API_KEY", os.getenv("OPENAI_API_KEY"))
        api_base = self.config.api_base or os.getenv("DEEPSEEK_BASE_URL", os.getenv("OPENAI_API_BASE"))
        model = self.config.model or os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
        
        if not api_key:
            raise ValueError("API key not provided. Set DEEPSEEK_API_KEY or OPENAI_API_KEY or provide in config")
        
        # 配置 LLM
        self.llm_config = {
            "model": model,
            "api_key": api_key,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens
        }
        
        if api_base:
            self.llm_config["api_base"] = api_base
        
        # 配置代码执行（关闭以提高安全性）
        self.code_execution_config = {
            "work_dir": "autogen_workspace",
            "use_docker": False,
        }
        
        self.logger.info(f"Initialized Autogen with model: {model}")
    
    def generate_psm(
        self, 
        pim_content: str, 
        platform: str = "fastapi",
        output_dir: Optional[Path] = None
    ) -> GenerationResult:
        """从 PIM 生成 PSM"""
        start_time = time.time()
        
        if output_dir is None:
            output_dir = Path.cwd()
        
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建工作目录
        work_dir = output_dir / "autogen_workspace"
        work_dir.mkdir(exist_ok=True)
        
        try:
            # 创建专门的 PSM 生成 Agent
            psm_architect = AssistantAgent(
                name="PSM_Architect",
                system_message=f"""You are a Platform Specific Model (PSM) architect.
                Your task is to convert Platform Independent Models (PIM) to PSM for {platform}.
                
                Target platform: {platform}
                Framework: {self._get_framework_for_platform(platform)}
                ORM: {self._get_orm_for_platform(platform)}
                Validation: {self._get_validation_lib_for_platform(platform)}
                
                Generate detailed PSM including:
                1. Data models with specific types and constraints
                2. API endpoints following RESTful conventions
                3. Service layer specifications
                4. Business rules and validations
                """,
                llm_config=self.llm_config
            )
            
            # User Proxy 用于接收结果
            user_proxy = UserProxyAgent(
                name="User",
                human_input_mode="NEVER",
                max_consecutive_auto_reply=0,
                code_execution_config=False
            )
            
            # 开始对话
            psm_prompt = f"""Convert the following PIM to PSM for {platform}:

```markdown
{pim_content}
```

Save the PSM as a markdown document."""
            
            # 使用 initiate_chat 进行同步对话
            chat_result = user_proxy.initiate_chat(
                psm_architect,
                message=psm_prompt,
                max_turns=3
            )
            
            # 从对话历史中提取 PSM 内容
            psm_content = self._extract_psm_from_chat(chat_result)
            
            if psm_content:
                # 保存 PSM 文件
                psm_file = output_dir / "psm.md"
                psm_file.write_text(psm_content, encoding='utf-8')
                
                return GenerationResult(
                    success=True,
                    output_path=output_dir,
                    psm_content=psm_content,
                    generation_time=time.time() - start_time,
                    logs=self._format_chat_history(chat_result)
                )
            else:
                return GenerationResult(
                    success=False,
                    output_path=output_dir,
                    error_message="Failed to extract PSM from conversation",
                    generation_time=time.time() - start_time
                )
                
        except Exception as e:
            self.logger.error(f"Failed to generate PSM: {e}")
            return GenerationResult(
                success=False,
                output_path=output_dir,
                error_message=str(e),
                generation_time=time.time() - start_time
            )
    
    def generate_code(
        self, 
        psm_content: str, 
        output_dir: Path,
        platform: str = "fastapi"
    ) -> GenerationResult:
        """从 PSM 生成代码"""
        start_time = time.time()
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建工作目录
        work_dir = output_dir / "autogen_workspace"
        work_dir.mkdir(exist_ok=True)
        
        try:
            # 创建多个专门的 Agent
            agents = self._create_code_generation_agents(platform, output_dir)
            
            # 创建群聊
            group_chat = GroupChat(
                agents=list(agents.values()),
                messages=[],
                max_round=20,
                speaker_selection_method="round_robin"
            )
            
            # 创建群聊管理器
            manager = GroupChatManager(
                groupchat=group_chat,
                llm_config=self.llm_config
            )
            
            # 开始代码生成任务
            code_prompt = f"""Generate complete {platform} application code based on the following PSM:

```markdown
{psm_content}
```

Requirements:
1. Create proper project structure
2. Include all necessary __init__.py files
3. Follow best practices for {platform}
4. Generate requirements.txt
5. Create README.md with usage instructions

Start by creating the project structure, then implement each component."""
            
            # 启动对话
            chat_result = agents["user_proxy"].initiate_chat(
                manager,
                message=code_prompt
            )
            
            # 收集生成的文件
            code_files = self._collect_generated_files(output_dir)
            
            return GenerationResult(
                success=True,
                output_path=output_dir,
                code_files=code_files,
                generation_time=time.time() - start_time,
                logs=self._format_chat_history(chat_result)
            )
            
        except Exception as e:
            self.logger.error(f"Failed to generate code: {e}")
            return GenerationResult(
                success=False,
                output_path=output_dir,
                error_message=str(e),
                generation_time=time.time() - start_time
            )
    
    def _create_code_generation_agents(self, platform: str, output_dir: Path) -> Dict[str, Any]:
        """创建代码生成需要的多个 Agent"""
        
        # 架构师 Agent
        architect = AssistantAgent(
            name="Architect",
            system_message=f"""You are a software architect specializing in {platform}.
            Design the overall system architecture and project structure.
            Focus on:
            - Directory structure
            - Module organization
            - Dependency management
            - Configuration setup""",
            llm_config=self.llm_config
        )
        
        # 数据模型 Agent
        model_designer = AssistantAgent(
            name="ModelDesigner",
            system_message=f"""You are a data model expert for {platform}.
            Design and implement:
            - Database models using {self._get_orm_for_platform(platform)}
            - Data validation schemas using {self._get_validation_lib_for_platform(platform)}
            - Model relationships and constraints""",
            llm_config=self.llm_config
        )
        
        # API 设计 Agent
        api_designer = AssistantAgent(
            name="APIDesigner",
            system_message=f"""You are an API design expert for {platform}.
            Design and implement:
            - RESTful API endpoints
            - Request/response schemas
            - Error handling
            - API documentation""",
            llm_config=self.llm_config
        )
        
        # 代码实现 Agent
        coder = AssistantAgent(
            name="Coder",
            system_message=f"""You are a {platform} developer.
            Implement the actual code based on designs from other agents.
            Write clean, maintainable code with:
            - Proper error handling
            - Type hints
            - Documentation
            - Unit tests when appropriate""",
            llm_config=self.llm_config
        )
        
        # 代码审查 Agent
        reviewer = AssistantAgent(
            name="Reviewer",
            system_message="""You are a code reviewer.
            Review generated code for:
            - Code quality
            - Best practices
            - Security issues
            - Performance concerns
            Suggest improvements when necessary.""",
            llm_config=self.llm_config
        )
        
        # User Proxy（带文件操作功能）
        user_proxy = UserProxyAgent(
            name="user_proxy",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=10,
            is_termination_msg=lambda x: "TERMINATE" in x.get("content", ""),
            code_execution_config={
                "work_dir": str(output_dir),
                "use_docker": False,
                "last_n_messages": 3
            },
            function_map={
                "write_file": lambda path, content: self._write_file(output_dir, path, content),
                "create_directory": lambda path: self._create_directory(output_dir, path)
            }
        )
        
        return {
            "architect": architect,
            "model_designer": model_designer,
            "api_designer": api_designer,
            "coder": coder,
            "reviewer": reviewer,
            "user_proxy": user_proxy
        }
    
    def _write_file(self, base_dir: Path, file_path: str, content: str) -> str:
        """写入文件"""
        try:
            full_path = base_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content, encoding='utf-8')
            return f"File written: {file_path}"
        except Exception as e:
            return f"Error writing file: {e}"
    
    def _create_directory(self, base_dir: Path, dir_path: str) -> str:
        """创建目录"""
        try:
            full_path = base_dir / dir_path
            full_path.mkdir(parents=True, exist_ok=True)
            return f"Directory created: {dir_path}"
        except Exception as e:
            return f"Error creating directory: {e}"
    
    def _extract_psm_from_chat(self, chat_result: Any) -> Optional[str]:
        """从聊天记录中提取 PSM 内容"""
        # 查找包含 markdown 代码块的消息
        # Autogen ChatResult 对象有 chat_history 属性
        messages = getattr(chat_result, 'chat_history', []) if hasattr(chat_result, 'chat_history') else []
        for message in reversed(messages):
            content = message.get("content", "")
            if "```markdown" in content or "```md" in content:
                # 提取 markdown 内容
                import re
                pattern = r'```(?:markdown|md)\n(.*?)```'
                match = re.search(pattern, content, re.DOTALL)
                if match:
                    return match.group(1).strip()
        
        # 如果没有找到代码块，返回最后一条助手消息
        for message in reversed(messages):
            if message.get("role") == "assistant":
                return message.get("content", "")
        
        return None
    
    def _collect_generated_files(self, output_dir: Path) -> Dict[str, str]:
        """收集生成的文件"""
        code_files = {}
        
        # 忽略的目录和文件
        ignore_dirs = {"autogen_workspace", "__pycache__", ".git", "venv"}
        ignore_files = {".DS_Store", ".gitignore"}
        
        for file_path in output_dir.rglob("*"):
            if file_path.is_file():
                # 检查是否应该忽略
                relative_path = file_path.relative_to(output_dir)
                path_parts = set(relative_path.parts)
                
                if not (path_parts & ignore_dirs) and file_path.name not in ignore_files:
                    if file_path.suffix in ['.py', '.txt', '.md', '.yml', '.yaml', '.json']:
                        try:
                            code_files[str(relative_path)] = file_path.read_text(encoding='utf-8')
                        except:
                            pass
        
        return code_files
    
    def _format_chat_history(self, chat_result: Any) -> str:
        """格式化聊天历史为日志"""
        logs = []
        messages = getattr(chat_result, 'chat_history', []) if hasattr(chat_result, 'chat_history') else []
        for message in messages:
            role = message.get("role", "unknown")
            content = message.get("content", "")
            logs.append(f"[{role}]: {content[:200]}...")
        return "\n".join(logs)
    
    def _get_framework_for_platform(self, platform: str) -> str:
        """获取平台对应的框架"""
        frameworks = {
            "fastapi": "FastAPI",
            "flask": "Flask",
            "django": "Django",
            "springboot": "Spring Boot",
            "express": "Express.js",
            "gin": "Gin"
        }
        return frameworks.get(platform, "FastAPI")
    
    def _get_orm_for_platform(self, platform: str) -> str:
        """获取平台对应的 ORM"""
        orms = {
            "fastapi": "SQLAlchemy",
            "flask": "SQLAlchemy",
            "django": "Django ORM",
            "springboot": "JPA/Hibernate",
            "express": "Sequelize",
            "gin": "GORM"
        }
        return orms.get(platform, "SQLAlchemy")
    
    def _get_validation_lib_for_platform(self, platform: str) -> str:
        """获取平台对应的验证库"""
        validators = {
            "fastapi": "Pydantic",
            "flask": "Marshmallow",
            "django": "Django Forms/Serializers",
            "springboot": "Bean Validation",
            "express": "Joi",
            "gin": "go-playground/validator"
        }
        return validators.get(platform, "Pydantic")