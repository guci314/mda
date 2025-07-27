#!/usr/bin/env python3
"""
PIM Compiler Chatbot

使用 LangChain ReAct Agent 实现的智能编译助手
"""

import os
import subprocess
import time
import glob
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

from langchain.agents import Tool, AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.schema import AgentAction, AgentFinish


class PIMCompilerTools:
    """PIM 编译器工具集"""
    
    def __init__(self, pim_compiler_path: str = "."):
        self.pim_compiler_path = Path(pim_compiler_path).resolve()
        self.examples_dir = self.pim_compiler_path / "examples"
        self.compiled_output_dir = self.pim_compiler_path / "compiled_output"
        self.active_processes = {}  # 跟踪活动的编译进程
        
    def search_pim_files(self, query: str) -> str:
        """搜索 PIM 文件
        
        Args:
            query: 搜索关键词，如 "医院系统", "hospital"
            
        Returns:
            找到的 PIM 文件列表
        """
        try:
            # 清理查询参数
            query = query.strip().strip('"\'')
            
            # 处理空查询
            if not query:
                # 列出所有 MD 文件
                all_files = list(self.examples_dir.glob("*.md"))
                if all_files:
                    result = f"所有可用的 PIM 文件 ({len(all_files)} 个):\n"
                    for file in all_files:
                        result += f"- {file.name}\n"
                    return result
                else:
                    return "未找到任何 PIM 文件"
            
            # 转换查询为可能的文件名模式
            patterns = [
                f"*{query}*.md",
                f"*{query.lower()}*.md",
                f"*{query.upper()}*.md",
                f"*{'_'.join(query.split())}*.md"
            ]
            
            found_files = []
            
            # 在 examples 目录中搜索
            for pattern in patterns:
                files = list(self.examples_dir.glob(pattern))
                found_files.extend(files)
            
            # 如果没找到，尝试更宽泛的搜索
            if not found_files:
                all_files = list(self.examples_dir.glob("*.md"))
                for file in all_files:
                    # 先检查文件名
                    if query.lower() in file.name.lower():
                        found_files.append(file)
                    else:
                        # 再尝试检查文件内容
                        try:
                            content = file.read_text(encoding='utf-8').lower()
                            if query.lower() in content:
                                found_files.append(file)
                        except Exception:
                            # 忽略读取错误
                            pass
            
            # 如果还是没找到，尝试使用关键词映射
            if not found_files and query:
                # 关键词映射
                keyword_mapping = {
                    '博客': 'blog',
                    'blog': 'blog',
                    '医院': 'hospital',
                    'hospital': 'hospital',
                    '用户': 'user',
                    'user': 'user',
                    '图书': 'library',
                    'library': 'library',
                    '借阅': 'borrowing',
                    'borrowing': 'borrowing'
                }
                
                # 尝试使用映射的关键词
                mapped_query = keyword_mapping.get(query.lower(), query.lower())
                if mapped_query != query.lower():
                    for file in all_files:
                        if mapped_query in file.name.lower():
                            found_files.append(file)
            
            # 去重
            found_files = list(set(found_files))
            
            if found_files:
                result = f"找到 {len(found_files)} 个相关的 PIM 文件:\n"
                for file in found_files:
                    relative_path = file.relative_to(self.pim_compiler_path)
                    result += f"- {relative_path}\n"
                    # 读取文件描述（前几行）
                    try:
                        with open(file, 'r', encoding='utf-8') as f:
                            first_lines = f.read(200).split('\n')[:3]
                            description = ' '.join(first_lines).strip()
                            result += f"  描述: {description[:100]}...\n"
                    except:
                        pass
                return result
            else:
                return f"未找到与 '{query}' 相关的 PIM 文件。可用的文件有：\n" + \
                       "\n".join([f"- {f.name}" for f in self.examples_dir.glob("*.md")])
                       
        except Exception as e:
            return f"搜索文件时出错: {str(e)}"
    
    def compile_pim(self, pim_file: str) -> str:
        """编译 PIM 文件
        
        Args:
            pim_file: PIM 文件路径（相对于 pim-compiler 目录）
            
        Returns:
            编译状态信息
        """
        try:
            # 清理文件路径参数
            pim_file = pim_file.strip().strip('"\'')
            
            # 如果只提供文件名，自动添加 examples/ 前缀
            if not '/' in pim_file and pim_file.endswith('.md'):
                # 先检查 examples 目录
                if (self.examples_dir / pim_file).exists():
                    pim_file = f"examples/{pim_file}"
            
            # 构建完整路径
            pim_path = self.pim_compiler_path / pim_file
            
            if not pim_path.exists():
                return f"错误: 文件 {pim_file} 不存在"
            
            # 生成输出目录名
            base_name = pim_path.stem
            output_dir = self.compiled_output_dir / base_name
            log_file = self.pim_compiler_path / f"{base_name}.log"
            
            # 构建编译命令
            cmd = f"cd {self.pim_compiler_path} && nohup ./pim-compiler {pim_file} --output {output_dir} > {log_file} 2>&1 &"
            
            # 执行编译命令
            process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # 获取后台进程的 PID
            time.sleep(0.5)  # 等待进程启动
            
            # 保存进程信息
            self.active_processes[base_name] = {
                'pid': process.pid,
                'log_file': str(log_file),
                'start_time': datetime.now(),
                'pim_file': pim_file,
                'output_dir': str(output_dir)
            }
            
            return f"""✅ 已启动编译任务:
- PIM 文件: {pim_file}
- 输出目录: {output_dir}
- 日志文件: {log_file}
- 进程 PID: {process.pid}

使用 "查看日志" 命令查看编译进度。"""
            
        except Exception as e:
            return f"编译时出错: {str(e)}"
    
    def check_log(self, system_name: Optional[str] = None) -> str:
        """查看编译日志
        
        Args:
            system_name: 系统名称（可选）。如果不提供，显示所有活动的编译任务
            
        Returns:
            日志内容和进度信息
        """
        try:
            # 处理 "None" 字符串和空字符串
            if system_name in ["None", "none", "", None, " "] or not system_name:
                # 显示所有活动的编译任务
                if not self.active_processes:
                    # 尝试查找最近的日志文件
                    log_files = list(self.pim_compiler_path.glob("*.log"))
                    if log_files:
                        latest_log = max(log_files, key=lambda f: f.stat().st_mtime)
                        system_name = latest_log.stem
                    else:
                        return "没有活动的编译任务。请先使用编译命令启动一个任务。"
                else:
                    result = "活动的编译任务:\n"
                    for name, info in self.active_processes.items():
                        duration = (datetime.now() - info['start_time']).seconds
                        result += f"\n- {name}:\n"
                        result += f"  PIM 文件: {info['pim_file']}\n"
                        result += f"  运行时间: {duration}秒\n"
                        result += f"  日志文件: {info['log_file']}\n"
                    
                    if len(self.active_processes) == 1:
                        system_name = list(self.active_processes.keys())[0]
                        result += f"\n自动选择查看: {system_name}\n"
                    else:
                        return result + "\n请指定要查看的系统名称。"
            
            # 查找日志文件
            if system_name in self.active_processes:
                log_file = Path(self.active_processes[system_name]['log_file'])
            else:
                log_file = self.pim_compiler_path / f"{system_name}.log"
            
            if not log_file.exists():
                return f"未找到 {system_name} 的日志文件"
            
            # 读取日志内容
            with open(log_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 分析日志内容提取进度信息
            lines = content.split('\n')
            last_50_lines = '\n'.join(lines[-50:])  # 最后50行
            
            # 提取关键进度信息
            progress_info = []
            keywords = ['Step', '成功', '失败', 'ERROR', 'Generating', 'Generated', 'Compiling', 'Completed']
            
            for line in lines:
                if any(keyword in line for keyword in keywords):
                    progress_info.append(line.strip())
            
            # 构建进度报告
            result = f"📋 {system_name} 编译日志分析\n"
            result += f"日志文件: {log_file}\n"
            result += f"文件大小: {log_file.stat().st_size / 1024:.1f} KB\n"
            result += f"最后更新: {datetime.fromtimestamp(log_file.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            
            # 检查是否完成
            if "Compilation completed successfully" in content:
                result += "✅ 编译已成功完成！\n\n"
            elif "ERROR" in content or "error" in content:
                result += "❌ 编译过程中出现错误\n\n"
            else:
                result += "⏳ 编译正在进行中...\n\n"
            
            # 显示关键进度
            if progress_info:
                result += "关键进度信息:\n"
                for info in progress_info[-10:]:  # 最后10条关键信息
                    result += f"  {info}\n"
            
            result += f"\n最新日志（最后50行）:\n{'-'*60}\n{last_50_lines}\n{'-'*60}"
            
            return result
            
        except Exception as e:
            return f"查看日志时出错: {str(e)}"
    
    def list_compiled_projects(self, _: str = "") -> str:
        """列出已编译的项目"""
        try:
            if not self.compiled_output_dir.exists():
                return "还没有编译过任何项目"
            
            projects = list(self.compiled_output_dir.iterdir())
            if not projects:
                return "还没有编译过任何项目"
            
            result = f"已编译的项目 ({len(projects)} 个):\n"
            for project in projects:
                if project.is_dir():
                    # 统计文件数
                    file_count = len(list(project.rglob("*")))
                    # 获取修改时间
                    mtime = datetime.fromtimestamp(project.stat().st_mtime)
                    result += f"\n- {project.name}:\n"
                    result += f"  文件数: {file_count}\n"
                    result += f"  编译时间: {mtime.strftime('%Y-%m-%d %H:%M:%S')}\n"
                    result += f"  路径: {project}\n"
            
            return result
            
        except Exception as e:
            return f"列出项目时出错: {str(e)}"
    
    def clean_output(self, project_name: str) -> str:
        """清理编译输出"""
        try:
            # 清理项目名称中的空白字符
            project_name = project_name.strip()
            output_dir = self.compiled_output_dir / project_name
            if output_dir.exists():
                import shutil
                shutil.rmtree(output_dir)
                return f"✅ 已清理项目: {project_name}"
            else:
                return f"项目 {project_name} 不存在"
        except Exception as e:
            return f"清理时出错: {str(e)}"
    
    def stop_compilation(self, system_name: Optional[str] = None) -> str:
        """终止编译进程
        
        Args:
            system_name: 系统名称（可选）。如果不提供，显示所有活动的编译进程
            
        Returns:
            终止结果信息
        """
        try:
            import signal
            import psutil
            
            # 如果没有指定系统名称，列出所有活动的编译进程
            if not system_name:
                # 查找所有 pim-compiler 相关进程
                compiler_processes = []
                for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
                    try:
                        cmdline = ' '.join(proc.info['cmdline'] or [])
                        if 'pim-compiler' in cmdline or 'compile_pim.py' in cmdline:
                            compiler_processes.append({
                                'pid': proc.info['pid'],
                                'name': proc.info['name'],
                                'cmdline': cmdline,
                                'running_time': time.time() - proc.info['create_time']
                            })
                    except:
                        pass
                
                if not compiler_processes:
                    return "没有找到活动的编译进程"
                
                result = f"找到 {len(compiler_processes)} 个编译进程:\n"
                for p in compiler_processes:
                    result += f"\n- PID {p['pid']}: {p['name']}\n"
                    result += f"  命令: {p['cmdline'][:100]}...\n" if len(p['cmdline']) > 100 else f"  命令: {p['cmdline']}\n"
                    result += f"  运行时间: {p['running_time']:.1f}秒\n"
                
                result += "\n使用 '终止编译 <系统名>' 来终止特定的编译任务"
                return result
            
            # 查找对应系统的日志文件
            log_file = self.pim_compiler_path / f"{system_name}.log"
            if not log_file.exists():
                return f"未找到 {system_name} 的编译任务"
            
            # 查找相关的编译进程
            killed_count = 0
            processes_info = []
            
            # 1. 查找 pim-compiler 进程
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = ' '.join(proc.info['cmdline'] or [])
                    # 检查是否包含系统名称
                    if ('pim-compiler' in cmdline and system_name in cmdline) or \
                       (f"{system_name}.log" in cmdline) or \
                       (f"compiled_output/{system_name}" in cmdline):
                        processes_info.append({
                            'pid': proc.info['pid'],
                            'name': proc.info['name'],
                            'cmdline': cmdline[:100] + '...' if len(cmdline) > 100 else cmdline
                        })
                        proc.terminate()
                        killed_count += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # 2. 查找可能的 Python 编译进程
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['name'] in ['python', 'python3']:
                        cmdline = ' '.join(proc.info['cmdline'] or [])
                        if system_name in cmdline and ('compile' in cmdline or 'pim' in cmdline):
                            processes_info.append({
                                'pid': proc.info['pid'],
                                'name': proc.info['name'],
                                'cmdline': cmdline[:100] + '...' if len(cmdline) > 100 else cmdline
                            })
                            proc.terminate()
                            killed_count += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # 3. 从 active_processes 中查找
            if system_name in self.active_processes:
                pid = self.active_processes[system_name]['pid']
                try:
                    proc = psutil.Process(pid)
                    if proc.is_running():
                        processes_info.append({
                            'pid': pid,
                            'name': 'pim-compiler',
                            'cmdline': f"编译 {self.active_processes[system_name]['pim_file']}"
                        })
                        proc.terminate()
                        killed_count += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
                
                # 从活动列表中移除
                del self.active_processes[system_name]
            
            # 构建结果消息
            if killed_count > 0:
                result = f"✅ 已终止 {system_name} 的 {killed_count} 个编译进程:\n"
                for p in processes_info:
                    result += f"\n- PID {p['pid']}: {p['name']}\n"
                    result += f"  {p['cmdline']}\n"
                
                # 在日志文件中添加终止标记
                try:
                    with open(log_file, 'a', encoding='utf-8') as f:
                        f.write(f"\n\n{'='*60}\n")
                        f.write(f"❌ 编译被用户终止 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                        f.write(f"{'='*60}\n")
                except:
                    pass
                
                return result
            else:
                # 检查日志文件最后修改时间
                mtime = time.time() - log_file.stat().st_mtime
                if mtime > 300:  # 超过5分钟
                    return f"未找到 {system_name} 的活动编译进程（日志文件最后更新于 {mtime/60:.1f} 分钟前）"
                else:
                    return f"未找到 {system_name} 的活动编译进程，可能已经完成或终止"
            
        except ImportError:
            return "❌ 错误: 需要安装 psutil 库。请运行: pip install psutil"
        except Exception as e:
            return f"终止编译时出错: {str(e)}"


def create_pim_compiler_agent(llm_config: Optional[Dict[str, Any]] = None):
    """创建 PIM 编译器智能体"""
    
    # 初始化工具
    tools_instance = PIMCompilerTools()
    
    # 创建通用的参数清理函数
    def clean_param(param: str) -> str:
        """清理 LangChain 传递的参数"""
        if not param:
            return ""
        # 去除首尾空白和引号
        cleaned = param.strip()
        # 去除可能的引号（单引号或双引号）
        while cleaned and cleaned[0] in '"\'':
            cleaned = cleaned[1:]
        while cleaned and cleaned[-1] in '"\'':
            cleaned = cleaned[:-1]
        # 再次去除空白
        cleaned = cleaned.strip()
        return cleaned
    
    # 为所有工具创建包装函数
    def search_pim_files_wrapper(query: str) -> str:
        """包装搜索函数"""
        return tools_instance.search_pim_files(clean_param(query))
    
    def compile_pim_wrapper(pim_file: str) -> str:
        """包装编译函数"""
        return tools_instance.compile_pim(clean_param(pim_file))
    
    def check_log_wrapper(system_name: str = "") -> str:
        """包装日志查看函数"""
        cleaned = clean_param(system_name)
        if not cleaned or cleaned.lower() in ["none", ""]:
            return tools_instance.check_log(None)
        return tools_instance.check_log(cleaned)
    
    def list_compiled_projects_wrapper(_: str = "") -> str:
        """包装项目列表函数"""
        return tools_instance.list_compiled_projects("")
    
    def clean_output_wrapper(project_name: str) -> str:
        """包装清理函数"""
        return tools_instance.clean_output(clean_param(project_name))
    
    def stop_compilation_wrapper(system_name: str = "") -> str:
        """包装终止编译函数"""
        cleaned = clean_param(system_name)
        if not cleaned or cleaned.lower() in ["none", ""]:
            return tools_instance.stop_compilation(None)
        return tools_instance.stop_compilation(cleaned)
    
    # 定义工具
    tools = [
        Tool(
            name="search_pim_files",
            func=search_pim_files_wrapper,
            description="搜索 PIM 文件。输入搜索关键词（如'医院'、'hospital'），返回匹配的文件列表。"
        ),
        Tool(
            name="compile_pim",
            func=compile_pim_wrapper,
            description="编译 PIM 文件。输入文件路径（如 'examples/smart_hospital_system.md' 或 'blog.md'），启动后台编译进程。"
        ),
        Tool(
            name="check_log",
            func=check_log_wrapper,
            description="查看编译日志和进度。可选输入系统名称，不输入则显示所有活动任务。"
        ),
        Tool(
            name="list_compiled_projects",
            func=list_compiled_projects_wrapper,
            description="列出所有已编译的项目"
        ),
        Tool(
            name="clean_output",
            func=clean_output_wrapper,
            description="清理编译输出。输入项目名称。"
        ),
        Tool(
            name="stop_compilation",
            func=stop_compilation_wrapper,
            description="终止编译进程。可选输入系统名称，不输入则显示所有活动的编译进程。"
        )
    ]
    
    # 创建 LLM
    if llm_config is None:
        llm_config = {
            "model": "gpt-3.5-turbo",
            "temperature": 0.3,
            "max_tokens": 2000
        }
    
    # 确保参数名正确
    if "openai_api_key" in llm_config:
        llm_config["api_key"] = llm_config.pop("openai_api_key")
    if "openai_api_base" in llm_config:
        llm_config["base_url"] = llm_config.pop("openai_api_base")
    if "model_name" in llm_config:
        llm_config["model"] = llm_config.pop("model_name")
    
    llm = ChatOpenAI(**llm_config)
    
    # 创建 ReAct 提示模板
    react_prompt = PromptTemplate.from_template("""你是 PIM 编译器助手，专门帮助用户编译 PIM（平台无关模型）文件。

你可以使用以下工具：

{tools}

使用以下格式回答问题：

Question: 需要回答的输入问题
Thought: 你应该思考要做什么
Action: 要采取的动作，应该是 [{tool_names}] 中的一个
Action Input: 动作的输入
Observation: 动作的结果
... (Thought/Action/Action Input/Observation 可以重复多次)
Thought: 我现在知道最终答案了
Final Answer: 对原始输入问题的最终答案

用户常见的指令模式：
- "编译XX系统" → 使用 search_pim_files 搜索相关文件 → 使用 compile_pim 编译
- "查看日志" → 使用 check_log 查看编译进度
- "列出项目" → 使用 list_compiled_projects 显示项目
- "终止编译" → 使用 stop_compilation 终止编译进程
- "停止XX编译" → 使用 stop_compilation 终止特定系统的编译

注意：
1. 当用户说"编译医院系统"时，先用 search_pim_files 搜索 "hospital" 或 "医院"
2. 找到文件后，使用完整路径调用 compile_pim
3. 编译后用户可以用 check_log 查看进度
4. 如果需要终止编译，使用 stop_compilation，可以指定系统名称

开始！

Question: {input}
Thought:{agent_scratchpad}""")
    
    # 创建 ReAct agent
    agent = create_react_agent(
        llm=llm,
        tools=tools,
        prompt=react_prompt
    )
    
    # 创建 agent executor
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        max_iterations=5,
        handle_parsing_errors=True
    )
    
    return agent_executor


def main():
    """主函数 - 交互式聊天机器人"""
    # 确保在正确的目录下运行
    import os
    script_dir = Path(__file__).parent.parent
    os.chdir(script_dir)
    
    # 导入 readline 以支持命令历史
    try:
        import readline
        # 设置历史文件
        history_file = Path.home() / ".pim_compiler_chatbot_history"
        
        # 加载历史记录
        if history_file.exists():
            readline.read_history_file(str(history_file))
        
        # 设置历史记录大小
        readline.set_history_length(1000)
        
        # 启用 tab 补全（可选）
        readline.parse_and_bind("tab: complete")
        
    except ImportError:
        # Windows 系统可能没有 readline
        pass
    
    print("🤖 PIM 编译器助手")
    print("=" * 60)
    print("我可以帮助你：")
    print("- 搜索和编译 PIM 文件")
    print("- 查看编译进度和日志")
    print("- 管理编译输出")
    print("\n示例命令：")
    print('- "编译医院系统"')
    print('- "查看日志"')
    print('- "列出所有项目"')
    print('- "终止编译"')
    print('- "停止博客编译"')
    print("\n输入 'exit' 退出\n")
    
    # 检查 API key
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  警告: 未设置 OPENAI_API_KEY")
        print("请设置环境变量或使用其他 LLM 配置")
        
        # 尝试使用 DeepSeek
        deepseek_key = os.getenv("DEEPSEEK_API_KEY")
        if deepseek_key:
            llm_config = {
                "api_key": deepseek_key,
                "base_url": "https://api.deepseek.com/v1",
                "model": "deepseek-chat",
                "temperature": 0.3
            }
            print(f"✅ 使用 DeepSeek 模型: deepseek-chat")
        else:
            print("❌ 未设置 DEEPSEEK_API_KEY")
            print("请运行: export DEEPSEEK_API_KEY='your-api-key'")
            return
    else:
        llm_config = None
    
    # 创建 agent
    agent = create_pim_compiler_agent(llm_config)
    
    # 交互循环
    while True:
        try:
            user_input = input("\n你: ").strip()
            
            if user_input.lower() in ['exit', 'quit', 'bye']:
                print("\n👋 再见！")
                break
            
            if not user_input:
                continue
            
            # 执行 agent
            result = agent.invoke({"input": user_input})
            
            print(f"\n助手: {result['output']}")
            
        except KeyboardInterrupt:
            print("\n\n👋 再见！")
            break
        except Exception as e:
            print(f"\n❌ 出错了: {str(e)}")
            import traceback
            traceback.print_exc()
    
    # 保存历史记录
    try:
        import readline
        history_file = Path.home() / ".pim_compiler_chatbot_history"
        readline.write_history_file(str(history_file))
    except:
        pass


if __name__ == "__main__":
    main()