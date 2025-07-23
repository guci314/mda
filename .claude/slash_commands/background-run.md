# Background Run Command

## 使用方法
使用 `/background-run` 或 `/bg` 来后台运行长时间任务并监控日志。

## 命令格式
```
/background-run <command> [wait_time] [check_pattern]
/bg <command> [wait_time] [check_pattern]
```

## 参数说明
- `<command>`: 要执行的命令（必需）
- `[wait_time]`: 等待时间（秒），默认 30 秒
- `[check_pattern]`: 检查日志的模式，默认检查最后 50 行

## 工作流程

### 1. 启动后台任务
```bash
# 生成唯一的日志文件名
LOG_FILE="${COMMAND_NAME}_$(date +%Y%m%d_%H%M%S).log"

# 使用 nohup 后台运行命令
nohup $COMMAND > $LOG_FILE 2>&1 &

# 记录进程 ID
echo $! > ${LOG_FILE}.pid
```

### 2. 监控进度
```bash
# 等待指定时间
sleep $WAIT_TIME

# 检查进程是否还在运行
if ps -p $(cat ${LOG_FILE}.pid) > /dev/null; then
    echo "任务仍在运行..."
else
    echo "任务已完成"
fi

# 查看日志最后 N 行
tail -n $CHECK_LINES $LOG_FILE
```

### 3. 检查特定模式
```bash
# 检查错误
grep -i "error\|failed\|exception" $LOG_FILE | tail -20

# 检查成功标志
grep -i "success\|completed\|passed" $LOG_FILE | tail -20

# 检查进度
grep -i "progress\|processing\|generated" $LOG_FILE | tail -20
```

### 4. 决策点
- 如果发现错误：分析错误并决定是否需要干预
- 如果任务完成：检查结果并进行下一步
- 如果任务仍在运行：继续等待或检查是否卡住

## 示例用法

### 示例 1：运行测试
```
/bg "python -m pytest tests/test_simple.py -v" 60
```
这将：
1. 后台运行 pytest
2. 等待 60 秒
3. 检查测试结果

### 示例 2：编译 PIM 文件
```
/bg "python pim-compiler/src/cli/main.py compile hello_world.md" 120 "PSM generated\|Code generated"
```
这将：
1. 后台运行编译器
2. 等待 120 秒
3. 检查 PSM 和代码生成状态

### 示例 3：运行长时间构建
```
/bg "npm run build" 180 "built\|error"
```
这将：
1. 后台运行构建
2. 等待 180 秒
3. 检查构建成功或错误

## 实际执行步骤

当用户输入 `/bg <command>` 时，Claude 应该：

1. **创建日志文件**
   ```bash
   LOG_FILE="bg_task_$(date +%Y%m%d_%H%M%S).log"
   ```

2. **启动后台任务**
   ```bash
   nohup $COMMAND > $LOG_FILE 2>&1 &
   echo $! > ${LOG_FILE}.pid
   echo "任务已在后台启动，PID: $(cat ${LOG_FILE}.pid)"
   echo "日志文件: $LOG_FILE"
   ```

3. **初始检查**（5-10秒后）
   ```bash
   sleep 10
   echo "=== 初始状态检查 ==="
   tail -20 $LOG_FILE
   ```

4. **定期监控**
   ```bash
   # 第一次检查（30秒）
   sleep 20
   echo "=== 30秒进度检查 ==="
   tail -50 $LOG_FILE | grep -E "progress|generated|completed|error|failed"
   
   # 第二次检查（60秒）
   sleep 30
   echo "=== 60秒进度检查 ==="
   ps -p $(cat ${LOG_FILE}.pid) > /dev/null && echo "任务仍在运行" || echo "任务已完成"
   tail -50 $LOG_FILE
   ```

5. **最终结果**
   ```bash
   # 检查特定结果模式
   echo "=== 结果摘要 ==="
   grep -i "success\|passed\|completed" $LOG_FILE | tail -10
   grep -i "error\|failed" $LOG_FILE | tail -10
   ```

## 高级功能

### 超时处理
```bash
# 设置最大运行时间
MAX_RUNTIME=600  # 10分钟
START_TIME=$(date +%s)

while ps -p $(cat ${LOG_FILE}.pid) > /dev/null; do
    CURRENT_TIME=$(date +%s)
    ELAPSED=$((CURRENT_TIME - START_TIME))
    
    if [ $ELAPSED -gt $MAX_RUNTIME ]; then
        echo "任务超时，终止进程"
        kill $(cat ${LOG_FILE}.pid)
        break
    fi
    
    sleep 30
    tail -20 $LOG_FILE
done
```

### 智能日志分析
```bash
# 根据日志内容自动决定下一步
if grep -q "All tests passed" $LOG_FILE; then
    echo "所有测试通过！"
elif grep -q "FAILED" $LOG_FILE; then
    echo "测试失败，分析失败原因..."
    grep -B5 -A5 "FAILED" $LOG_FILE
fi
```

## 注意事项

1. **日志文件管理**
   - 为每个任务创建唯一的日志文件
   - 保留日志文件供后续分析
   - 定期清理旧日志文件

2. **进程管理**
   - 保存 PID 用于监控和清理
   - 处理僵尸进程
   - 支持手动终止

3. **错误处理**
   - 检查命令是否存在
   - 处理权限问题
   - 捕获异常退出

4. **性能考虑**
   - 避免过于频繁的检查
   - 使用 grep 过滤大日志文件
   - 限制 tail 输出行数

## 常见场景模板

### 测试运行模板
```
/bg "python -m pytest tests/ -v --cov" 120
```

### 编译模板
```
/bg "python compiler.py input.md -o output/" 180
```

### 服务启动模板
```
/bg "./start_server.sh" 30 "Server started|Error"
```

### 数据处理模板
```
/bg "python process_data.py large_dataset.csv" 300 "Processed|rows"
```