#!/bin/bash
# PIM Engine 启动脚本

# 设置 PIM_HOME（如果未设置）
if [ -z "$PIM_HOME" ]; then
    # 获取脚本所在目录的父目录
    SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
    export PIM_HOME="$(dirname "$SCRIPT_DIR")"
fi

# 设置默认 classpath
if [ -z "$PIM_CLASSPATH" ]; then
    export PIM_CLASSPATH="$PIM_HOME/classpath/models:$PIM_HOME/classpath/lib:$PIM_HOME/classpath/plugins"
fi

# 配置文件路径
CONFIG_DIR="$PIM_HOME/config"
ENGINE_CONFIG="$CONFIG_DIR/engine.yml"
CLASSPATH_CONFIG="$CONFIG_DIR/classpath.yml"

# 日志目录
LOG_DIR="$PIM_HOME/runtime/logs"
mkdir -p "$LOG_DIR"

# PID 文件
PID_FILE="$PIM_HOME/runtime/pim-engine.pid"

# Python 环境
PYTHON="${PYTHON:-python3}"
VENV_DIR="$PIM_HOME/venv"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 打印消息
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# 检查环境
check_environment() {
    log_info "Checking environment..."
    
    # 检查 Python
    if ! command -v $PYTHON &> /dev/null; then
        log_error "Python 3 not found. Please install Python 3.8+"
        exit 1
    fi
    
    # 检查配置文件
    if [ ! -f "$ENGINE_CONFIG" ]; then
        if [ -f "$ENGINE_CONFIG.example" ]; then
            log_warn "Engine config not found. Copying from example..."
            cp "$ENGINE_CONFIG.example" "$ENGINE_CONFIG"
        else
            log_error "Engine config not found: $ENGINE_CONFIG"
            exit 1
        fi
    fi
    
    if [ ! -f "$CLASSPATH_CONFIG" ]; then
        if [ -f "$CLASSPATH_CONFIG.example" ]; then
            log_warn "Classpath config not found. Copying from example..."
            cp "$CLASSPATH_CONFIG.example" "$CLASSPATH_CONFIG"
        else
            log_error "Classpath config not found: $CLASSPATH_CONFIG"
            exit 1
        fi
    fi
    
    # 创建必要的目录
    mkdir -p "$PIM_HOME/classpath/models"
    mkdir -p "$PIM_HOME/classpath/lib"
    mkdir -p "$PIM_HOME/classpath/plugins"
    mkdir -p "$PIM_HOME/runtime/db"
    mkdir -p "$PIM_HOME/runtime/cache"
    
    log_info "Environment check completed"
}

# 显示 classpath 信息
show_classpath() {
    log_info "PIM Classpath Configuration:"
    echo "  PIM_HOME: $PIM_HOME"
    echo "  PIM_CLASSPATH: $PIM_CLASSPATH"
    echo ""
    echo "  Model directories:"
    for path in ${PIM_CLASSPATH//:/ }; do
        if [[ $path == */models* ]]; then
            echo "    - $path"
            if [ -d "$path" ]; then
                count=$(find "$path" -name "*.psm" 2>/dev/null | wc -l)
                echo "      (contains $count PSM files)"
            fi
        fi
    done
}

# 启动引擎
start_engine() {
    check_environment
    
    # 检查是否已经运行
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p $PID > /dev/null 2>&1; then
            log_error "PIM Engine is already running (PID: $PID)"
            exit 1
        else
            rm -f "$PID_FILE"
        fi
    fi
    
    log_info "Starting PIM Engine..."
    show_classpath
    
    # 激活虚拟环境（如果存在）
    if [ -d "$VENV_DIR" ]; then
        source "$VENV_DIR/bin/activate"
    fi
    
    # 设置 PYTHONPATH
    export PYTHONPATH="$PIM_HOME/src:$PYTHONPATH"
    
    # 启动引擎
    nohup $PYTHON -m pim_engine.main \
        --config="$ENGINE_CONFIG" \
        --classpath-config="$CLASSPATH_CONFIG" \
        >> "$LOG_DIR/pim-engine.log" 2>&1 &
    
    PID=$!
    echo $PID > "$PID_FILE"
    
    # 等待启动
    sleep 2
    
    if ps -p $PID > /dev/null 2>&1; then
        log_info "PIM Engine started successfully (PID: $PID)"
        log_info "API available at: http://localhost:8001"
        log_info "Documentation at: http://localhost:8001/docs"
    else
        log_error "Failed to start PIM Engine"
        rm -f "$PID_FILE"
        exit 1
    fi
}

# 停止引擎
stop_engine() {
    if [ ! -f "$PID_FILE" ]; then
        log_error "PIM Engine is not running"
        exit 1
    fi
    
    PID=$(cat "$PID_FILE")
    
    if ps -p $PID > /dev/null 2>&1; then
        log_info "Stopping PIM Engine (PID: $PID)..."
        kill -TERM $PID
        
        # 等待进程结束
        for i in {1..10}; do
            if ! ps -p $PID > /dev/null 2>&1; then
                break
            fi
            sleep 1
        done
        
        # 如果还在运行，强制结束
        if ps -p $PID > /dev/null 2>&1; then
            log_warn "Force stopping PIM Engine..."
            kill -KILL $PID
        fi
        
        rm -f "$PID_FILE"
        log_info "PIM Engine stopped"
    else
        log_error "PIM Engine process not found"
        rm -f "$PID_FILE"
    fi
}

# 查看状态
status_engine() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p $PID > /dev/null 2>&1; then
            log_info "PIM Engine is running (PID: $PID)"
            
            # 调用 API 获取详细状态
            if command -v curl &> /dev/null; then
                echo ""
                log_info "Engine Status:"
                curl -s http://localhost:8001/engine/status 2>/dev/null | jq . 2>/dev/null || echo "  (Unable to fetch status)"
            fi
        else
            log_error "PIM Engine is not running (stale PID file)"
            rm -f "$PID_FILE"
        fi
    else
        log_error "PIM Engine is not running"
    fi
}

# 列出已加载的模型
list_models() {
    if command -v curl &> /dev/null; then
        log_info "Loaded models:"
        curl -s http://localhost:8001/engine/models 2>/dev/null | jq -r '.models[] | "  - \(.module) (v\(.version))"' 2>/dev/null || echo "  (Unable to fetch model list)"
    else
        log_error "curl not found. Cannot fetch model list."
    fi
}

# 重新加载模型
reload_model() {
    MODEL=$1
    if [ -z "$MODEL" ]; then
        log_error "Usage: $0 reload <model_name>"
        exit 1
    fi
    
    log_info "Reloading model: $MODEL"
    curl -X POST "http://localhost:8001/engine/models/reload?model_name=$MODEL" 2>/dev/null
}

# 添加 classpath
add_classpath() {
    PATH_TO_ADD=$1
    if [ -z "$PATH_TO_ADD" ]; then
        log_error "Usage: $0 classpath add <path>"
        exit 1
    fi
    
    # 转换为绝对路径
    ABS_PATH=$(readlink -f "$PATH_TO_ADD")
    
    log_info "Adding classpath: $ABS_PATH"
    curl -X POST "http://localhost:8001/engine/classpath/add" \
        -H "Content-Type: application/json" \
        -d "{\"path\": \"$ABS_PATH\"}" 2>/dev/null
}

# 主函数
case "$1" in
    start)
        start_engine
        ;;
    stop)
        stop_engine
        ;;
    restart)
        stop_engine
        sleep 2
        start_engine
        ;;
    status)
        status_engine
        ;;
    list)
        list_models
        ;;
    reload)
        reload_model "$2"
        ;;
    classpath)
        case "$2" in
            show)
                show_classpath
                ;;
            add)
                add_classpath "$3"
                ;;
            *)
                log_error "Usage: $0 classpath {show|add <path>}"
                exit 1
                ;;
        esac
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|list|reload <model>|classpath {show|add <path>}}"
        exit 1
        ;;
esac

exit 0