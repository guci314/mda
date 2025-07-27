# Gemini CLI 自动化教程

## 目录
1. [简介](#简介)
2. [安装与配置](#安装与配置)
3. [基础用法](#基础用法)
4. [自动化脚本](#自动化脚本)
5. [高级工作流](#高级工作流)
6. [实战案例](#实战案例)
7. [最佳实践](#最佳实践)

## 简介

Gemini CLI 是 Google 推出的开源 AI 命令行工具，直接在终端中提供 Gemini 模型的强大功能。它特别适合自动化任务、批处理和 CI/CD 集成。

### 核心特性
- 🚀 免费使用（每天 1000 次请求）
- 💻 支持非交互式脚本执行
- 🔧 可扩展的工具系统（MCP）
- 📁 文件和图像处理能力
- 🔄 多链式提示支持

## 安装与配置

### 1. 安装 Node.js
Gemini CLI 需要 Node.js 18 或更高版本：

```bash
# 使用 nvm 安装（推荐）
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 18
nvm use 18

# 或使用系统包管理器
# Ubuntu/Debian
sudo apt update
sudo apt install nodejs npm

# macOS
brew install node
```

### 2. 安装 Gemini CLI

```bash
# 全局安装
npm install -g @google/gemini-cli

# 或使用 npx（无需安装）
npx @google/gemini-cli
```

### 3. 配置 API Key

```bash
# 设置环境变量
export GOOGLE_GENAI_API_KEY="your-api-key-here"

# 永久保存（添加到 ~/.bashrc 或 ~/.zshrc）
echo 'export GOOGLE_GENAI_API_KEY="your-api-key-here"' >> ~/.bashrc
source ~/.bashrc
```

### 4. 验证安装

```bash
# 测试 Gemini CLI
gemini "Hello, are you working?"

# 检查版本
gemini --version
```

## 基础用法

### 1. 交互模式

```bash
# 启动交互式会话
gemini

# 带检查点的交互模式（保存对话历史）
gemini -c
gemini --checkpointing
```

### 2. 单次命令

```bash
# 直接执行命令
gemini "写一个计算斐波那契数列的 Python 函数"

# 从文件读取提示
gemini < prompt.txt

# 管道输入
echo "解释这段代码" | gemini

# 处理文件内容
cat code.py | gemini "为这段代码添加注释"
```

### 3. Shell 模式

```bash
# 切换到 shell 模式
gemini
> !
# 现在可以直接执行 shell 命令
> ls -la
> !
# 退出 shell 模式
```

## 自动化脚本

### 1. 基础 Bash 脚本

```bash
#!/bin/bash
# gemini-auto.sh - Gemini CLI 自动化脚本

# 设置 API Key
export GOOGLE_GENAI_API_KEY="${GEMINI_API_KEY}"

# 函数：使用 Gemini 生成代码
generate_code() {
    local description="$1"
    local output_file="$2"
    
    gemini "生成代码：$description" > "$output_file"
    echo "代码已生成到：$output_file"
}

# 函数：代码审查
review_code() {
    local file="$1"
    
    echo "正在审查 $file..."
    cat "$file" | gemini "审查这段代码，指出潜在问题和改进建议"
}

# 函数：生成文档
generate_docs() {
    local source_dir="$1"
    local docs_file="$2"
    
    echo "# 项目文档" > "$docs_file"
    
    for file in "$source_dir"/*.py; do
        echo "## $(basename "$file")" >> "$docs_file"
        cat "$file" | gemini "为这个文件生成文档" >> "$docs_file"
        echo "" >> "$docs_file"
    done
}

# 使用示例
generate_code "一个 REST API 用户管理系统" "user_api.py"
review_code "user_api.py"
generate_docs "src" "API_DOCS.md"
```

### 2. 批量处理脚本

```bash
#!/bin/bash
# batch-process.sh - 批量处理文件

# 批量重命名图片文件
rename_images() {
    local dir="$1"
    
    for img in "$dir"/*.{jpg,png,jpeg}; do
        if [ -f "$img" ]; then
            # 使用 Gemini 分析图片内容
            new_name=$(gemini "描述这张图片的内容，用3-5个词" < "$img" | tr ' ' '_')
            ext="${img##*.}"
            mv "$img" "$dir/${new_name}.${ext}"
            echo "重命名：$img -> ${new_name}.${ext}"
        fi
    done
}

# 批量生成测试用例
generate_tests() {
    local src_dir="$1"
    local test_dir="$2"
    
    mkdir -p "$test_dir"
    
    for src_file in "$src_dir"/*.py; do
        if [ -f "$src_file" ]; then
            base_name=$(basename "$src_file" .py)
            test_file="$test_dir/test_${base_name}.py"
            
            cat "$src_file" | gemini "为这个 Python 文件生成完整的单元测试" > "$test_file"
            echo "生成测试：$test_file"
        fi
    done
}
```

### 3. Git 工作流自动化

```bash
#!/bin/bash
# git-workflow.sh - Git 工作流自动化

# 生成提交信息
generate_commit_message() {
    local staged_diff=$(git diff --cached)
    
    if [ -z "$staged_diff" ]; then
        echo "没有暂存的更改"
        return 1
    fi
    
    echo "$staged_diff" | gemini "基于这些代码更改生成一个简洁的提交信息（中文）"
}

# 生成 PR 描述
generate_pr_description() {
    local base_branch="${1:-main}"
    local commits=$(git log --oneline "$base_branch"..HEAD)
    local diff=$(git diff "$base_branch"...HEAD)
    
    echo "提交历史：
$commits

代码更改：
$diff" | gemini "基于这些信息生成一个详细的 Pull Request 描述，包括：
- 更改摘要
- 主要改动
- 测试情况
- 注意事项"
}

# 每日站会总结
daily_standup() {
    local yesterday=$(date -d "yesterday" +%Y-%m-%d)
    local commits=$(git log --since="$yesterday" --author="$(git config user.email)" --oneline)
    
    echo "昨天的提交：
$commits" | gemini "基于这些提交生成站会汇报：
- 昨天完成了什么
- 今天计划做什么
- 有什么阻碍"
}
```

## 高级工作流

### 1. 多链式提示（MCP）

```bash
#!/bin/bash
# multi-chain.sh - 多链式任务

# 创建完整的微服务
create_microservice() {
    local service_name="$1"
    
    # 使用 MCP 命令执行多步骤任务
    gemini "/mcp 创建一个名为 $service_name 的微服务：
    1. 生成项目结构
    2. 创建 Dockerfile
    3. 编写 API 代码
    4. 生成测试文件
    5. 创建 CI/CD 配置
    6. 生成 README 文档"
}
```

### 2. JSON 配置的自动化

```json
// prompts/code-review.json
{
  "name": "code-review",
  "description": "自动代码审查",
  "prompts": [
    {
      "id": "security-check",
      "template": "检查以下代码的安全问题：\n{code}"
    },
    {
      "id": "performance-check",
      "template": "分析以下代码的性能问题：\n{code}"
    },
    {
      "id": "best-practices",
      "template": "这段代码是否遵循最佳实践：\n{code}"
    }
  ]
}
```

使用 JSON 配置：

```bash
#!/bin/bash
# json-workflow.sh

run_code_review() {
    local file="$1"
    local code=$(cat "$file")
    
    # 安全检查
    jq -r '.prompts[0].template' prompts/code-review.json | 
    sed "s/{code}/$code/g" | 
    gemini
    
    # 性能检查
    jq -r '.prompts[1].template' prompts/code-review.json | 
    sed "s/{code}/$code/g" | 
    gemini
}
```

### 3. CI/CD 集成

```yaml
# .github/workflows/gemini-automation.yml
name: Gemini CLI Automation

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  code-review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install Gemini CLI
        run: npm install -g @google/gemini-cli
      
      - name: Code Review
        env:
          GOOGLE_GENAI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
        run: |
          # 获取 PR 的更改
          git diff origin/main...HEAD > changes.diff
          
          # 使用 Gemini 审查代码
          cat changes.diff | gemini "审查这些代码更改，关注：
          1. 潜在的 bug
          2. 性能问题
          3. 安全隐患
          4. 代码风格" > review.md
          
          # 将审查结果作为 PR 评论
          gh pr comment --body-file review.md
```

## 实战案例

### 案例1：自动化 API 文档生成

```bash
#!/bin/bash
# api-doc-generator.sh

generate_api_docs() {
    local project_dir="$1"
    local output_file="docs/API.md"
    
    # 创建文档目录
    mkdir -p docs
    
    # 生成文档头部
    echo "# API 文档
生成时间：$(date)

" > "$output_file"
    
    # 分析路由文件
    for route_file in "$project_dir"/routes/*.js; do
        if [ -f "$route_file" ]; then
            echo "## $(basename "$route_file" .js)" >> "$output_file"
            
            # 提取路由信息并生成文档
            cat "$route_file" | gemini "分析这个路由文件，生成 API 文档，包括：
            - 端点列表
            - 请求方法
            - 参数说明
            - 响应格式
            - 示例请求
            使用 Markdown 格式" >> "$output_file"
            
            echo -e "\n---\n" >> "$output_file"
        fi
    done
    
    # 生成 Postman 集合
    cat "$output_file" | gemini "基于这个 API 文档生成 Postman collection JSON" > docs/postman_collection.json
}

# 执行
generate_api_docs "src"
```

### 案例2：智能日志分析

```bash
#!/bin/bash
# log-analyzer.sh

analyze_logs() {
    local log_file="$1"
    local report_file="reports/log_analysis_$(date +%Y%m%d).md"
    
    mkdir -p reports
    
    # 提取错误日志
    grep -i "error\|exception" "$log_file" > temp_errors.log
    
    # 分析错误模式
    cat temp_errors.log | gemini "分析这些错误日志：
    1. 识别错误模式
    2. 统计错误频率
    3. 找出根本原因
    4. 提供解决建议
    生成详细的分析报告" > "$report_file"
    
    # 生成可视化数据
    cat temp_errors.log | gemini "基于这些错误生成 Chart.js 配置，用于可视化：
    - 错误类型分布
    - 时间趋势
    - 严重程度分布" > reports/chart_config.json
    
    rm temp_errors.log
}

# 每日定时执行
# crontab -e
# 0 2 * * * /path/to/log-analyzer.sh /var/log/app.log
```

### 案例3：代码迁移助手

```bash
#!/bin/bash
# migration-helper.sh

migrate_code() {
    local source_dir="$1"
    local target_framework="$2"
    local output_dir="migrated_$target_framework"
    
    mkdir -p "$output_dir"
    
    # 分析项目结构
    project_structure=$(find "$source_dir" -name "*.py" -o -name "*.js" | head -20)
    
    # 生成迁移计划
    echo "$project_structure" | gemini "分析这个项目结构，生成从当前框架迁移到 $target_framework 的详细计划" > migration_plan.md
    
    # 逐文件迁移
    find "$source_dir" -name "*.py" | while read -r file; do
        relative_path="${file#$source_dir/}"
        output_file="$output_dir/$relative_path"
        mkdir -p "$(dirname "$output_file")"
        
        cat "$file" | gemini "将这个文件从当前框架迁移到 $target_framework，保持功能不变" > "$output_file"
        echo "已迁移：$file -> $output_file"
    done
    
    # 生成新的配置文件
    gemini "为 $target_framework 项目生成必要的配置文件（如 package.json, requirements.txt 等）" > "$output_dir/setup_files.sh"
    
    # 执行配置
    cd "$output_dir" && bash setup_files.sh
}

# 使用示例：将 Flask 项目迁移到 FastAPI
migrate_code "flask_project" "FastAPI"
```

## 最佳实践

### 1. 错误处理

```bash
#!/bin/bash
# 带错误处理的 Gemini CLI 脚本

safe_gemini() {
    local prompt="$1"
    local max_retries=3
    local retry_count=0
    
    while [ $retry_count -lt $max_retries ]; do
        if output=$(gemini "$prompt" 2>&1); then
            echo "$output"
            return 0
        else
            echo "错误：Gemini 调用失败（尝试 $((retry_count + 1))/$max_retries）" >&2
            ((retry_count++))
            sleep 2
        fi
    done
    
    return 1
}
```

### 2. 性能优化

```bash
# 并行处理多个文件
process_files_parallel() {
    local dir="$1"
    local max_jobs=5
    
    find "$dir" -name "*.py" | xargs -P "$max_jobs" -I {} bash -c '
        file="{}"
        output="${file%.py}_analyzed.md"
        cat "$file" | gemini "分析这个 Python 文件" > "$output"
        echo "处理完成：$file"
    '
}
```

### 3. 配置管理

```bash
# .gemini/settings.json
{
  "model": "gemini-2.5-pro",
  "temperature": 0.1,
  "maxTokens": 8192,
  "timeout": 120000,
  "checkpointing": true,
  "tools": {
    "enabled": true,
    "allowedTools": ["file_read", "file_write", "web_search"]
  }
}
```

### 4. 安全考虑

```bash
#!/bin/bash
# 安全的 Gemini CLI 使用

# 不要在脚本中硬编码 API Key
if [ -z "$GOOGLE_GENAI_API_KEY" ]; then
    echo "错误：请设置 GOOGLE_GENAI_API_KEY 环境变量"
    exit 1
fi

# 限制输入大小
limit_input() {
    local input="$1"
    local max_size=10000
    
    if [ ${#input} -gt $max_size ]; then
        echo "${input:0:$max_size}... (已截断)"
    else
        echo "$input"
    fi
}

# 清理敏感信息
sanitize_output() {
    local output="$1"
    
    # 移除可能的密钥、密码等
    echo "$output" | sed -E 's/(api[_-]?key|password|secret)[ ]*[:=][ ]*[^ ]+/\1=***REDACTED***/gi'
}
```

## 总结

Gemini CLI 提供了强大的自动化能力：

1. **简单易用**：一行命令即可调用 AI
2. **灵活集成**：支持各种脚本和工作流
3. **功能丰富**：从代码生成到文档编写
4. **免费配额**：每天 1000 次请求足够日常使用

通过本教程的脚本和案例，你可以：
- 自动化日常开发任务
- 构建智能 CI/CD 流程
- 批量处理文件和代码
- 创建自定义 AI 工具链

开始使用 Gemini CLI，让 AI 成为你的命令行助手！