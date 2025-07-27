#!/bin/bash
# advanced-gemini-interactive.sh - 高级交互式 Gemini CLI 会话管理

# ==================== 配置部分 ====================

# 颜色定义
declare -A COLORS=(
    [RED]='\033[0;31m'
    [GREEN]='\033[0;32m'
    [BLUE]='\033[0;34m'
    [YELLOW]='\033[1;33m'
    [PURPLE]='\033[0;35m'
    [CYAN]='\033[0;36m'
    [NC]='\033[0m'
)

# 全局变量
SESSION_NAME="${1:-default_session}"
SESSION_DIR="./gemini_sessions/$SESSION_NAME"
PIPE_IN="$SESSION_DIR/pipe_in"
PIPE_OUT="$SESSION_DIR/pipe_out"
PID_FILE="$SESSION_DIR/gemini.pid"
LOG_FILE="$SESSION_DIR/session.log"
STATE_FILE="$SESSION_DIR/state.json"
HISTORY_FILE="$SESSION_DIR/history.json"

# ==================== 工具函数 ====================

# 彩色输出
cecho() {
    local color=$1
    shift
    echo -e "${COLORS[$color]}$*${COLORS[NC]}"
}

# 错误处理
error_exit() {
    cecho RED "错误: $1"
    exit 1
}

# 创建会话目录
setup_session() {
    cecho YELLOW "设置会话: $SESSION_NAME"
    mkdir -p "$SESSION_DIR"
    
    # 初始化状态文件
    if [ ! -f "$STATE_FILE" ]; then
        cat > "$STATE_FILE" << EOF
{
    "session_name": "$SESSION_NAME",
    "created_at": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
    "step_count": 0,
    "context": {},
    "status": "active"
}
EOF
    fi
    
    # 初始化历史文件
    if [ ! -f "$HISTORY_FILE" ]; then
        echo "[]" > "$HISTORY_FILE"
    fi
}

# 创建命名管道
create_pipes() {
    cecho YELLOW "创建通信管道..."
    
    # 清理旧管道
    rm -f "$PIPE_IN" "$PIPE_OUT"
    
    # 创建新管道
    mkfifo "$PIPE_IN" || error_exit "无法创建输入管道"
    mkfifo "$PIPE_OUT" || error_exit "无法创建输出管道"
    
    cecho GREEN "✓ 管道创建成功"
}

# 启动 Gemini CLI
start_gemini_session() {
    cecho YELLOW "启动 Gemini CLI 会话..."
    
    # 检查 API Key
    [ -z "$GOOGLE_GENAI_API_KEY" ] && error_exit "请设置 GOOGLE_GENAI_API_KEY"
    
    # 启动 Gemini CLI，同时捕获输出
    (
        gemini -c < "$PIPE_IN" 2>&1 | while IFS= read -r line; do
            echo "$line" >> "$LOG_FILE"
            echo "$line" > "$PIPE_OUT"
        done
    ) &
    
    local gemini_pid=$!
    echo $gemini_pid > "$PID_FILE"
    
    # 等待启动
    sleep 2
    
    if kill -0 $gemini_pid 2>/dev/null; then
        cecho GREEN "✓ Gemini CLI 启动成功 (PID: $gemini_pid)"
    else
        error_exit "Gemini CLI 启动失败"
    fi
}

# 发送命令并等待响应
send_command() {
    local command="$1"
    local timeout="${2:-30}"
    
    # 更新步骤计数
    local step_count=$(jq -r '.step_count' "$STATE_FILE")
    ((step_count++))
    jq ".step_count = $step_count" "$STATE_FILE" > "$STATE_FILE.tmp" && mv "$STATE_FILE.tmp" "$STATE_FILE"
    
    # 记录到历史
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    jq ". += [{\"step\": $step_count, \"timestamp\": \"$timestamp\", \"role\": \"user\", \"content\": \"$command\"}]" \
        "$HISTORY_FILE" > "$HISTORY_FILE.tmp" && mv "$HISTORY_FILE.tmp" "$HISTORY_FILE"
    
    # 发送命令
    echo "$command" > "$PIPE_IN"
    
    # 收集响应
    local response=""
    local start_time=$(date +%s)
    
    while true; do
        if read -t 1 line < "$PIPE_OUT"; then
            response="${response}${line}\n"
            
            # 检查是否是提示符
            if [[ "$line" == ">" ]]; then
                break
            fi
        fi
        
        # 超时检查
        local current_time=$(date +%s)
        if [ $((current_time - start_time)) -gt $timeout ]; then
            cecho RED "响应超时"
            break
        fi
    done
    
    # 记录响应到历史
    jq ". += [{\"step\": $step_count, \"timestamp\": \"$(date -u +"%Y-%m-%dT%H:%M:%SZ")\", \"role\": \"assistant\", \"content\": \"$response\"}]" \
        "$HISTORY_FILE" > "$HISTORY_FILE.tmp" && mv "$HISTORY_FILE.tmp" "$HISTORY_FILE"
    
    echo -e "$response"
}

# 获取会话状态
get_session_state() {
    local key="$1"
    jq -r ".context.$key // \"\"" "$STATE_FILE"
}

# 设置会话状态
set_session_state() {
    local key="$1"
    local value="$2"
    jq ".context.\"$key\" = \"$value\"" "$STATE_FILE" > "$STATE_FILE.tmp" && \
        mv "$STATE_FILE.tmp" "$STATE_FILE"
}

# 执行工作流步骤
execute_workflow_step() {
    local step_name="$1"
    local prompt="$2"
    local save_key="${3:-}"
    
    cecho BLUE "\n=== $step_name ==="
    cecho CYAN "提示: $prompt"
    
    local response=$(send_command "$prompt")
    
    # 保存到状态
    if [ -n "$save_key" ]; then
        set_session_state "$save_key" "$response"
    fi
    
    # 显示响应摘要
    local preview=$(echo -e "$response" | head -n 10)
    cecho GREEN "响应预览:"
    echo "$preview"
    
    if [ $(echo -e "$response" | wc -l) -gt 10 ]; then
        cecho YELLOW "... (更多内容已保存)"
    fi
    
    # 保存完整响应到文件
    local step_file="$SESSION_DIR/step_${step_name// /_}.txt"
    echo -e "$response" > "$step_file"
    cecho GREEN "✓ 完整响应已保存到: $step_file"
}

# 生成会话报告
generate_session_report() {
    local report_file="$SESSION_DIR/session_report.md"
    
    cecho YELLOW "\n生成会话报告..."
    
    cat > "$report_file" << EOF
# Gemini CLI 会话报告

**会话名称**: $SESSION_NAME  
**生成时间**: $(date)

## 会话信息

$(jq -r '. | "- 创建时间: \(.created_at)\n- 步骤总数: \(.step_count)\n- 状态: \(.status)"' "$STATE_FILE")

## 执行历史

\`\`\`json
$(jq '.' "$HISTORY_FILE")
\`\`\`

## 生成的文件

$(ls -la "$SESSION_DIR"/step_*.txt 2>/dev/null | awk '{print "- " $9}')

## 会话日志摘要

\`\`\`
$(tail -n 50 "$LOG_FILE")
\`\`\`
EOF

    cecho GREEN "✓ 报告已生成: $report_file"
}

# 清理函数
cleanup() {
    cecho YELLOW "\n清理会话..."
    
    # 终止 Gemini 进程
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if kill -0 $pid 2>/dev/null; then
            kill $pid
            cecho GREEN "✓ Gemini 进程已终止"
        fi
        rm -f "$PID_FILE"
    fi
    
    # 清理管道
    rm -f "$PIPE_IN" "$PIPE_OUT"
    
    # 更新状态
    if [ -f "$STATE_FILE" ]; then
        jq '.status = "completed"' "$STATE_FILE" > "$STATE_FILE.tmp" && \
            mv "$STATE_FILE.tmp" "$STATE_FILE"
    fi
    
    cecho GREEN "✓ 清理完成"
}

# ==================== 主程序 ====================

main() {
    # 设置清理钩子
    trap cleanup EXIT INT TERM
    
    cecho PURPLE "╔════════════════════════════════════════╗"
    cecho PURPLE "║   高级 Gemini CLI 交互式会话管理器    ║"
    cecho PURPLE "╚════════════════════════════════════════╝"
    
    # 初始化会话
    setup_session
    create_pipes
    start_gemini_session
    
    # 选择工作流
    cecho CYAN "\n选择要执行的工作流:"
    echo "1. 完整应用开发流程"
    echo "2. API 设计流程"
    echo "3. 数据库设计流程"
    echo "4. 自定义交互"
    
    read -p "请选择 (1-4): " choice
    
    case $choice in
        1) workflow_full_app ;;
        2) workflow_api_design ;;
        3) workflow_database_design ;;
        4) workflow_custom ;;
        *) error_exit "无效选择" ;;
    esac
    
    # 生成报告
    generate_session_report
    
    cecho GREEN "\n✅ 会话完成！"
    cecho CYAN "会话文件保存在: $SESSION_DIR"
}

# ==================== 工作流定义 ====================

# 完整应用开发流程
workflow_full_app() {
    cecho PURPLE "\n开始完整应用开发流程..."
    
    execute_workflow_step "需求分析" \
        "设计一个任务管理应用的需求文档，包括：用户故事、功能需求、非功能需求" \
        "requirements"
    
    execute_workflow_step "架构设计" \
        "基于上述需求，设计系统架构，包括：技术栈选择、系统组件、部署架构" \
        "architecture"
    
    execute_workflow_step "数据模型" \
        "设计任务管理系统的数据模型，包括所有实体、属性和关系" \
        "data_model"
    
    execute_workflow_step "API设计" \
        "基于数据模型，设计 RESTful API，包括所有端点、请求/响应格式" \
        "api_design"
    
    execute_workflow_step "代码生成" \
        "基于 API 设计，生成 FastAPI 实现代码" \
        "backend_code"
    
    execute_workflow_step "前端设计" \
        "设计 React 前端组件结构和状态管理方案" \
        "frontend_design"
    
    execute_workflow_step "测试策略" \
        "制定完整的测试策略，包括单元测试、集成测试和端到端测试" \
        "test_strategy"
    
    execute_workflow_step "部署方案" \
        "设计 Docker 容器化和 Kubernetes 部署方案" \
        "deployment"
}

# API 设计流程
workflow_api_design() {
    cecho PURPLE "\n开始 API 设计流程..."
    
    execute_workflow_step "业务分析" \
        "分析一个电商平台的核心业务流程" \
        "business_analysis"
    
    execute_workflow_step "资源识别" \
        "基于业务流程，识别所有 REST 资源" \
        "resources"
    
    execute_workflow_step "端点设计" \
        "为每个资源设计 CRUD 端点和业务端点" \
        "endpoints"
    
    execute_workflow_step "数据格式" \
        "设计请求和响应的 JSON Schema" \
        "schemas"
    
    execute_workflow_step "OpenAPI规范" \
        "生成完整的 OpenAPI 3.0 规范文档" \
        "openapi"
}

# 数据库设计流程
workflow_database_design() {
    cecho PURPLE "\n开始数据库设计流程..."
    
    execute_workflow_step "概念模型" \
        "设计一个内容管理系统的概念数据模型" \
        "conceptual"
    
    execute_workflow_step "逻辑模型" \
        "将概念模型转换为逻辑模型，进行规范化" \
        "logical"
    
    execute_workflow_step "物理模型" \
        "生成 PostgreSQL 的物理模型，包括索引和约束" \
        "physical"
    
    execute_workflow_step "优化建议" \
        "提供查询优化和索引优化建议" \
        "optimization"
}

# 自定义交互
workflow_custom() {
    cecho PURPLE "\n进入自定义交互模式..."
    cecho YELLOW "输入 'exit' 退出交互"
    
    while true; do
        echo -n -e "${COLORS[CYAN]}> ${COLORS[NC]}"
        read -r user_input
        
        [ "$user_input" = "exit" ] && break
        
        response=$(send_command "$user_input")
        cecho GREEN "$response"
    done
}

# ==================== 程序入口 ====================

# 检查是否作为脚本运行
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi