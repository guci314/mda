# Background Run (Short Version)

## 快速使用
`/bg` - 后台运行命令并监控日志

## 基本用法
```
/bg <命令>
```

## 示例

### 运行测试
```
/bg pytest tests/test_simple.py -v
```

### 编译 PIM
```
/bg python compile.py hello.md
```

### 启动服务
```
/bg ./start.sh
```

## 执行流程

1. **启动任务**
   ```bash
   LOG_FILE="task_$(date +%Y%m%d_%H%M%S).log"
   nohup <命令> > $LOG_FILE 2>&1 &
   echo "PID: $!, 日志: $LOG_FILE"
   ```

2. **10秒后检查**
   ```bash
   sleep 10
   tail -20 $LOG_FILE
   ```

3. **30秒后检查**
   ```bash
   sleep 20
   tail -50 $LOG_FILE | grep -E "error|success|completed|failed"
   ```

4. **60秒后总结**
   ```bash
   sleep 30
   ps -p $PID && echo "仍在运行" || echo "已完成"
   tail -100 $LOG_FILE | grep -E "PASSED|FAILED|Error|Success"
   ```

## 快捷模式

### 测试模式
`/bg test <文件>` → `pytest <文件> -v`

### 编译模式  
`/bg compile <文件>` → 运行编译器

### 检查模式
`/bg check <日志文件>` → 分析现有日志