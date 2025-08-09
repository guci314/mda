#!/usr/bin/env python3
"""MDA双Agent架构演示 - 使用Agent as Tool模式"""

import os
import sys
from pathlib import Path
import time
import json
import shutil
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

# 禁用缓存以提高性能
os.environ['DISABLE_LANGCHAIN_CACHE'] = 'true'

from core.react_agent import GenericReactAgent, ReactAgentConfig, MemoryLevel
from core.langchain_agent_tool import AgentToolWrapper, create_langchain_tool
from langchain_core.tools import tool

# 如果使用 Gemini 需要导入 httpx
try:
    import httpx
    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False


def compress_debug_notes(notes_path: str, max_keep_errors: int = 10, max_keep_strategies: int = 20):
    """压缩调试笔记，防止文件过大
    
    Args:
        notes_path: 调试笔记文件路径
        max_keep_errors: 保留的最大错误数
        max_keep_strategies: 保留的最大策略数
    """
    try:
        with open(notes_path, 'r', encoding='utf-8') as f:
            notes = json.load(f)
        
        # 归档原文件
        archive_dir = Path(notes_path).parent / "debug_archive"
        archive_dir.mkdir(exist_ok=True)
        archive_name = f"debug_notes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        shutil.copy(notes_path, archive_dir / archive_name)
        print(f"   已归档到: {archive_dir / archive_name}")
        
        # 压缩错误历史 - 只保留最近的N个
        if 'error_history' in notes and len(notes['error_history']) > max_keep_errors:
            error_items = list(notes['error_history'].items())
            notes['error_history'] = dict(error_items[-max_keep_errors:])
        
        # 压缩修复尝试 - 只保留最近的
        if 'fix_attempts' in notes and len(notes['fix_attempts']) > max_keep_strategies:
            notes['fix_attempts'] = notes['fix_attempts'][-max_keep_strategies:]
        
        # 压缩测试结果历史
        if 'test_results_history' in notes and len(notes['test_results_history']) > 10:
            notes['test_results_history'] = notes['test_results_history'][-10:]
        
        # 保留成功策略但限制数量
        if 'successful_strategies' in notes and len(notes['successful_strategies']) > max_keep_strategies:
            # 按成功率和置信度排序，保留最好的
            sorted_strategies = sorted(
                notes['successful_strategies'],
                key=lambda x: (x.get('confidence', 0), x.get('success_count', 0)),
                reverse=True
            )
            notes['successful_strategies'] = sorted_strategies[:max_keep_strategies]
        
        # 重置迭代计数
        notes['current_iteration'] = 0
        notes['created_at'] = datetime.now().isoformat()
        
        # 保存压缩后的版本
        with open(notes_path, 'w', encoding='utf-8') as f:
            json.dump(notes, f, indent=2)
        
        original_size = os.path.getsize(archive_dir / archive_name)
        new_size = os.path.getsize(notes_path)
        print(f"   压缩完成: {original_size//1024}KB -> {new_size//1024}KB")
        
        # 清理超过7天的归档
        cutoff = datetime.now().timestamp() - (7 * 24 * 3600)
        for old_file in archive_dir.glob("debug_notes_*.json"):
            if old_file.stat().st_mtime < cutoff:
                old_file.unlink()
                print(f"   已删除旧归档: {old_file.name}")
                
    except Exception as e:
        print(f"⚠️ 压缩调试笔记失败: {e}")


def create_generation_agent(work_dir: str, llm_config: dict) -> GenericReactAgent:
    """创建专注于代码生成的Agent"""
    config = ReactAgentConfig(
        work_dir=work_dir,
        memory_level=MemoryLevel.SMART,
        knowledge_files=["knowledge/mda/generation_knowledge.md"],  # 使用生成专用知识
        enable_project_exploration=False,
        **llm_config
    )
    
    agent = GenericReactAgent(config, name="generation_agent")
    agent.interface = """代码生成专家 - 专注于快速生成高质量代码
    
能力：
- PIM到PSM转换
- FastAPI应用生成
- 快速交付，不做调试

原则：
- 生成即返回，不运行测试
- 遇到问题记录但不修复
- 让调试Agent处理所有错误
"""
    return agent


def create_debug_agent(work_dir: str, llm_config: dict) -> GenericReactAgent:
    """创建专门的调试Agent"""
    from langchain_core.tools import tool
    import json
    from datetime import datetime
    import os
    
    # 检查并压缩调试笔记
    notes_path = os.path.join(work_dir, 'debug_notes.json')
    if os.path.exists(notes_path):
        size = os.path.getsize(notes_path)
        if size > 50 * 1024:  # 超过50KB
            print(f"📦 调试笔记大小 {size//1024}KB，正在压缩...")
            compress_debug_notes(notes_path)
    
    @tool
    def init_debug_notes() -> str:
        """初始化或读取调试笔记"""
        import os
        notes_path = os.path.join(work_dir, 'debug_notes.json')
        
        if os.path.exists(notes_path):
            with open(notes_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # 限制返回内容大小，只返回摘要
                notes = json.loads(content)
                summary = {
                    "session_id": notes.get("session_id"),
                    "current_iteration": notes.get("current_iteration", 0),
                    "error_count": len(notes.get("error_history", {})),
                    "successful_strategies_count": len(notes.get("successful_strategies", [])),
                    "failed_strategies_count": len(notes.get("failed_strategies", []))
                }
                return f"Debug notes exists with {summary['error_count']} errors tracked, {summary['successful_strategies_count']} successful strategies"
        else:
            initial_notes = {
                "session_id": f"debug_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "created_at": datetime.now().isoformat(),
                "current_iteration": 0,
                "error_history": {},
                "fix_attempts": [],
                "successful_strategies": [],
                "failed_strategies": [],
                "test_results_history": []
            }
            with open(notes_path, 'w', encoding='utf-8') as f:
                json.dump(initial_notes, f, indent=2)
            return f"Created new debug notes: {notes_path}"
    
    @tool
    def fix_python_syntax_errors(file_path: str) -> str:
        """【推荐】修复Python文件的语法错误 - 重写整个文件而不是逐行修复
        
        这个工具专门用于修复Python语法错误（缩进、括号不匹配等）。
        它会读取整个文件，修复所有语法问题，然后重写整个文件。
        
        Args:
            file_path: 要修复的Python文件路径
            
        Returns:
            修复结果信息
        """
        import os
        import ast
        import re
        import json
        
        full_path = os.path.join(work_dir, file_path)
        
        if not os.path.exists(full_path):
            return f"文件不存在: {file_path}"
        
        # 读取文件内容
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 尝试解析以检测语法错误
        original_error = None
        try:
            ast.parse(content)
            return f"文件 {file_path} 没有语法错误"
        except (SyntaxError, IndentationError) as e:
            original_error = f"{e.__class__.__name__}: {e.msg} at line {e.lineno}"
        
        # 修复策略1：智能括号匹配
        def fix_brackets(text):
            """修复括号不匹配问题"""
            lines = text.split('\n')
            fixed_lines = []
            bracket_stack = []
            
            for line_num, line in enumerate(lines):
                # 统计各种括号
                for char in line:
                    if char in '({[':
                        bracket_stack.append(char)
                    elif char in ')}]':
                        expected = {'(': ')', '{': '}', '[': ']'}
                        if bracket_stack and expected.get(bracket_stack[-1]) == char:
                            bracket_stack.pop()
                        else:
                            # 发现不匹配的括号，尝试修复
                            if char == '}' and not bracket_stack:
                                # 多余的闭合括号，可能需要删除
                                line = line.replace(char, '', 1)
                
                fixed_lines.append(line)
            
            # 如果还有未闭合的括号，在文件末尾添加
            if bracket_stack:
                closing = ''
                for bracket in reversed(bracket_stack):
                    if bracket == '(':
                        closing += ')'
                    elif bracket == '{':
                        closing += '}'
                    elif bracket == '[':
                        closing += ']'
                if closing:
                    fixed_lines.append(closing)
            
            return '\n'.join(fixed_lines)
        
        # 修复策略2：修复JSON格式问题
        def fix_json_syntax(text):
            """修复JSON格式的语法问题"""
            # 修复缺少逗号的情况
            text = re.sub(r'"\s*\n\s*"', '",\n"', text)
            text = re.sub(r'(\d)\s*\n\s*"', r'\1,\n"', text)
            text = re.sub(r'}\s*\n\s*"', r'},\n"', text)
            text = re.sub(r']\s*\n\s*"', r'],\n"', text)
            return text
        
        # 修复策略3：智能缩进修复
        def fix_indentation(text):
            """修复缩进问题"""
            lines = text.split('\n')
            fixed_lines = []
            indent_level = 0
            
            for line in lines:
                stripped = line.strip()
                if not stripped:
                    fixed_lines.append('')
                    continue
                
                # 减少缩进的情况
                if stripped.startswith(('else:', 'elif ', 'except:', 'finally:', 'except ', 'elif:')):
                    indent_level = max(0, indent_level - 1)
                    fixed_lines.append('    ' * indent_level + stripped)
                    indent_level += 1
                elif stripped.startswith(('return', 'break', 'continue', 'pass', 'raise')):
                    fixed_lines.append('    ' * indent_level + stripped)
                    if indent_level > 0 and not line.endswith(':'):
                        indent_level = max(0, indent_level - 1)
                elif stripped.startswith(('def ', 'class ', 'if ', 'for ', 'while ', 'with ', 'try:')):
                    fixed_lines.append('    ' * indent_level + stripped)
                    if stripped.endswith(':'):
                        indent_level += 1
                elif stripped == '}' or stripped == ']' or stripped == ')':
                    indent_level = max(0, indent_level - 1)
                    fixed_lines.append('    ' * indent_level + stripped)
                else:
                    # 普通行
                    fixed_lines.append('    ' * indent_level + stripped)
                    if stripped.endswith(':'):
                        indent_level += 1
                    elif stripped in ('}', ']', ')'):
                        indent_level = max(0, indent_level - 1)
            
            return '\n'.join(fixed_lines)
        
        # 依次应用修复策略
        fixed_content = content
        fixed_content = fix_brackets(fixed_content)
        fixed_content = fix_json_syntax(fixed_content)
        fixed_content = fix_indentation(fixed_content)
        
        # 写回文件
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        
        # 再次检查是否修复成功
        try:
            ast.parse(fixed_content)
            return f"成功修复 {file_path} 的语法错误:\n原始错误: {original_error}\n\n文件已完全重写。"
        except (SyntaxError, IndentationError) as e:
            new_error = f"{e.__class__.__name__}: {e.msg} at line {e.lineno}"
            return f"尝试修复 {file_path}:\n原始错误: {original_error}\n当前错误: {new_error}\n\n部分修复成功，建议使用 write_file 工具手动重写。"
    
    config = ReactAgentConfig(
        work_dir=work_dir,
        memory_level=MemoryLevel.SMART,
        knowledge_files=[
            "knowledge/mda/debugging_knowledge.md",      # 调试专用知识
            "knowledge/mda/syntax_fix_strategies.md"     # 语法修复策略
        ],
        enable_project_exploration=False,
        **llm_config
    )
    
    agent = GenericReactAgent(config, name="debug_agent", custom_tools=[init_debug_notes, fix_python_syntax_errors])
    agent.interface = """调试专家 - 系统性修复代码错误
    
能力：
- 维护调试笔记避免重复修复
- 智能语法错误修复（整文件重写）
- 系统性错误诊断和修复
- 确保100%测试通过
"""
    
    # 为调试Agent添加额外的系统提示，指导其使用正确的工具
    agent._system_prompt = (agent._system_prompt or "") + """

## 调试流程指导

你必须完成完整的调试流程，不要只初始化就返回！

### Python语法错误修复策略（重要）
**优先使用 fix_python_syntax_errors 工具！**
- 遇到缩进错误（IndentationError）：立即使用 fix_python_syntax_errors 工具
- 遇到括号不匹配（SyntaxError: unmatched）：立即使用 fix_python_syntax_errors 工具  
- 遇到多个语法错误：使用 fix_python_syntax_errors 一次性修复整个文件
- 避免使用 edit_lines 逐行修复语法错误！这会导致反复修复同样的问题。

### 执行流程（必须全部完成）
1. 调用 init_debug_notes 工具初始化调试笔记
2. 使用 execute_command 运行 pytest -xvs 获取测试结果
3. 如果有失败：
   - 对于语法错误：立即使用 fix_python_syntax_errors 工具
   - 对于其他错误：使用 read_file、search_replace 或 write_file 修复
   - 更新 debug_notes.json 记录修复尝试
4. 再次运行 pytest 验证修复
5. 重复步骤3-4直到所有测试通过
6. 更新最终的 debug_notes.json

### 返回条件
- 成功：所有测试通过（0 failed），返回"调试完成，所有测试通过"
- 失败：达到最大尝试次数（10次），返回"需要人工介入"
- 继续：如果需要更多步骤，返回"需要继续调试，请再次调用"
"""
    return agent


def create_coordinator_agent(work_dir: str, llm_config: dict, 
                           generation_tool, debug_tool) -> GenericReactAgent:
    """创建协调两个子Agent的主Agent"""
    
    # 导入write_file工具用于TODO管理
    from langchain_core.tools import tool
    import subprocess
    
    @tool
    def write_todo_file(file_path: str, content: str) -> str:
        """写入或更新TODO文件"""
        import os
        full_path = os.path.join(work_dir, file_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully wrote TODO file: {file_path}"
    
    @tool
    def execute_command(command: str) -> str:
        """执行shell命令并返回结果"""
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=60
            )
            output = f"Command: {command}\n"
            output += f"Return code: {result.returncode}\n"
            if result.stdout:
                output += f"Output:\n{result.stdout}\n"
            if result.stderr:
                output += f"Error:\n{result.stderr}\n"
            return output
        except subprocess.TimeoutExpired:
            return f"Command timed out after 60 seconds: {command}"
        except Exception as e:
            return f"Error executing command: {str(e)}"
    
    # 主Agent配置 - 只负责协调
    config = ReactAgentConfig(
        work_dir=work_dir,
        memory_level=MemoryLevel.SMART,
        knowledge_files=[],  # 主Agent不需要领域知识
        enable_project_exploration=False,
        **llm_config
    )
    
    # 创建主Agent，通过构造函数传入自定义工具
    agent = GenericReactAgent(
        config, 
        name="coordinator_agent",
        custom_tools=[write_todo_file, execute_command, generation_tool, debug_tool]  # 添加write_todo_file和execute_command工具
    )
    
    agent.interface = """MDA Pipeline协调者
    
我协调两个专门的Agent：
1. 生成Agent - 负责代码生成
2. 调试Agent - 负责错误修复

工作流程：
1. 调用生成Agent创建代码
2. 运行测试验证
3. 如有失败，调用调试Agent修复
4. 循环直到100%通过
"""
    
    return agent


def main():
    """运行双Agent架构的MDA Pipeline"""
    
    print("=" * 80)
    print("MDA双Agent架构演示")
    print("=" * 80)
    
    # 设置工作目录
    work_dir = Path("output/mda_dual_agent_demo")
    work_dir.mkdir(parents=True, exist_ok=True)
    
    # PSM文件路径 (使用已有的PSM)
    psm_file = Path(__file__).parent / "output/mda_demo/library_borrowing_system_psm.md"
    
    # 选择LLM配置
    print("\n选择LLM配置：")
    print("1. DeepSeek (默认)")
    print("2. Kimi k2-turbo (128K上下文)")
    print("3. Gemini 2.5 Pro (via OpenRouter)")
    print("4. Claude Sonnet 4 (via OpenRouter)")
    
    choice = input("请选择 (1-4，默认1): ").strip() or "1"
    
    if choice == "2":
        # Kimi配置
        llm_config = {
            "llm_model": "kimi-k2-turbo-preview",
            "llm_base_url": "https://api.moonshot.cn/v1",
            "llm_api_key_env": "MOONSHOT_API_KEY",
            "llm_temperature": 0
        }
        llm_name = "Kimi k2-turbo (128K上下文)"
    elif choice == "3":
        # Gemini配置 (通过OpenRouter)
        llm_config = {
            "llm_model": "google/gemini-2.5-pro",
            "llm_base_url": "https://openrouter.ai/api/v1",
            "llm_api_key_env": "OPENROUTER_API_KEY",
            "llm_temperature": 0
        }
        llm_name = "Gemini 2.5 Pro (via OpenRouter)"
    elif choice == "4":
        # Claude配置
        llm_config = {
            "llm_model": "anthropic/claude-sonnet-4",
            "llm_base_url": "https://openrouter.ai/api/v1",
            "llm_api_key_env": "OPENROUTER_API_KEY",
            "llm_temperature": 0
        }
        llm_name = "Claude Sonnet 4"
    else:
        # DeepSeek配置（默认）
        llm_config = {
            "llm_model": "deepseek-chat",
            "llm_base_url": "https://api.deepseek.com/v1",
            "llm_api_key_env": "DEEPSEEK_API_KEY",
            "llm_temperature": 0
        }
        llm_name = "DeepSeek"
    
    print(f"\n使用 {llm_name} 作为LLM后端")
    
    # 创建子Agent
    print("\n创建专门的子Agent...")
    generation_agent = create_generation_agent(str(work_dir), llm_config)
    debug_agent = create_debug_agent(str(work_dir), llm_config)
    
    # 将子Agent包装为工具
    print("将子Agent包装为LangChain工具...")
    
    # 设置Agent的名称，这将被create_langchain_tool使用
    generation_agent.name = "code_generator"
    generation_agent.interface = """生成代码的专门Agent，用于PSM生成和FastAPI代码生成
    
输入：生成任务描述
输出：生成的代码文件"""
    
    debug_agent.name = "code_debugger" 
    debug_agent.interface = """调试代码的专门Agent，用于修复测试失败和错误
    
输入：调试任务描述
输出：修复后的代码和调试报告"""
    
    generation_tool = create_langchain_tool(generation_agent)
    debug_tool = create_langchain_tool(debug_agent)
    
    # 创建协调Agent
    print("创建协调Agent...")
    coordinator = create_coordinator_agent(
        str(work_dir), 
        llm_config,
        generation_tool,
        debug_tool
    )
    
    # 执行任务 - 使用意图声明风格
    print("\n" + "=" * 60)
    print("开始执行MDA Pipeline...")
    print("=" * 60)
    
    start_time = time.time()
    
    # 意图声明风格的任务描述
    task = f"""
## 目标
从PSM文件生成一个完全可工作的FastAPI应用，确保所有测试100%通过。

## 输入
- PSM文件：{psm_file}
- 输出目录：{work_dir}


## TODO管理要求
你必须在 {work_dir}/coordinator_todo.json 文件中维护任务清单。

初始TODO结构：
```json
{{
  "tasks": [
    {{"id": 1, "task": "生成FastAPI应用代码", "status": "pending"}},
    {{"id": 2, "task": "运行pytest测试验证", "status": "pending"}},
    {{"id": 3, "task": "如果测试失败，调用调试Agent修复", "status": "pending"}},
    {{"id": 4, "task": "确认所有测试100%通过", "status": "pending"}}
  ],
  "current_task": null,
  "completed_count": 0,
  "total_count": 4
}}
```

每次开始和完成任务时，使用 write_todo_file 工具更新TODO文件：
- 开始任务时：设置 status = "in_progress"，更新 current_task
- 完成任务时：设置 status = "completed"，更新 completed_count
- 跳过任务时：设置 status = "skipped"

## 执行策略
你有四个工具可以使用：
1. **write_todo_file** - 用于创建和更新TODO笔记
2. **code_generator** - 用于生成代码
3. **execute_command** - 用于运行命令（如pytest）  
4. **code_debugger** - 用于修复测试失败

请按照以下流程执行：
1. 首先，创建TODO笔记文件
2. 使用 code_generator 生成FastAPI应用（更新TODO：任务1完成）
3. 使用 execute_command 运行 `cd {work_dir} && python -m pytest tests/ -xvs` 验证代码（更新TODO：任务2完成）
4. 如果测试有失败：
   - 使用 code_debugger 修复所有错误，传递明确的任务：
     "修复测试错误直到全部通过。你必须完成整个调试流程，不要只初始化就返回。
      
      【重要】你有一个专门的工具 fix_python_syntax_errors 用于修复Python语法错误：
      - 遇到任何缩进错误（IndentationError）：使用 fix_python_syntax_errors 工具
      - 遇到括号不匹配（SyntaxError）：使用 fix_python_syntax_errors 工具
      - 这个工具会自动重写整个文件，避免逐行修复的问题
      
      使用你的所有工具，特别是 fix_python_syntax_errors 处理语法错误。
      持续修复直到所有测试通过或达到最大尝试次数。"
   - 如果 code_debugger 返回"需要继续调试"，立即再次调用它
   - 循环调用 code_debugger 直到返回"调试完成"或"需要人工介入"
   - 再次使用 execute_command 运行测试确认修复成功
   - 检查 debug_notes.json 确认调试Agent记录了所有活动
5. 确认所有测试通过（更新TODO：任务4完成）

## 重要提示
- 每个任务开始和结束都要更新TODO笔记
- 必须完成整个流程，不要在生成代码后就停止
- 必须实际运行测试并查看结果
- 如果测试失败，必须调用调试Agent修复
- **绝对不要自己使用sed或其他命令修改代码，只能通过code_debugger修复**
- **如果code_debugger需要更多步骤，必须继续调用它，不要放弃**
- 只有当看到所有测试通过才能结束任务

现在开始执行，记得维护TODO笔记，确保达到100%测试通过的目标。

## 成功标准
- TODO列表中的每一项任务都必须完成（status为"completed"或"skipped"）
- FastAPI应用成功生成在指定目录
- 运行 `pytest tests/ -xvs` 所有测试必须通过（0个失败）
- 如果有测试失败，必须修复直到100%通过
- coordinator_todo.json 的 completed_count 必须等于 total_count

"""
    
    try:
        # 执行完整任务
        result = coordinator.execute_task(task)
        
        elapsed_time = time.time() - start_time
        
        print("\n" + "=" * 60)
        print("执行完成！")
        print("=" * 60)
        print(f"总耗时：{elapsed_time:.1f} 秒")
        
        # 检查协调Agent的TODO笔记
        todo_file = work_dir / "coordinator_todo.json"
        if todo_file.exists():
            with open(todo_file, 'r') as f:
                todo_data = json.load(f)
            
            print("\n📋 任务完成情况（coordinator_todo.json）：")
            for task in todo_data.get('tasks', []):
                status_emoji = {
                    'completed': '✅',
                    'in_progress': '🔄',
                    'pending': '⏳',
                    'skipped': '⏭️'
                }.get(task['status'], '❓')
                print(f"  {status_emoji} {task['task']} [{task['status']}]")
            
            print(f"\n完成进度：{todo_data.get('completed_count', 0)}/{todo_data.get('total_count', 0)}")
        
        # 检查是否有调试笔记（调试Agent必须创建的）
        debug_notes_file = work_dir / "debug_notes.json"
        if debug_notes_file.exists():
            with open(debug_notes_file, 'r') as f:
                notes = json.load(f)
            
            print("\n🔧 调试统计（debug_notes.json）：")
            print(f"- 迭代次数：{notes.get('current_iteration', 0)}")
            print(f"- 修复尝试：{len(notes.get('fix_attempts', []))}")
            print(f"- 错误类型：{len(notes.get('error_history', {}))}")
            
            # 显示成功策略
            successful = [a for a in notes.get('fix_attempts', []) 
                         if a.get('result') == 'success']
            if successful:
                print(f"\n成功的修复策略：")
                for s in successful[:3]:
                    print(f"  - {s.get('strategy', 'unknown')}")
        
        print("\n结果摘要：")
        print(result[:500] if len(result) > 500 else result)
        
    except Exception as e:
        print(f"\n执行失败：{e}")
        import traceback
        traceback.print_exc()
        
    print("finished")


if __name__ == "__main__":
    main()