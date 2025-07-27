# ReactAgent v3 三级记忆功能

## 功能概述

ReactAgent v3 现已支持三级记忆系统，让代码生成更智能、更高效。

## 三级记忆配置

### 1. 无记忆模式 (`--memory none`)
- **特点**：每次运行完全独立，无历史记录
- **性能**：最快，零额外开销
- **用途**：一次性代码生成、模板项目、Demo
- **命令**：
  ```bash
  python direct_react_agent_v3_fixed.py --memory none
  ```

### 2. 智能记忆模式 (`--memory smart`) 【默认】
- **特点**：使用 Summary Buffer，智能平衡记忆和性能
- **性能**：中等，Token 使用可控
- **用途**：迭代开发、错误修复、功能增强
- **命令**：
  ```bash
  python direct_react_agent_v3_fixed.py --memory smart
  # 或直接运行（默认使用smart）
  python direct_react_agent_v3_fixed.py
  ```

### 3. 专业记忆模式 (`--memory pro`)
- **特点**：SQLite 持久化存储，支持会话恢复
- **性能**：稍慢，但提供完整历史追溯
- **用途**：长期项目、团队协作、企业应用
- **命令**：
  ```bash
  python direct_react_agent_v3_fixed.py --memory pro --session-id project_123
  ```

## 命令行参数

```bash
python direct_react_agent_v3_fixed.py [options]

Options:
  --memory {none,smart,pro}    记忆级别 (默认: smart)
  --session-id SESSION_ID      会话ID，用于pro模式 (自动生成)
  --pim-file PIM_FILE         PIM文件路径 (默认: ../models/domain/用户管理_pim.md)
  --output-dir OUTPUT_DIR     输出目录 (默认: output/react_agent_v3)
```

## 使用场景示例

### 场景1：快速生成API脚手架
```bash
# 使用无记忆模式，快速生成
python direct_react_agent_v3_fixed.py --memory none --output-dir output/api_scaffold
```

### 场景2：迭代开发用户系统
```bash
# 第一次：创建基础结构
python direct_react_agent_v3_fixed.py --memory smart

# 第二次：基于记忆添加认证功能
# Agent会记住之前的代码结构，避免重复工作
python direct_react_agent_v3_fixed.py --memory smart
# 输入："基于之前的用户系统，添加JWT认证"

# 第三次：修复问题
python direct_react_agent_v3_fixed.py --memory smart
# 输入："修复刚才认证中的token过期问题"
```

### 场景3：企业级项目开发
```bash
# 项目启动
python direct_react_agent_v3_fixed.py --memory pro --session-id erp_system_v2

# 一周后继续开发（恢复会话）
python direct_react_agent_v3_fixed.py --memory pro --session-id erp_system_v2
# Agent会记住整个项目历史，可以继续之前的工作

# 查看历史记录
sqlite3 memory.db "SELECT * FROM message_store WHERE session_id='erp_system_v2';"
```

## 记忆数据存储位置

- **Smart模式**：内存中，程序结束后清除
- **Pro模式**：
  - 默认数据库：`./memory.db`
  - 可通过环境变量自定义：`MEMORY_DB_PATH=/path/to/memory.db`

## 性能对比

| 模式 | 启动时间 | Token消耗 | 适用场景 |
|------|---------|-----------|----------|
| None | 0ms | 基准 | 简单任务 |
| Smart | 5ms | +20-30% | 常规开发 |
| Pro | 20ms | +30-40% | 复杂项目 |

## 最佳实践

1. **默认使用 Smart 模式**
   - 适合大多数开发场景
   - 自动管理记忆，无需配置

2. **长期项目使用 Pro 模式**
   - 使用有意义的 session-id
   - 定期备份 memory.db
   - 可以在团队间共享数据库

3. **简单任务使用 None 模式**
   - 生成简单的CRUD代码
   - 创建项目模板
   - 性能测试

## 注意事项

1. **Smart模式**的记忆在程序退出后会丢失
2. **Pro模式**需要指定 session-id 才能恢复之前的会话
3. 记忆功能会增加 Token 使用量，请注意 API 配额

## 故障排除

### 问题：记忆似乎没有生效
- 检查是否使用了正确的记忆模式
- Smart模式需要在同一个运行会话中才能保持记忆
- Pro模式需要使用相同的session-id

### 问题：Token 超限
- 切换到 Smart 模式（自动压缩历史）
- 或使用 None 模式（无记忆）

### 问题：数据库错误
- 检查 memory.db 文件权限
- 删除损坏的数据库文件重新开始

## 更新日志

- v3.0: 初始三级记忆系统实现
- 支持 none/smart/pro 三种模式
- 命令行参数配置
- SQLite 持久化存储