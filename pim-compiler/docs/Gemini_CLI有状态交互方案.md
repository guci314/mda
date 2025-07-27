# Gemini CLI 有状态多步骤交互实现方案

## 概述

Gemini CLI 默认是无状态的，每次调用都是独立的。但在实际应用中，我们经常需要有状态的多步骤交互。本文档提供多种实现方案。

## 方案对比

| 方案 | 优点 | 缺点 | 适用场景 |
|------|------|------|----------|
| Checkpointing | 原生支持，简单 | 仅限交互模式 | 人工交互 |
| 上下文注入 | 灵活，可控 | 需要管理上下文 | 脚本自动化 |
| 会话文件 | 持久化，可恢复 | 实现复杂 | 长时间任务 |
| Expect 脚本 | 真正的交互 | 复杂，平台限制 | 复杂交互 |
| API 封装 | 完全控制 | 需要开发 | 生产环境 |

## 方案1：使用 Checkpointing（交互模式）

### 基础用法

```bash
# 启用 checkpointing 的交互模式
gemini -c
gemini --checkpointing

# 会话会自动保存，可以引用之前的对话
```

### 脚本化交互

```bash
#!/bin/bash
# interactive-session.sh

# 创建命名管道
mkfifo gemini_pipe

# 启动 Gemini CLI 并重定向输入
gemini -c < gemini_pipe &
GEMINI_PID=$!

# 发送命令到 Gemini
send_to_gemini() {
    echo "$1" > gemini_pipe
}

# 示例：多步骤交互
send_to_gemini "创建一个用户管理系统的数据模型"
sleep 2
send_to_gemini "基于上面的模型，生成 SQLAlchemy 代码"
sleep 2
send_to_gemini "为这些模型添加验证方法"

# 清理
kill $GEMINI_PID
rm gemini_pipe
```

## 方案2：上下文注入（推荐）

### 基础实现

```bash
#!/bin/bash
# stateful-gemini.sh - 有状态的 Gemini CLI 封装

# 初始化会话目录
SESSION_DIR="${GEMINI_SESSION_DIR:-/tmp/gemini_sessions}"
SESSION_ID="${1:-$(date +%s)}"
SESSION_PATH="$SESSION_DIR/$SESSION_ID"

mkdir -p "$SESSION_PATH"

# 初始化会话文件
CONTEXT_FILE="$SESSION_PATH/context.txt"
HISTORY_FILE="$SESSION_PATH/history.json"
STATE_FILE="$SESSION_PATH/state.json"

# 初始化状态
init_session() {
    echo "[]" > "$HISTORY_FILE"
    echo '{"step": 0, "variables": {}}' > "$STATE_FILE"
    echo "会话已初始化: $SESSION_ID"
}

# 添加到历史
add_to_history() {
    local role="$1"
    local content="$2"
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    
    jq ". += [{\"role\": \"$role\", \"content\": \"$content\", \"timestamp\": \"$timestamp\"}]" \
        "$HISTORY_FILE" > "$HISTORY_FILE.tmp" && mv "$HISTORY_FILE.tmp" "$HISTORY_FILE"
}

# 获取上下文
get_context() {
    local max_history="${1:-5}"
    
    echo "=== 对话历史 ==="
    jq -r ".[-$max_history:] | .[] | \"\\(.role): \\(.content)\"" "$HISTORY_FILE" 2>/dev/null || echo ""
    echo "=== 当前状态 ==="
    cat "$STATE_FILE"
}

# 有状态的 Gemini 调用
stateful_gemini() {
    local prompt="$1"
    local include_context="${2:-true}"
    
    # 构建完整提示
    local full_prompt=""
    if [ "$include_context" = "true" ]; then
        local context=$(get_context)
        full_prompt="基于以下上下文：
$context

当前请求：$prompt

请考虑之前的对话和状态来回答。"
    else
        full_prompt="$prompt"
    fi
    
    # 添加用户输入到历史
    add_to_history "user" "$prompt"
    
    # 调用 Gemini
    local response=$(echo "$full_prompt" | gemini)
    
    # 添加响应到历史
    add_to_history "assistant" "$response"
    
    # 更新步骤计数
    local current_step=$(jq -r '.step' "$STATE_FILE")
    jq ".step = $((current_step + 1))" "$STATE_FILE" > "$STATE_FILE.tmp" && \
        mv "$STATE_FILE.tmp" "$STATE_FILE"
    
    echo "$response"
}

# 更新状态变量
set_state_var() {
    local key="$1"
    local value="$2"
    
    jq ".variables.\"$key\" = \"$value\"" "$STATE_FILE" > "$STATE_FILE.tmp" && \
        mv "$STATE_FILE.tmp" "$STATE_FILE"
}

# 获取状态变量
get_state_var() {
    local key="$1"
    jq -r ".variables.\"$key\" // \"\"" "$STATE_FILE"
}

# 使用示例
if [ "$0" = "${BASH_SOURCE[0]}" ]; then
    init_session
    
    # 步骤1：创建数据模型
    echo "=== 步骤1：创建数据模型 ==="
    response1=$(stateful_gemini "创建一个电商系统的用户和订单数据模型")
    echo "$response1"
    set_state_var "model_created" "true"
    
    echo -e "\n=== 步骤2：生成代码 ==="
    response2=$(stateful_gemini "基于上面的数据模型，生成 FastAPI 的 SQLAlchemy 模型代码")
    echo "$response2"
    set_state_var "code_generated" "true"
    
    echo -e "\n=== 步骤3：添加业务逻辑 ==="
    response3=$(stateful_gemini "为订单模型添加计算总价的方法，考虑折扣和税率")
    echo "$response3"
    
    echo -e "\n=== 会话摘要 ==="
    stateful_gemini "总结我们刚才完成的工作" false
fi
```

### 高级状态管理

```bash
#!/bin/bash
# advanced-state-manager.sh

class_StatefulGemini() {
    local session_id="$1"
    local session_dir="/tmp/gemini_sessions/$session_id"
    
    # 构造函数
    mkdir -p "$session_dir"
    
    # 方法：执行步骤
    execute_step() {
        local step_name="$1"
        local prompt="$2"
        local dependencies="$3"
        
        # 检查依赖
        if [ -n "$dependencies" ]; then
            for dep in $dependencies; do
                if [ ! -f "$session_dir/steps/$dep.completed" ]; then
                    echo "错误：依赖步骤 $dep 未完成"
                    return 1
                fi
            done
        fi
        
        # 构建上下文
        local context=""
        if [ -d "$session_dir/steps" ]; then
            for completed in "$session_dir/steps"/*.output; do
                if [ -f "$completed" ]; then
                    context="$context\n$(cat "$completed")"
                fi
            done
        fi
        
        # 执行步骤
        mkdir -p "$session_dir/steps"
        echo "执行步骤：$step_name"
        
        local full_prompt="已完成的步骤输出：$context\n\n当前步骤：$prompt"
        local output=$(echo "$full_prompt" | gemini)
        
        # 保存输出
        echo "$output" > "$session_dir/steps/$step_name.output"
        touch "$session_dir/steps/$step_name.completed"
        
        echo "$output"
    }
    
    # 方法：获取步骤输出
    get_step_output() {
        local step_name="$1"
        cat "$session_dir/steps/$step_name.output" 2>/dev/null
    }
    
    # 方法：重置会话
    reset_session() {
        rm -rf "$session_dir"
        mkdir -p "$session_dir"
    }
}
```

## 方案3：持久化会话文件

```bash
#!/bin/bash
# persistent-session.sh

# 会话管理器
class SessionManager {
    constructor() {
        this.sessions_dir="${GEMINI_SESSIONS_DIR:-$HOME/.gemini/sessions}"
        mkdir -p "$this.sessions_dir"
    }
    
    create_session() {
        local name="$1"
        local session_file="$this.sessions_dir/$name.session"
        
        cat > "$session_file" << EOF
{
    "id": "$name",
    "created": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
    "messages": [],
    "context": {},
    "metadata": {}
}
EOF
        echo "$session_file"
    }
    
    load_session() {
        local name="$1"
        local session_file="$this.sessions_dir/$name.session"
        
        if [ -f "$session_file" ]; then
            cat "$session_file"
        else
            echo "{}"
        fi
    }
    
    save_message() {
        local session_name="$1"
        local role="$2"
        local content="$3"
        local session_file="$this.sessions_dir/$session_name.session"
        
        # 添加消息到会话
        local temp_file=$(mktemp)
        jq ".messages += [{
            \"role\": \"$role\",
            \"content\": \"$content\",
            \"timestamp\": \"$(date -u +"%Y-%m-%dT%H:%M:%SZ")\"
        }]" "$session_file" > "$temp_file" && mv "$temp_file" "$session_file"
    }
    
    get_conversation_context() {
        local session_name="$1"
        local max_messages="${2:-10}"
        local session_file="$this.sessions_dir/$session_name.session"
        
        jq -r ".messages[-$max_messages:] | 
            map(\"\\(.role): \\(.content)\") | 
            join(\"\\n\")" "$session_file"
    }
}

# 使用持久化会话
use_persistent_session() {
    local session_name="${1:-default}"
    local manager=$(SessionManager new)
    
    # 创建或加载会话
    if [ ! -f "$HOME/.gemini/sessions/$session_name.session" ]; then
        $manager.create_session "$session_name"
    fi
    
    # 交互函数
    chat() {
        local message="$1"
        
        # 获取历史上下文
        local context=$($manager.get_conversation_context "$session_name")
        
        # 构建提示
        local prompt="对话历史：
$context

用户：$message

请基于对话历史回答。"
        
        # 保存用户消息
        $manager.save_message "$session_name" "user" "$message"
        
        # 调用 Gemini
        local response=$(echo "$prompt" | gemini)
        
        # 保存助手响应
        $manager.save_message "$session_name" "assistant" "$response"
        
        echo "$response"
    }
    
    # 导出 chat 函数
    export -f chat
}
```

## 方案4：使用 Expect 脚本（真正的交互）

```expect
#!/usr/bin/expect
# gemini-interactive.exp

set timeout 30
set session_log "gemini_session.log"

# 启动 Gemini CLI
spawn gemini -c

# 等待提示符
expect ">"

# 日志记录
log_file -a $session_log

# 步骤1：创建模型
send "创建一个博客系统的数据模型，包括文章、用户和评论\r"
expect ">"

# 步骤2：基于前面的回答
send "将上面的数据模型转换为 Prisma schema\r"
expect ">"

# 步骤3：继续构建
send "基于这个 schema，生成相应的 GraphQL 类型定义\r"
expect ">"

# 步骤4：生成解析器
send "为这些 GraphQL 类型生成解析器函数\r"
expect ">"

# 保存并退出
send "exit\r"
expect eof
```

### Python Expect 包装器

```python
#!/usr/bin/env python3
# gemini_stateful.py

import pexpect
import json
import time
from datetime import datetime
from typing import List, Dict, Any

class StatefulGeminiCLI:
    def __init__(self, checkpoint: bool = True):
        self.checkpoint = checkpoint
        self.session = None
        self.history: List[Dict[str, Any]] = []
        self.context: Dict[str, Any] = {}
        
    def start_session(self):
        """启动 Gemini CLI 会话"""
        cmd = "gemini"
        if self.checkpoint:
            cmd += " -c"
            
        self.session = pexpect.spawn(cmd, encoding='utf-8')
        self.session.expect('>')
        
    def send_command(self, command: str) -> str:
        """发送命令并获取响应"""
        if not self.session:
            self.start_session()
            
        # 记录发送的命令
        self.history.append({
            'timestamp': datetime.now().isoformat(),
            'type': 'user',
            'content': command
        })
        
        # 发送命令
        self.session.sendline(command)
        
        # 等待响应
        self.session.expect('>', timeout=60)
        response = self.session.before.strip()
        
        # 记录响应
        self.history.append({
            'timestamp': datetime.now().isoformat(),
            'type': 'assistant',
            'content': response
        })
        
        return response
    
    def multi_step_execution(self, steps: List[Dict[str, str]]) -> List[str]:
        """执行多步骤任务"""
        results = []
        
        for i, step in enumerate(steps):
            print(f"\n=== 执行步骤 {i+1}: {step['name']} ===")
            
            # 检查依赖
            if 'depends_on' in step:
                for dep_idx in step['depends_on']:
                    if dep_idx >= len(results) or not results[dep_idx]:
                        raise Exception(f"依赖步骤 {dep_idx} 未完成")
            
            # 构建带上下文的提示
            prompt = step['prompt']
            if 'use_context' in step and step['use_context']:
                context_info = self._build_context_info(results, step.get('context_steps', []))
                prompt = f"{context_info}\n\n{prompt}"
            
            # 执行步骤
            result = self.send_command(prompt)
            results.append(result)
            
            # 保存到上下文
            if 'save_as' in step:
                self.context[step['save_as']] = result
                
            # 可选：步骤间延迟
            if 'delay' in step:
                time.sleep(step['delay'])
                
        return results
    
    def _build_context_info(self, results: List[str], context_steps: List[int]) -> str:
        """构建上下文信息"""
        context_parts = []
        
        if context_steps:
            for idx in context_steps:
                if idx < len(results):
                    context_parts.append(f"步骤 {idx+1} 的输出：\n{results[idx]}")
        else:
            # 使用所有之前的结果
            for i, result in enumerate(results):
                context_parts.append(f"步骤 {i+1} 的输出：\n{result}")
                
        return "\n\n".join(context_parts)
    
    def save_session(self, filename: str):
        """保存会话到文件"""
        session_data = {
            'history': self.history,
            'context': self.context,
            'timestamp': datetime.now().isoformat()
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, ensure_ascii=False, indent=2)
            
    def close(self):
        """关闭会话"""
        if self.session:
            self.session.sendline('exit')
            self.session.close()

# 使用示例
if __name__ == "__main__":
    # 创建有状态的 Gemini CLI
    gemini = StatefulGeminiCLI(checkpoint=True)
    
    # 定义多步骤任务
    steps = [
        {
            'name': '创建数据模型',
            'prompt': '设计一个任务管理系统的数据模型，包括项目、任务、用户和标签',
            'save_as': 'data_model'
        },
        {
            'name': '生成数据库架构',
            'prompt': '基于上面的数据模型，生成 PostgreSQL 的建表语句',
            'depends_on': [0],
            'use_context': True,
            'context_steps': [0]
        },
        {
            'name': '生成 API 接口',
            'prompt': '基于数据模型，设计 RESTful API 接口，包括所有 CRUD 操作',
            'depends_on': [0],
            'use_context': True,
            'context_steps': [0]
        },
        {
            'name': '生成示例代码',
            'prompt': '基于上面的 API 设计，生成 FastAPI 的实现代码',
            'depends_on': [2],
            'use_context': True,
            'context_steps': [0, 2]
        }
    ]
    
    try:
        # 执行多步骤任务
        results = gemini.multi_step_execution(steps)
        
        # 保存会话
        gemini.save_session('task_management_session.json')
        
        # 生成最终报告
        report_prompt = "基于我们刚才的所有工作，生成一个项目实施报告"
        report = gemini.send_command(report_prompt)
        
        print("\n=== 最终报告 ===")
        print(report)
        
    finally:
        gemini.close()
```

## 方案5：API 封装服务

```python
#!/usr/bin/env python3
# gemini_state_server.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import subprocess
import json
import uuid
from datetime import datetime
import asyncio
from concurrent.futures import ThreadPoolExecutor

app = FastAPI()

# 会话存储
sessions: Dict[str, 'GeminiSession'] = {}

class GeminiSession:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.created_at = datetime.now()
        self.messages: List[Dict[str, Any]] = []
        self.context: Dict[str, Any] = {}
        self.state: Dict[str, Any] = {'step': 0}
        
    def add_message(self, role: str, content: str):
        self.messages.append({
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat()
        })
        
    def get_context_prompt(self, max_messages: int = 10) -> str:
        recent_messages = self.messages[-max_messages:]
        context_str = "\n".join([
            f"{msg['role']}: {msg['content']}" 
            for msg in recent_messages
        ])
        return f"对话历史：\n{context_str}"

class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    message: str
    include_context: bool = True
    max_context_messages: int = 10

class ChatResponse(BaseModel):
    session_id: str
    response: str
    step: int

class SessionInfo(BaseModel):
    session_id: str
    created_at: str
    message_count: int
    current_step: int

executor = ThreadPoolExecutor(max_workers=10)

def call_gemini_cli(prompt: str) -> str:
    """调用 Gemini CLI"""
    try:
        result = subprocess.run(
            ['gemini'],
            input=prompt,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        raise Exception(f"Gemini CLI 错误: {e.stderr}")

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """有状态的聊天接口"""
    # 获取或创建会话
    if request.session_id and request.session_id in sessions:
        session = sessions[request.session_id]
    else:
        session_id = str(uuid.uuid4())
        session = GeminiSession(session_id)
        sessions[session_id] = session
        
    # 添加用户消息
    session.add_message("user", request.message)
    
    # 构建提示
    if request.include_context and len(session.messages) > 1:
        context = session.get_context_prompt(request.max_context_messages)
        full_prompt = f"{context}\n\n用户: {request.message}\n\n基于对话历史回答："
    else:
        full_prompt = request.message
        
    # 异步调用 Gemini CLI
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(executor, call_gemini_cli, full_prompt)
    
    # 添加响应
    session.add_message("assistant", response)
    session.state['step'] += 1
    
    return ChatResponse(
        session_id=session.session_id,
        response=response,
        step=session.state['step']
    )

@app.get("/sessions", response_model=List[SessionInfo])
async def list_sessions():
    """列出所有会话"""
    return [
        SessionInfo(
            session_id=session.session_id,
            created_at=session.created_at.isoformat(),
            message_count=len(session.messages),
            current_step=session.state['step']
        )
        for session in sessions.values()
    ]

@app.get("/session/{session_id}/history")
async def get_session_history(session_id: str):
    """获取会话历史"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="会话不存在")
        
    session = sessions[session_id]
    return {
        'session_id': session_id,
        'messages': session.messages,
        'context': session.context,
        'state': session.state
    }

@app.post("/session/{session_id}/context")
async def update_context(session_id: str, context: Dict[str, Any]):
    """更新会话上下文"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="会话不存在")
        
    sessions[session_id].context.update(context)
    return {"status": "success"}

@app.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """删除会话"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="会话不存在")
        
    del sessions[session_id]
    return {"status": "success"}

# 客户端示例
"""
import requests

# 创建会话并进行多步骤对话
base_url = "http://localhost:8000"

# 第一步
resp1 = requests.post(f"{base_url}/chat", json={
    "message": "创建一个博客系统的数据模型"
})
session_id = resp1.json()['session_id']

# 第二步（带上下文）
resp2 = requests.post(f"{base_url}/chat", json={
    "session_id": session_id,
    "message": "基于上面的模型生成 GraphQL schema",
    "include_context": True
})

# 第三步
resp3 = requests.post(f"{base_url}/chat", json={
    "session_id": session_id,
    "message": "为这个 schema 生成 resolver 函数",
    "include_context": True
})

# 查看完整历史
history = requests.get(f"{base_url}/session/{session_id}/history")
print(history.json())
"""

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## 最佳实践建议

### 1. 选择合适的方案

```bash
# 决策树
choose_solution() {
    local use_case="$1"
    
    case "$use_case" in
        "interactive")
            echo "使用 Checkpointing 或 Expect"
            ;;
        "automation")
            echo "使用上下文注入"
            ;;
        "long_running")
            echo "使用持久化会话"
            ;;
        "production")
            echo "使用 API 封装"
            ;;
        *)
            echo "使用上下文注入（通用方案）"
            ;;
    esac
}
```

### 2. 上下文管理策略

```bash
# 智能上下文裁剪
manage_context() {
    local context="$1"
    local max_tokens=4000
    
    # 计算 token 数（简化）
    local token_count=$(echo "$context" | wc -w)
    
    if [ $token_count -gt $max_tokens ]; then
        # 保留最重要的部分
        echo "$context" | tail -n 50
    else
        echo "$context"
    fi
}
```

### 3. 错误恢复

```bash
# 带重试的状态恢复
execute_with_recovery() {
    local session_id="$1"
    local step="$2"
    local max_retries=3
    
    for i in $(seq 1 $max_retries); do
        if execute_step "$session_id" "$step"; then
            return 0
        else
            echo "步骤失败，尝试恢复（$i/$max_retries）"
            # 从检查点恢复
            restore_from_checkpoint "$session_id" "$step"
        fi
    done
    
    return 1
}
```

## 完整示例：多步骤项目生成器

```bash
#!/bin/bash
# project-generator.sh - 完整的有状态项目生成器

source stateful-gemini.sh

generate_project() {
    local project_name="$1"
    local project_type="$2"
    
    # 初始化会话
    init_session "$project_name"
    
    # 步骤定义
    declare -A steps=(
        ["requirements"]="分析需求并创建项目规范"
        ["architecture"]="设计系统架构"
        ["models"]="创建数据模型"
        ["api"]="设计 API 接口"
        ["implementation"]="生成实现代码"
        ["tests"]="生成测试代码"
        ["documentation"]="生成文档"
    )
    
    # 执行顺序
    local order=("requirements" "architecture" "models" "api" "implementation" "tests" "documentation")
    
    # 执行每个步骤
    for step in "${order[@]}"; do
        echo -e "\n=== 执行: ${steps[$step]} ==="
        
        case "$step" in
            "requirements")
                stateful_gemini "为 $project_type 类型的 $project_name 项目创建详细需求规范"
                ;;
            "architecture")
                stateful_gemini "基于需求规范，设计系统架构，包括技术栈选择"
                ;;
            "models")
                stateful_gemini "基于架构设计，创建详细的数据模型"
                ;;
            "api")
                stateful_gemini "基于数据模型，设计完整的 API 接口"
                ;;
            "implementation")
                stateful_gemini "基于 API 设计，生成完整的实现代码"
                ;;
            "tests")
                stateful_gemini "为实现的代码生成完整的测试套件"
                ;;
            "documentation")
                stateful_gemini "基于所有前面的工作，生成项目文档"
                ;;
        esac
        
        # 保存步骤输出
        set_state_var "${step}_completed" "true"
        sleep 2
    done
    
    # 生成最终报告
    echo -e "\n=== 生成项目报告 ==="
    stateful_gemini "总结整个项目生成过程，列出所有生成的组件"
}

# 使用
generate_project "MyAwesomeApp" "SaaS平台"
```

## 总结

实现 Gemini CLI 的有状态多步骤交互有多种方案：

1. **简单场景**：使用上下文注入
2. **交互场景**：使用 Expect 或 Checkpointing
3. **生产环境**：使用 API 封装
4. **持久任务**：使用会话文件

选择合适的方案，可以充分发挥 Gemini CLI 在复杂任务中的能力。