# ReactAgent 三级记忆系统使用指南

## 快速开始

### 1. 创建虚拟环境（推荐）

```bash
# 创建虚拟环境
python -m venv react_agent_env

# 激活虚拟环境
source react_agent_env/bin/activate  # Linux/Mac
# 或
react_agent_env\Scripts\activate     # Windows

# 运行安装脚本
./install_react_agent_deps.sh
```

### 2. 使用三级记忆

#### 无记忆模式（默认最快）
```bash
# 适合：一次性任务、简单代码生成
python direct_react_agent_v3_fixed.py --memory none
```

#### 智能缓冲模式（平衡方案）
```bash
# 适合：中等复杂项目、需要上下文连续性
python direct_react_agent_v3_fixed.py --memory smart

# 自定义窗口大小（通过token限制）
python direct_react_agent_v3_fixed.py --memory smart --max-tokens 50000
```

#### 持久化模式（专业项目）
```bash
# 适合：长期项目、需要保存对话历史
python direct_react_agent_v3_fixed.py --memory pro --session-id my_project

# 继续之前的会话
python direct_react_agent_v3_fixed.py --memory pro --session-id my_project
```

## 三级记忆详解

### 1. None（无记忆）
- **原理**：每次调用独立，不保留历史
- **优点**：
  - 速度最快
  - 内存占用最小
  - 无状态，易于并发
- **缺点**：
  - 无法记住之前的上下文
  - 可能重复生成相似代码
- **使用场景**：
  - 简单的PIM到代码转换
  - 批量处理多个独立项目
  - 测试和调试

### 2. Smart（智能缓冲）
- **原理**：保留最近N条对话（窗口缓冲）
- **优点**：
  - 保持上下文连续性
  - 自动管理内存大小
  - 平衡性能和功能
- **缺点**：
  - 超出窗口的历史会丢失
  - 需要更多内存
- **使用场景**：
  - 交互式开发
  - 迭代改进代码
  - 中等复杂度项目

### 3. Pro（SQLite持久化）
- **原理**：所有对话保存到数据库
- **优点**：
  - 永久保存所有历史
  - 可跨会话恢复
  - 支持多个并行项目
- **缺点**：
  - 速度相对较慢
  - 需要管理数据库文件
- **使用场景**：
  - 长期项目开发
  - 需要审计追踪
  - 团队协作项目

## 实际使用示例

### 示例1：快速原型开发
```bash
# 无记忆模式，快速生成代码
python direct_react_agent_v3_fixed.py \
    --memory none \
    --pim-file examples/simple_user_crud.md \
    --output-dir output/prototype
```

### 示例2：迭代开发项目
```bash
# 第一次运行
python direct_react_agent_v3_fixed.py \
    --memory smart \
    --pim-file models/user_management.md \
    --output-dir output/user_system

# 继续改进（记忆保持在会话中）
# ... 修改PIM文件 ...
python direct_react_agent_v3_fixed.py \
    --memory smart \
    --pim-file models/user_management_v2.md \
    --output-dir output/user_system_v2
```

### 示例3：长期项目管理
```bash
# 启动新项目
python direct_react_agent_v3_fixed.py \
    --memory pro \
    --session-id ecommerce_platform \
    --pim-file models/ecommerce.md \
    --output-dir output/ecommerce

# 一周后继续开发
python direct_react_agent_v3_fixed.py \
    --memory pro \
    --session-id ecommerce_platform \
    --pim-file models/ecommerce_payment.md \
    --output-dir output/ecommerce/payment
```

## 性能对比

| 记忆级别 | 启动速度 | 内存占用 | 上下文保持 | 持久化 |
|---------|---------|---------|-----------|--------|
| none    | ⚡⚡⚡   | 最小     | ❌        | ❌     |
| smart   | ⚡⚡     | 中等     | ✅ (有限)  | ❌     |
| pro     | ⚡       | 较大     | ✅ (完整)  | ✅     |

## 故障排除

### 1. Token计数错误
如果遇到 token 计数相关错误，设置环境变量：
```bash
export DISABLE_TOKEN_PATCH=1
python direct_react_agent_v3_fixed.py --memory smart
```

### 2. 导入错误
确保在虚拟环境中运行：
```bash
which python  # 应该显示 react_agent_env 路径
```

### 3. SQLite权限错误
确保有写入权限：
```bash
chmod 755 .
touch memory.db && chmod 644 memory.db
```

## 最佳实践

1. **开发流程**：
   - 原型阶段：使用 `none` 快速迭代
   - 开发阶段：使用 `smart` 保持上下文
   - 生产阶段：使用 `pro` 追踪历史

2. **会话管理**：
   - 为不同项目使用不同的 session-id
   - 定期清理旧的数据库文件
   - 使用有意义的会话名称

3. **性能优化**：
   - 大型项目考虑增加 max-tokens
   - 定期重启以清理内存
   - 监控数据库文件大小

## 环境变量

```bash
# .env 文件示例
DEEPSEEK_API_KEY=your_api_key_here
DISABLE_TOKEN_PATCH=1  # 可选，禁用token计数补丁
```

## 命令行参数完整列表

```bash
python direct_react_agent_v3_fixed.py --help

参数：
  --memory {none,smart,pro}  记忆级别选择
  --session-id TEXT         会话ID（仅pro模式需要）
  --max-tokens INT          最大token数（默认30000）
  --pim-file PATH          PIM文件路径
  --output-dir PATH        输出目录
```

## 总结

ReactAgent 的三级记忆系统提供了灵活的选择：
- **快速简单**：选择 `none`
- **平衡方案**：选择 `smart`（推荐）
- **专业需求**：选择 `pro`

根据项目需求选择合适的记忆级别，可以在性能和功能之间找到最佳平衡。