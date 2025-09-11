#!/usr/bin/env python3
"""
Claude Code Tool - 调用Claude Code CLI进行代码分析和生成
"""

import os
import sys
import subprocess
import json
from typing import Optional, Dict, Any

# 添加父目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tool_base import Function


class ClaudeCodeTool(Function):
    """Claude Code Tool - 调用Claude Code进行代码分析"""
    
    def __init__(self):
        super().__init__(
            name="claude_code",
            description="调用Claude Code CLI进行代码分析、生成和重构",
            parameters={
                "action": {
                    "type": "string",
                    "enum": [
                        "analyze",      # 分析代码
                        "generate",     # 生成代码
                        "refactor",     # 重构代码
                        "review",       # 代码审查
                        "explain",      # 解释代码
                        "fix",          # 修复问题
                        "test",         # 生成测试
                        "custom"        # 自定义命令
                    ],
                    "description": "操作类型"
                },
                "prompt": {
                    "type": "string",
                    "description": "给Claude Code的提示词，描述要执行的任务"
                },
                "files": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "要处理的文件列表（可选）"
                },
                "max_turns": {
                    "type": "integer",
                    "description": "最大对话轮数（默认10）",
                    "default": 10
                },
                "output_file": {
                    "type": "string",
                    "description": "输出文件路径（可选）"
                },
                "custom_command": {
                    "type": "string",
                    "description": "自定义的完整claude命令（当action为custom时使用）"
                }
            }
        )
        
        # 检查claude命令是否可用
        self.claude_available = self._check_claude_available()
    
    def _check_claude_available(self) -> bool:
        """检查claude命令是否可用"""
        try:
            result = subprocess.run(
                ["which", "claude"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False
    
    def execute(self, **kwargs) -> str:
        """执行Claude Code操作"""
        if not self.claude_available:
            return "❌ Claude Code CLI不可用，请先安装: npm install -g @anthropic/claude-cli"
        
        action = kwargs.get('action')
        prompt = kwargs.get('prompt', '')
        files = kwargs.get('files', [])
        max_turns = kwargs.get('max_turns', 10)
        output_file = kwargs.get('output_file')
        custom_command = kwargs.get('custom_command')
        
        # 处理不同的action
        if action == 'custom' and custom_command:
            return self._execute_custom(custom_command)
        
        # 构建标准命令
        cmd = self._build_command(action, prompt, files, max_turns, output_file)
        if not cmd:
            return f"❌ 无法构建命令，action={action}"
        
        return self._execute_command(cmd)
    
    def _build_command(self, action: str, prompt: str, files: list, 
                      max_turns: int, output_file: Optional[str]) -> Optional[list]:
        """构建Claude命令"""
        if not prompt and action != 'custom':
            return None
        
        # 基础命令 - 使用 -p 参数让claude直接输出结果
        cmd = ["claude", "-p"]
        
        # 构建完整的prompt，包含文件内容
        full_prompt = ""
        
        # 如果有文件，读取文件内容并包含在prompt中
        if files:
            file_contents = []
            for file_path in files:
                if os.path.exists(file_path):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            file_contents.append(f"文件: {file_path}\n```\n{content}\n```")
                    except Exception as e:
                        file_contents.append(f"无法读取文件 {file_path}: {e}")
            
            if file_contents:
                full_prompt = "\n".join(file_contents) + "\n\n"
        
        # 添加action特定的prompt
        if action == 'analyze':
            full_prompt += f"请分析上述代码：{prompt}"
        elif action == 'generate':
            full_prompt += f"生成代码：{prompt}"
        elif action == 'refactor':
            full_prompt += f"重构上述代码：{prompt}"
        elif action == 'review':
            full_prompt += f"审查上述代码并提供改进建议：{prompt}"
        elif action == 'explain':
            full_prompt += f"详细解释上述代码的功能和实现：{prompt}"
        elif action == 'fix':
            full_prompt += f"修复以下问题：{prompt}"
        elif action == 'test':
            full_prompt += f"为上述代码生成测试：{prompt}"
        else:
            full_prompt += prompt
        
        cmd.append(full_prompt)
        
        # claude的-p模式不支持max-turns，它会直接输出结果
        # 所以我们不添加--max-turns参数
        
        return cmd
    
    def _execute_command(self, cmd: list) -> str:
        """执行命令并返回结果"""
        try:
            # 记录执行的命令
            cmd_str = ' '.join(cmd)
            
            # 使用subprocess.run更简单可靠
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            # 构建返回结果
            output_lines = []
            output_lines.append(f"🚀 执行命令: {cmd_str}\n")
            
            if result.returncode == 0:
                output_lines.append("✅ Claude Code执行成功\n")
                if result.stdout:
                    # 限制输出长度
                    lines = result.stdout.split('\n')
                    if len(lines) > 50:
                        output_lines.append(f"\n📝 输出（显示最后50行）:\n")
                        output_lines.extend(lines[-50:])
                    else:
                        output_lines.append(f"\n📝 输出:\n{result.stdout}")
            else:
                output_lines.append(f"❌ Claude Code执行失败 (返回码: {result.returncode})\n")
                if result.stderr:
                    output_lines.append(f"\n错误信息:\n{result.stderr}")
                if result.stdout:
                    output_lines.append(f"\n输出:\n{result.stdout}")
            
            return '\n'.join(output_lines)
            
        except subprocess.TimeoutExpired:
            return "❌ 命令执行超时（60秒）"
        except Exception as e:
            return f"❌ 执行命令失败: {str(e)}"
    
    def _execute_custom(self, custom_command: str) -> str:
        """执行自定义命令"""
        try:
            # 直接执行自定义命令
            result = subprocess.run(
                custom_command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            output = []
            output.append(f"🚀 执行自定义命令: {custom_command}\n")
            
            if result.returncode == 0:
                output.append("✅ 执行成功\n")
                if result.stdout:
                    # 限制输出长度
                    lines = result.stdout.split('\n')
                    if len(lines) > 50:
                        output.append(f"\n输出（显示最后50行）:\n")
                        output.extend(lines[-50:])
                    else:
                        output.append(f"\n输出:\n{result.stdout}")
            else:
                output.append(f"❌ 执行失败 (返回码: {result.returncode})\n")
                if result.stderr:
                    output.append(f"\n错误:\n{result.stderr}")
            
            return '\n'.join(output)
            
        except subprocess.TimeoutExpired:
            return "❌ 自定义命令执行超时（60秒）"
        except Exception as e:
            return f"❌ 执行自定义命令失败: {str(e)}"


# 测试代码
if __name__ == "__main__":
    tool = ClaudeCodeTool()
    
    # 测试分析代码
    result = tool.execute(
        action="analyze",
        prompt="分析当前目录的Python代码结构",
        max_turns=5
    )
    print(result)