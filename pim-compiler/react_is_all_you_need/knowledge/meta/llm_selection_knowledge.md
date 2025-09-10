# LLM选择常识知识

## 核心理念
选择LLM就像选择工具：
- 钉钉子用锤子，不用显微镜
- 做手术用手术刀，不用斧头
- 每个LLM都有最适合的场景

## LLM特性矩阵

| LLM | 速度 | 成本 | 推理 | 代码 | 创意 | 最佳场景 |
|-----|------|------|------|------|------|----------|
| grok-fast | ⚡⚡⚡ | 💰 | ⭐⭐ | ⭐⭐⭐ | ⭐⭐ | 文件操作、快速查询 |
| gemini-flash | ⚡⚡⚡ | 💰 | ⭐⭐ | ⭐⭐ | ⭐⭐ | 批量处理、多模态 |
| kimi-turbo | ⚡⚡ | 💰💰 | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | 长文本、文档处理 |
| deepseek | ⚡ | 💰💰 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | 代码调试、深度分析 |
| claude-sonnet | ⚡ | 💰💰💰 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 复杂推理、创意设计 |

## 任务类型映射

### 🚀 需要速度的任务
**选择**: grok-fast, gemini-flash
```
- 文件列表 (ls)
- 简单查询 (cat, grep)
- 目录操作 (mkdir, rm)
- 格式转换
- 批量重命名
```

### 🧠 需要深度的任务
**选择**: deepseek, claude-sonnet
```
- 代码调试
- 架构设计
- 算法优化
- 性能分析
- 安全审计
```

### 📝 需要创意的任务
**选择**: claude-sonnet, kimi
```
- 文档编写
- API设计
- 用户故事
- 技术博客
- 代码注释
```

### 🔍 需要精确的任务
**选择**: deepseek
```
- 单元测试
- 集成测试
- 错误定位
- 代码审查
- 重构建议
```

## 选择决策流程

```python
def select_llm(task):
    # 1. 紧急度检查
    if "紧急" in task or "立即" in task:
        return "grok-fast"  # 最快响应
    
    # 2. 复杂度检查
    if "调试" in task or "修复" in task:
        return "deepseek"  # 最强调试
    
    # 3. 创意度检查
    if "设计" in task or "创建" in task:
        return "claude-sonnet"  # 最有创意
    
    # 4. 文档类检查
    if "文档" in task or "说明" in task:
        return "kimi-turbo"  # 最擅长文档
    
    # 5. 默认选择
    return "grok-fast"  # 通用快速
```

## 成本优化策略

### 预算充足时
1. 复杂任务 → claude-sonnet
2. 中等任务 → deepseek
3. 简单任务 → grok-fast

### 预算有限时
1. 复杂任务 → deepseek
2. 中等任务 → kimi-turbo
3. 简单任务 → grok-fast

### 极限节省时
1. 所有任务 → grok-fast
2. 只在失败时升级模型

## 组合使用模式

### 探索-精炼模式
```
grok-fast (快速探索) → deepseek (深度精炼)
```

### 生成-审查模式
```
claude-sonnet (创意生成) → deepseek (严格审查)
```

### 分析-总结模式
```
deepseek (深度分析) → kimi-turbo (文档总结)
```

## 常见错误

❌ **过度使用高端模型**
- 问题: 简单任务用claude-sonnet
- 后果: 成本高、速度慢
- 正确: 用grok-fast

❌ **低端模型处理复杂任务**
- 问题: 用grok-fast调试复杂bug
- 后果: 反复失败、浪费时间
- 正确: 直接用deepseek

❌ **忽视上下文窗口**
- 问题: 长文档用短上下文模型
- 后果: 信息丢失
- 正确: 用kimi或claude

## 动态调整规则

### 失败升级
```
grok-fast失败 → 升级到kimi-turbo
kimi-turbo失败 → 升级到deepseek
deepseek失败 → 升级到claude-sonnet
```

### 成功降级
```
连续3次简单任务成功 → 考虑降级模型
节省成本，保持效率
```

### 负载均衡
```
高并发时分散到多个模型
避免单点限流
```

## 未来趋势

1. **专门化**: 每个LLM会更专注特定领域
2. **本地化**: 小模型本地部署处理隐私数据
3. **协作化**: 多个LLM协同工作
4. **自适应**: LLM自动选择最佳配置

## 记住
- 没有最好的LLM，只有最适合的LLM
- 成本和效果的平衡是艺术
- 让Meta Agent的选择成为常识，而非规则