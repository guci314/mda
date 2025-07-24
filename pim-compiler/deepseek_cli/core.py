#!/usr/bin/env python3
"""
基于 DeepSeek 的 Gemini CLI 风格实现
使用 DeepSeek API 替代 Gemini，解决网络访问问题
"""
import os
import json
import time
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from abc import ABC, abstractmethod
import requests

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ActionType(Enum):
    """动作类型"""
    THINK = "think"
    PLAN = "plan"
    READ_FILE = "read_file"
    WRITE_FILE = "write_file"
    LIST_FILES = "list_files"
    ANALYZE = "analyze"
    GENERATE = "generate"
    VALIDATE = "validate"
    COMPLETE = "complete"


@dataclass
class Action:
    """动作定义"""
    type: ActionType
    description: str
    params: Optional[Dict[str, Any]] = None
    result: Any = None
    error: Optional[str] = None


@dataclass
class ExecutionPlan:
    """执行计划"""
    goal: str
    steps: List[str]
    current_step: int = 0
    
    def get_current_step(self) -> Optional[str]:
        if self.current_step < len(self.steps):
            return self.steps[self.current_step]
        return None
    
    def advance(self):
        self.current_step += 1
    
    def is_complete(self) -> bool:
        return self.current_step >= len(self.steps)


class Tool(ABC):
    """工具基类"""
    @abstractmethod
    def execute(self, params: Dict[str, Any]) -> Any:
        pass


class FileReader(Tool):
    """文件读取工具"""
    def execute(self, params: Dict[str, Any]) -> str:
        file_path = params.get("file_path")
        if not file_path:
            raise ValueError("file_path is required")
        logger.info(f"Reading file: {file_path}")
        
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        logger.info(f"Read {len(content)} characters from {file_path}")
        return content


class FileWriter(Tool):
    """文件写入工具"""
    def execute(self, params: Dict[str, Any]) -> str:
        file_path = params.get("file_path")
        content = params.get("content")
        
        if not file_path:
            raise ValueError("file_path is required")
        if content is None:
            raise ValueError("content is required")
        
        logger.info(f"Writing file: {file_path}")
        
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Wrote {len(content)} characters to {file_path}")
        return f"File written: {file_path}"


class FileLister(Tool):
    """文件列表工具"""
    def execute(self, params: Dict[str, Any]) -> List[str]:
        directory = params.get("directory", ".")
        pattern = params.get("pattern", "*")
        
        logger.info(f"Listing files in {directory} with pattern {pattern}")
        
        path = Path(directory)
        if not path.exists():
            return []
        
        files = list(path.glob(pattern))
        file_list = [str(f) for f in files]
        
        logger.info(f"Found {len(file_list)} files")
        return file_list


class DeepSeekLLM:
    """DeepSeek API 集成"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.deepseek.com"):
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        self.base_url = base_url
        self.model = "deepseek-chat"
        
        if not self.api_key:
            raise ValueError("DeepSeek API key not provided. Set DEEPSEEK_API_KEY environment variable.")
    
    def _call_api(self, messages: List[Dict[str, str]], temperature: float = 0.3) -> str:
        """调用 DeepSeek API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "stream": False
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
            
        except requests.exceptions.RequestException as e:
            logger.error(f"DeepSeek API error: {e}")
            raise
    
    def think(self, context: str, task: str) -> str:
        """思考当前任务"""
        messages = [
            {
                "role": "system",
                "content": "你是一个任务执行助手，需要分析当前状态并决定下一步行动。"
            },
            {
                "role": "user",
                "content": f"""当前上下文：
{context}

当前任务：{task}

请分析当前状态，并说明下一步应该做什么。"""
            }
        ]
        
        return self._call_api(messages)
    
    def plan(self, task: str) -> ExecutionPlan:
        """制定任务执行计划"""
        messages = [
            {
                "role": "system",
                "content": """你是一个任务规划专家。请将复杂任务分解为具体的执行步骤。
每个步骤应该是一个明确的、可执行的动作。
返回 JSON 格式的步骤列表。"""
            },
            {
                "role": "user",
                "content": f"""请为以下任务制定执行计划：
{task}

返回格式：
{{
    "steps": ["步骤1", "步骤2", "步骤3", ...]
}}"""
            }
        ]
        
        response = self._call_api(messages, temperature=0.1)
        
        try:
            # 尝试解析 JSON
            plan_data = json.loads(response)
            steps = plan_data.get("steps", [])
        except json.JSONDecodeError:
            # 如果不是 JSON，尝试从文本中提取步骤
            logger.warning("Failed to parse JSON, extracting steps from text")
            steps = []
            for line in response.split('\n'):
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('-')):
                    # 移除数字和符号前缀
                    step = line.lstrip('0123456789.- \t')
                    if step:
                        steps.append(step)
        
        if not steps:
            # 如果还是没有步骤，使用默认步骤
            if "PSM" in task and "PIM" in task:
                steps = [
                    "读取 PIM 文件内容",
                    "分析 PIM 中的实体和属性",
                    "生成 SQLAlchemy 数据模型",
                    "生成 Pydantic Schema 定义",
                    "生成 CRUD 操作接口",
                    "生成 REST API 端点",
                    "组合所有代码为 PSM 文档",
                    "写入 PSM 文件"
                ]
            else:
                steps = ["执行任务"]
        
        return ExecutionPlan(goal=task, steps=steps)
    
    def analyze_content(self, content: str, instruction: str) -> Dict[str, Any]:
        """分析内容"""
        messages = [
            {
                "role": "system",
                "content": "你是一个代码分析专家，擅长分析和理解各种格式的技术文档。"
            },
            {
                "role": "user",
                "content": f"""{instruction}

内容：
{content}

请以 JSON 格式返回分析结果。"""
            }
        ]
        
        response = self._call_api(messages, temperature=0.1)
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"raw_response": response}
    
    def generate_code(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """生成代码"""
        system_prompt = """你是一个专业的代码生成专家，擅长生成高质量的 Python 代码。
生成的代码应该：
1. 遵循 PEP 8 规范
2. 包含适当的类型注解
3. 有清晰的注释
4. 处理错误情况
5. 使用现代 Python 特性（3.8+）"""
        
        user_prompt = prompt
        if context:
            user_prompt = f"""基于以下上下文生成代码：
{json.dumps(context, indent=2, ensure_ascii=False)}

任务：{prompt}"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        return self._call_api(messages, temperature=0.3)


class DeepSeekCLI:
    """基于 DeepSeek 的 CLI 实现"""
    
    def __init__(self, working_dir: str = ".", api_key: Optional[str] = None):
        self.working_dir = Path(working_dir)
        self.llm = DeepSeekLLM(api_key)
        self.tools = {
            "read_file": FileReader(),
            "write_file": FileWriter(),
            "list_files": FileLister()
        }
        self.context: Dict[str, Any] = {}
        self.action_history: List[Action] = []
        self.max_iterations = 50
    
    def execute_task(self, task: str) -> Tuple[bool, str]:
        """执行任务的主入口"""
        logger.info(f"Starting task: {task}")
        
        # 1. 制定执行计划
        logger.info("Creating execution plan...")
        plan = self.llm.plan(task)
        logger.info(f"Execution plan created with {len(plan.steps)} steps:")
        for i, step in enumerate(plan.steps):
            logger.info(f"  Step {i+1}: {step}")
        
        # 2. 执行计划
        iteration = 0
        while not plan.is_complete() and iteration < self.max_iterations:
            iteration += 1
            current_step = plan.get_current_step()
            if not current_step:
                break
                
            logger.info(f"\n{'='*60}")
            logger.info(f"Iteration {iteration}: {current_step}")
            logger.info(f"{'='*60}")
            
            try:
                # 思考当前步骤
                thought = self._think(current_step)
                
                # 决定动作
                action = self._decide_action(thought, current_step)
                
                # 执行动作
                result = self._execute_action(action)
                action.result = result
                
                # 更新上下文
                self._update_context(action)
                
                # 记录动作
                self.action_history.append(action)
                
                # 判断是否可以进入下一步
                if self._should_advance(action, current_step):
                    plan.advance()
                    logger.info(f"✓ Step completed: {current_step}")
                    
            except Exception as e:
                logger.error(f"Action failed: {e}")
                action.error = str(e)
                self.action_history.append(action)
                
                # 尝试恢复或跳过
                if self._can_recover(e):
                    logger.info("Attempting to recover...")
                    continue
                else:
                    return False, f"Task failed: {str(e)}"
        
        # 3. 检查是否完成
        if plan.is_complete():
            logger.info("\n✅ Task completed successfully!")
            return True, "Task completed"
        else:
            logger.warning("\n⚠️ Task did not complete within iteration limit")
            return False, "Max iterations reached"
    
    def _think(self, step: str) -> str:
        """思考当前步骤"""
        context_str = json.dumps(self.context, indent=2, ensure_ascii=False)
        thought = self.llm.think(context_str, step)
        logger.info(f"Thought: {thought[:200]}...")
        return thought
    
    def _decide_action(self, thought: str, step: str) -> Action:
        """基于思考决定动作"""
        # 根据步骤内容决定动作类型
        step_lower = step.lower()
        
        if "读取" in step and ("文件" in step or "pim" in step):
            # 从思考中提取文件路径
            file_path = self._extract_file_path(thought, step)
            return Action(
                type=ActionType.READ_FILE,
                description=f"读取文件: {file_path}",
                params={"file_path": file_path}
            )
        
        elif "分析" in step or "解析" in step:
            return Action(
                type=ActionType.ANALYZE,
                description="分析内容结构",
                params={
                    "content": self.context.get("file_content", ""),
                    "instruction": f"请分析以下内容并提取实体、属性和关系。{step}"
                }
            )
        
        elif "生成" in step:
            # 根据步骤内容决定生成什么
            if "sqlalchemy" in step_lower or "数据模型" in step:
                prompt = "基于分析结果生成 SQLAlchemy 数据模型"
            elif "pydantic" in step_lower or "schema" in step_lower:
                prompt = "基于分析结果生成 Pydantic Schema 定义"
            elif "crud" in step_lower:
                prompt = "基于数据模型生成 CRUD 操作接口"
            elif "api" in step_lower or "endpoint" in step_lower:
                prompt = "基于 CRUD 接口生成 FastAPI REST 端点"
            elif "组合" in step or "psm" in step_lower:
                prompt = "将所有生成的代码组合成完整的 PSM 文档"
            else:
                prompt = step
            
            return Action(
                type=ActionType.GENERATE,
                description=f"生成: {step}",
                params={
                    "prompt": prompt,
                    "context": self.context.get("analysis", {})
                }
            )
        
        elif "写入" in step or "保存" in step:
            file_path = self._extract_output_path(step)
            return Action(
                type=ActionType.WRITE_FILE,
                description=f"写入文件: {file_path}",
                params={
                    "file_path": file_path,
                    "content": self.context.get("generated_content", "")
                }
            )
        
        else:
            # 默认为思考动作
            return Action(
                type=ActionType.THINK,
                description="继续分析和思考",
                params={}
            )
    
    def _execute_action(self, action: Action) -> Any:
        """执行动作"""
        logger.info(f"Executing: {action.type.value} - {action.description}")
        
        if action.type == ActionType.READ_FILE:
            tool = self.tools["read_file"]
            return tool.execute(action.params or {})
        
        elif action.type == ActionType.WRITE_FILE:
            tool = self.tools["write_file"]
            return tool.execute(action.params or {})
        
        elif action.type == ActionType.LIST_FILES:
            tool = self.tools["list_files"]
            return tool.execute(action.params or {})
        
        elif action.type == ActionType.ANALYZE:
            params = action.params or {}
            content = params.get("content", "")
            instruction = params.get("instruction", "")
            return self.llm.analyze_content(content, instruction)
        
        elif action.type == ActionType.GENERATE:
            params = action.params or {}
            prompt = params.get("prompt", "")
            context = params.get("context", {})
            return self.llm.generate_code(prompt, context)
        
        elif action.type == ActionType.THINK:
            return "Continuing analysis..."
        
        else:
            return None
    
    def _update_context(self, action: Action):
        """更新执行上下文"""
        if action.type == ActionType.READ_FILE and action.result:
            self.context["file_content"] = action.result
            if action.params:
                self.context["input_file"] = action.params.get("file_path")
        
        elif action.type == ActionType.ANALYZE and action.result:
            self.context["analysis"] = action.result
        
        elif action.type == ActionType.GENERATE and action.result:
            # 累积生成的内容
            if "generated_content" not in self.context:
                self.context["generated_content"] = ""
            
            # 添加适当的分隔
            if self.context["generated_content"]:
                self.context["generated_content"] += "\n\n"
            
            self.context["generated_content"] += action.result
            
            # 保存特定类型的生成内容
            if "sqlalchemy" in action.description.lower():
                self.context["sqlalchemy_models"] = action.result
            elif "pydantic" in action.description.lower():
                self.context["pydantic_schemas"] = action.result
            elif "crud" in action.description.lower():
                self.context["crud_operations"] = action.result
            elif "api" in action.description.lower():
                self.context["api_endpoints"] = action.result
    
    def _should_advance(self, action: Action, current_step: str) -> bool:
        """判断是否应该进入下一步"""
        # 如果动作成功完成且有结果，通常可以进入下一步
        if action.result and not action.error:
            # 特定动作类型的判断
            if action.type in [ActionType.READ_FILE, ActionType.ANALYZE, 
                             ActionType.GENERATE, ActionType.WRITE_FILE]:
                return True
        
        # 思考动作通常不推进步骤
        if action.type == ActionType.THINK:
            return False
        
        return False
    
    def _can_recover(self, error: Exception) -> bool:
        """判断是否可以从错误中恢复"""
        # 文件不存在错误通常可以通过创建文件或使用默认值恢复
        if isinstance(error, FileNotFoundError):
            return True
        
        # 其他错误暂时不尝试恢复
        return False
    
    def _extract_file_path(self, thought: str, step: str) -> str:
        """从思考或步骤中提取文件路径"""
        # 简单实现：查找常见的文件扩展名
        import re
        
        # 尝试从步骤中找到文件名
        patterns = [
            r'([a-zA-Z0-9_\-]+\.(?:md|py|txt|json|yaml|yml))',
            r'"([^"]+)"',
            r"'([^']+)'"
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, step + " " + thought)
            for match in matches:
                if '.' in match:  # 可能是文件名
                    return match
        
        # 默认返回
        return "input.md"
    
    def _extract_output_path(self, step: str) -> str:
        """从步骤中提取输出文件路径"""
        if "psm" in step.lower():
            return "output_psm.md"
        
        return "output.md"
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """获取执行摘要"""
        return {
            "total_actions": len(self.action_history),
            "successful_actions": sum(1 for a in self.action_history if not a.error),
            "failed_actions": sum(1 for a in self.action_history if a.error),
            "action_types": {
                action_type.value: sum(1 for a in self.action_history if a.type == action_type)
                for action_type in ActionType
            },
            "context_keys": list(self.context.keys()),
            "execution_log": [
                {
                    "type": action.type.value,
                    "description": action.description,
                    "success": action.error is None,
                    "error": action.error
                }
                for action in self.action_history
            ]
        }


# 使用示例
if __name__ == "__main__":
    # 创建测试 PIM 文件
    test_pim = """# 智慧医院系统 PIM

## 实体模型

### 患者 (Patient)
- 患者ID (patientId): 字符串，唯一标识
- 姓名 (name): 字符串，必填
- 身份证号 (idNumber): 字符串，唯一
- 性别 (gender): 枚举[男, 女]
- 出生日期 (birthDate): 日期
- 电话 (phone): 字符串
- 地址 (address): 字符串

### 医生 (Doctor)
- 医生ID (doctorId): 字符串，唯一标识
- 姓名 (name): 字符串，必填
- 工号 (employeeId): 字符串，唯一
- 科室 (department): 字符串，必填
- 职称 (title): 字符串
- 专长 (specialties): 字符串列表

## 业务规则
1. 患者必须先注册才能挂号
2. 医生必须属于某个科室
3. 挂号时需要选择具体的医生和时间段
"""
    
    # 保存测试文件
    with open("hospital_pim.md", "w", encoding="utf-8") as f:
        f.write(test_pim)
    
    # 创建 CLI 实例
    cli = DeepSeekCLI()
    
    # 执行任务
    print("开始执行任务...")
    success, message = cli.execute_task("将 hospital_pim.md 中的 PIM 转换为 FastAPI 平台的 PSM")
    
    # 打印结果
    print(f"\n{'='*60}")
    print(f"执行结果: {'✅ 成功' if success else '❌ 失败'}")
    print(f"消息: {message}")
    
    # 打印执行摘要
    summary = cli.get_execution_summary()
    print(f"\n执行摘要:")
    print(f"- 总动作数: {summary['total_actions']}")
    print(f"- 成功动作: {summary['successful_actions']}")
    print(f"- 失败动作: {summary['failed_actions']}")
    print(f"- 生成的上下文: {', '.join(summary['context_keys'])}")
    
    # 检查输出文件
    output_file = Path("output_psm.md")
    if output_file.exists():
        print(f"\n✅ PSM 文件已生成: {output_file}")
        print(f"文件大小: {output_file.stat().st_size} 字节")
    else:
        print(f"\n❌ PSM 文件未生成")