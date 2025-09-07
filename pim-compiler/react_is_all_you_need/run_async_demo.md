# 异步Agent演示运行指南

## 准备工作

### 1. 安装watchdog（推荐）
```bash
pip install watchdog
```

## 方案对比运行

### 方案1：原始版（高API消耗）
```bash
# 终端1 - 启动李四监听（会持续消耗API）
python demo_zhangsan_lisi.py lisi

# 终端2 - 张三发送消息
python demo_zhangsan_lisi.py zhangsan

# 清理
python demo_zhangsan_lisi.py clean
```

### 方案2：Python循环版（有消息才调用API）
```bash
# 终端1 - 启动李四监听
python demo_zhangsan_lisi_correct.py lisi

# 终端2 - 张三发送消息  
python demo_zhangsan_lisi_correct.py zhangsan

# 停止李四服务
python demo_zhangsan_lisi_correct.py stop

# 清理
python demo_zhangsan_lisi_correct.py clean
```

### 方案3：Watchdog事件驱动版（最优方案）⭐⭐⭐⭐⭐
```bash
# 终端1 - 启动李四监听（0 API空闲成本）
python demo_zhangsan_lisi_watchdog.py lisi

# 终端2 - 张三发送消息
python demo_zhangsan_lisi_watchdog.py zhangsan

# 清理
python demo_zhangsan_lisi_watchdog.py clean
```

## 批量测试

### 连续发送多条消息测试
```bash
# 终端1 - 启动李四监听
python demo_zhangsan_lisi_watchdog.py lisi

# 终端2 - 连续发送3条消息
python demo_zhangsan_lisi_watchdog.py zhangsan
sleep 2
python demo_zhangsan_lisi_watchdog.py zhangsan
sleep 2
python demo_zhangsan_lisi_watchdog.py zhangsan
```

## 性能对比

| 方案 | 空闲时API调用 | 响应延迟 | 推荐场景 |
|------|--------------|----------|----------|
| 原始版 | 60次/分钟 | 1秒 | 不推荐 |
| Python循环 | 0次 | 1秒 | 测试环境 |
| **Watchdog** | **0次** | **<0.1秒** | **生产环境** |

## 监控运行状态

```bash
# 查看inbox目录
ls -la .inbox/

# 查看李四的inbox
ls -la .inbox/李四/

# 查看张三的inbox  
ls -la .inbox/张三/

# 实时监控inbox变化
watch -n 1 'ls -la .inbox/*/'
```

## 故障排查

```bash
# 检查是否有遗留进程
ps aux | grep demo_zhangsan_lisi

# 强制停止所有相关进程
pkill -f demo_zhangsan_lisi

# 完全清理
rm -rf .inbox/
rm -f monitor_lisi.*
```

## 最佳实践

1. **开发测试**：使用原始版快速验证逻辑
2. **性能测试**：使用Python循环版测试消息处理
3. **正式部署**：使用Watchdog版实现真正的异步服务

## 注意事项

- Watchdog版需要先安装：`pip install watchdog`
- 确保有.env文件配置API密钥
- 李四服务使用Ctrl+C优雅退出
- 每次测试后记得清理inbox目录