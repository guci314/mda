#!/bin/bash
# gemini-interactive-demo.sh - 使用命名管道实现 Gemini CLI 交互式会话

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 配置
PIPE_NAME="/tmp/gemini_pipe_$$"
OUTPUT_FILE="gemini_output_$(date +%Y%m%d_%H%M%S).log"
GEMINI_PID=""

# 清理函数
cleanup() {
    echo -e "\n${YELLOW}正在清理...${NC}"
    if [ -n "$GEMINI_PID" ]; then
        kill $GEMINI_PID 2>/dev/null
    fi
    rm -f "$PIPE_NAME"
    echo -e "${GREEN}清理完成！${NC}"
}

# 设置退出时清理
trap cleanup EXIT INT TERM

# 打印标题
print_header() {
    echo -e "${BLUE}================================================${NC}"
    echo -e "${BLUE}       Gemini CLI 交互式会话演示${NC}"
    echo -e "${BLUE}================================================${NC}"
    echo
}

# 创建命名管道
create_pipe() {
    echo -e "${YELLOW}创建命名管道: $PIPE_NAME${NC}"
    mkfifo "$PIPE_NAME"
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ 管道创建成功${NC}"
    else
        echo -e "${RED}✗ 管道创建失败${NC}"
        exit 1
    fi
}

# 启动 Gemini CLI
start_gemini() {
    echo -e "\n${YELLOW}启动 Gemini CLI (带检查点)...${NC}"
    
    # 启动 Gemini 并将输出保存到文件
    gemini -c < "$PIPE_NAME" > "$OUTPUT_FILE" 2>&1 &
    GEMINI_PID=$!
    
    # 检查是否启动成功
    sleep 2
    if kill -0 $GEMINI_PID 2>/dev/null; then
        echo -e "${GREEN}✓ Gemini CLI 启动成功 (PID: $GEMINI_PID)${NC}"
        echo -e "${GREEN}✓ 输出保存到: $OUTPUT_FILE${NC}"
    else
        echo -e "${RED}✗ Gemini CLI 启动失败${NC}"
        exit 1
    fi
}

# 发送命令到 Gemini
send_to_gemini() {
    local command="$1"
    local step_name="$2"
    
    echo -e "\n${BLUE}=== $step_name ===${NC}"
    echo -e "${YELLOW}发送: ${NC}$command"
    echo "$command" > "$PIPE_NAME"
    
    # 等待响应并显示部分输出
    sleep 3
    echo -e "${GREEN}响应预览:${NC}"
    tail -n 20 "$OUTPUT_FILE" | grep -v "^>" | tail -n 10
}

# 显示输出文件的特定部分
show_output_section() {
    local start_pattern="$1"
    local end_pattern="$2"
    local section_name="$3"
    
    echo -e "\n${BLUE}=== $section_name ===${NC}"
    sed -n "/$start_pattern/,/$end_pattern/p" "$OUTPUT_FILE" | head -n 50
}

# 主程序
main() {
    print_header
    
    # 检查 API Key
    if [ -z "$GOOGLE_GENAI_API_KEY" ]; then
        echo -e "${RED}错误: 请设置 GOOGLE_GENAI_API_KEY 环境变量${NC}"
        exit 1
    fi
    
    # 创建管道并启动 Gemini
    create_pipe
    start_gemini
    
    echo -e "\n${BLUE}开始多步骤交互演示...${NC}"
    
    # 步骤1: 创建数据模型
    send_to_gemini \
        "创建一个博客系统的数据模型，包括：用户(User)、文章(Post)、评论(Comment)、标签(Tag)。请详细说明每个实体的属性和关系。" \
        "步骤1: 创建数据模型"
    
    # 等待更长时间以确保响应完整
    sleep 5
    
    # 步骤2: 生成数据库 Schema
    send_to_gemini \
        "基于上面设计的博客系统数据模型，生成对应的 PostgreSQL 数据库建表语句。包括主键、外键、索引和约束。" \
        "步骤2: 生成数据库 Schema"
    
    sleep 5
    
    # 步骤3: 生成 ORM 代码
    send_to_gemini \
        "将上面的数据库表结构转换为 SQLAlchemy ORM 模型代码。使用 Python 3.8+ 的类型注解。" \
        "步骤3: 生成 SQLAlchemy ORM 模型"
    
    sleep 5
    
    # 步骤4: 生成 API 接口
    send_to_gemini \
        "基于前面的 ORM 模型，设计 RESTful API 接口。为每个实体生成 CRUD 操作的端点设计，包括路径、方法和参数。" \
        "步骤4: 设计 RESTful API"
    
    sleep 5
    
    # 步骤5: 生成 FastAPI 实现
    send_to_gemini \
        "基于上面的 API 设计，生成完整的 FastAPI 实现代码。包括路由、请求/响应模型和基本的错误处理。" \
        "步骤5: 生成 FastAPI 实现"
    
    sleep 5
    
    # 步骤6: 生成测试代码
    send_to_gemini \
        "为上面的 FastAPI 代码生成 pytest 测试用例。包括单元测试和集成测试，覆盖主要的 CRUD 操作。" \
        "步骤6: 生成测试代码"
    
    sleep 5
    
    # 步骤7: 生成文档
    send_to_gemini \
        "基于我们刚才完成的所有工作，生成一个完整的项目 README.md 文档。包括项目介绍、技术栈、安装说明、API 文档和开发指南。" \
        "步骤7: 生成项目文档"
    
    sleep 5
    
    # 步骤8: 总结
    send_to_gemini \
        "总结我们刚才完成的博客系统开发过程，列出所有生成的组件，并提供下一步的改进建议。" \
        "步骤8: 项目总结"
    
    sleep 5
    
    echo -e "\n${GREEN}所有步骤执行完成！${NC}"
    echo -e "${YELLOW}完整输出保存在: $OUTPUT_FILE${NC}"
    
    # 询问是否查看完整输出
    echo -e "\n${BLUE}是否查看完整输出？(y/n)${NC}"
    read -r response
    if [[ "$response" == "y" ]]; then
        less "$OUTPUT_FILE"
    fi
    
    # 提取并保存各个步骤的输出
    extract_outputs
}

# 提取各步骤输出到单独文件
extract_outputs() {
    echo -e "\n${YELLOW}提取各步骤输出...${NC}"
    
    local output_dir="gemini_outputs_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$output_dir"
    
    # 使用 awk 分割输出
    awk '
    /步骤1:/ {out="'$output_dir'/01_data_model.md"}
    /步骤2:/ {out="'$output_dir'/02_database_schema.sql"}
    /步骤3:/ {out="'$output_dir'/03_orm_models.py"}
    /步骤4:/ {out="'$output_dir'/04_api_design.md"}
    /步骤5:/ {out="'$output_dir'/05_fastapi_code.py"}
    /步骤6:/ {out="'$output_dir'/06_test_code.py"}
    /步骤7:/ {out="'$output_dir'/07_readme.md"}
    /步骤8:/ {out="'$output_dir'/08_summary.md"}
    out && /^>/ {out=""}
    out {print >> out}
    ' "$OUTPUT_FILE"
    
    echo -e "${GREEN}✓ 输出已提取到目录: $output_dir${NC}"
    ls -la "$output_dir"
}

# 执行主程序
main