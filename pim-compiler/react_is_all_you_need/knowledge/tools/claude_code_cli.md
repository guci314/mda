# Claude Code CLI 使用指南

## 概述
Claude Code是一个强大的AI代码助手，可以帮助分析、生成、重构代码。本指南教你如何在Agent中调用Claude Code。

## 基本用法

### ⚠️ 重要提示：超时问题
`execute_command`工具默认只有10秒超时，而Claude Code通常需要更长时间。
**解决方法**：
1. 优先使用`claude_code`工具（如果可用）
2. 使用异步执行方式（见下文）
3. 创建脚本文件并后台执行

### 1. 快速问答（使用claude_code工具）
如果有`claude_code`工具，优先使用它：

```python
# 使用claude_code工具
claude_code(action="custom", custom_command='claude -p "解释Python装饰器"')

# 或者使用专门的action
claude_code(action="generate", prompt="生成斐波那契数列函数")
```

### 1.1 备选：异步执行（避免超时）
当必须使用`execute_command`时，使用异步方式：

```bash
# 后台执行，避免超时
echo "解释Python装饰器" | claude -p > /tmp/result.txt 2>&1 &
sleep 3  # 等待一会
cat /tmp/result.txt
```

### 2. 交互式会话（异步模式）⭐推荐
对于复杂任务（如分析整个代码库），使用交互式模式：

```bash
# 启动交互式会话，输出重定向到文件
claude > claude_output.log 2>&1 &

# 获取进程ID
CLAUDE_PID=$!

# 监控输出
tail -f claude_output.log

# 结束会话
kill $CLAUDE_PID
```

### 3. 分析代码库的正确方式

**不要**直接在命令行传递大量文件内容。

**正确方法**：
1. 启动claude交互式会话
2. 在会话中让claude自己读取和分析文件
3. 监控输出日志

示例：
```bash
# 创建一个分析脚本
cat > analyze_project.sh << 'EOF'
#!/bin/bash
# 启动claude并记录输出
claude > /tmp/claude_analysis.log 2>&1 << 'CLAUDE_INPUT'
请分析当前目录的代码结构：
1. 首先使用ls和find了解项目结构
2. 读取关键文件如README、package.json等
3. 分析核心模块的设计
4. 提供改进建议
CLAUDE_INPUT
EOF

# 执行分析
bash analyze_project.sh &
ANALYSIS_PID=$!

# 实时查看输出
tail -f /tmp/claude_analysis.log

# 等待完成或手动停止
wait $ANALYSIS_PID
```

## 异步监控技巧

### 1. 后台运行并监控
```bash
# 启动后台任务
nohup claude -p "分析项目并生成文档" > claude.log 2>&1 &
PID=$!

# 监控输出（非阻塞）
tail -f claude.log &

# 检查进程状态
ps -p $PID

# 等待完成
wait $PID
```

### 2. 使用命名管道（高级）
```bash
# 创建命名管道
mkfifo /tmp/claude_pipe

# 启动claude，输出到管道
claude > /tmp/claude_pipe 2>&1 &

# 另一个进程读取管道
cat /tmp/claude_pipe | while read line; do
    echo "[$(date)] $line"
    # 可以在这里添加处理逻辑
done
```

### 3. 定期检查输出文件
```bash
# 启动claude任务
claude > analysis.log 2>&1 &
CLAUDE_PID=$!

# 定期检查输出
while kill -0 $CLAUDE_PID 2>/dev/null; do
    # 获取最新的10行
    tail -10 analysis.log
    sleep 2
done

echo "Claude任务完成"
```

## 实用模式

### 模式1：快速代码生成
```bash
claude -p "生成一个REST API服务器框架，使用FastAPI"
```

### 模式2：代码审查
```bash
# 先读取文件内容
FILE_CONTENT=$(cat mycode.py)

# 然后请求审查
claude -p "请审查以下Python代码并提供改进建议：
$FILE_CONTENT"
```

### 模式3：项目级分析（推荐）
```bash
# 让claude自己探索和分析
claude << 'EOF'
我需要你分析这个项目：
1. 使用execute_command工具运行: find . -type f -name "*.py" | head -20
2. 读取关键文件了解架构
3. 分析代码质量和设计模式
4. 提供详细的分析报告
EOF
```

## Agent调用示例

当Agent需要使用Claude Code时，应该：

1. **简单任务**：直接使用execute_command
```python
execute_command(command='claude -p "解释这段代码的功能"')
```

2. **复杂任务**：创建脚本并异步执行
```python
# 创建分析脚本
write_file(file_path='analyze.sh', content='''
claude > analysis.log 2>&1 << 'EOF'
分析core目录下的所有Python文件
生成架构文档
EOF
''')

# 异步执行
execute_command(command='bash analyze.sh &')

# 监控输出
execute_command(command='tail -f analysis.log')
```

## 注意事项

1. **避免命令行参数过长**：不要在命令行直接传递大文件内容
2. **使用重定向**：将输出保存到文件便于后续分析
3. **异步执行**：对于长时间任务，使用后台执行
4. **监控进度**：通过日志文件实时了解执行状态
5. **资源管理**：记得清理临时文件和结束后台进程

## 最佳实践

1. **分析代码库**：让Claude自己读取文件，而不是传递文件内容
2. **生成文档**：使用交互式模式，让Claude逐步探索
3. **代码重构**：先分析，再生成改进方案
4. **持续监控**：使用`tail -f`实时查看输出
5. **错误处理**：检查进程退出状态和错误日志