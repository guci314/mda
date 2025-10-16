
### Compact压缩系统

#### 核心实现
- [react_agent_minimal.py](core/react_agent_minimal.py) - `_compact_messages()` 实现 (第1424行)
- [compact_prompt.md](knowledge/minimal/system/compact_prompt.md) - ⭐ 压缩提示词（三头注意力机制）
- [system_prompt_minimal.md](knowledge/minimal/system/system_prompt_minimal.md) - 系统提示词模板

#### 理论文档
- [compact_multihead_design.md](knowledge/compact_multihead_design.md) - 🧠 多头注意力设计文档（理论+实践，v1.0）
- [COMPACT_REFACTOR_LOG.md](knowledge/COMPACT_REFACTOR_LOG.md) - 📝 2025-10-14重构日志（历史记录）

#### 测试套件
- [test_compact_prompt.py](tests/test_compact_prompt.py) - ⚡ 质量测试（压缩率+评分，30秒反馈）
- [test_connectionism.py](tests/test_connectionism.py) - 🔬 连接主义验证（语义泛化能力）
- [test_multihead_attention.py](tests/test_multihead_attention.py) - 🎯 多头机制验证（并行处理）
- [README_COMPACT_TEST.md](tests/README_COMPACT_TEST.md) - 测试文档

### Compact压缩机制
**位置**: `knowledge/minimal/system/compact_prompt.md`
**实现**: `core/react_agent_minimal.py:1424-1611`
**测试**: `tests/test_compact_prompt.py` + `test_connectionism.py` + `test_multihead_attention.py`

**核心架构**：三头注意力机制（Multi-Head Attention）
```
每条消息 → [Head1: 上级注意力] → L0/L1/L3/L4
          → [Head2: 自我注意力] → L2/L3/L4
          → [Head3: 环境注意力] → L1/L2/L3/L4
          ↓
    Max-Pooling融合
          ↓
      最终层级（L0-L4）
```

**关键设计**：
- L0-L4五层压缩策略（基于香农编码原理）
- 三个并行注意力头（类比Transformer Multi-Head）
- Max-Pooling融合策略（保守原则，取最高权重）
- 直接API调用（避免递归）
- 连接主义+归纳偏置（非符号主义规则）

**验证结果**：
- 压缩质量：98.7%（平均评分）
- 压缩率：50.4%（平均）
- 语义泛化：100%（识别未见过的表达）
- 多头机制：✅ 验证通过（复合信息激活多个头）

**相关决策**：
- [为什么用API而不是Agent?](#为什么compact用api而不是agent) → 避免递归，基础设施层操作
- [为什么是5层?](#为什么是l0-l4五层) → 平衡精度和性能
- [为什么是三个头?](#为什么是三个注意力头) → 基于Object关系的归纳偏置
- [为什么用Max而不是Average?](#为什么用max-pooling) → 保守策略，防止关键信息降级


