# 模块知识 - 语义记忆系统实现

## 核心概念
- **自然语言驱动**：通过系统提示词触发，而非硬编码规则
- **语义记忆工具**：`write_semantic_memory` 和 `read_semantic_memory`
- **级联加载**：自动注入当前目录和父目录的 agent.md
- **大道至简**：零额外代码，纯知识文件驱动

## 重要模式
- **系统提示词触发**：在 `system_prompt_minimal.md` 中定义何时写入
- **Agent主动判断**：像人类一样"觉得应该记录"
- **工具类封装**：继承 Function 基类，符合工具系统架构
- **动态注入**：execute() 时基于 work_dir 加载

## 实现细节

### 文件结构
```
core/
├── react_agent_minimal.py      # 注册工具，动态注入
├── tools/
│   └── semantic_memory_tool.py # 工具实现
└── knowledge/
    └── minimal/system/
        └── system_prompt_minimal.md # 触发指导
```

### 关键改动
1. **系统提示词** - 添加"语义记忆管理"章节
2. **工具注册** - `_create_function_instances()` 中添加
3. **工具实现** - WriteSemanticMemoryTool 和 ReadSemanticMemoryTool

## 注意事项
- ⚠️ **参数不需要 required 字段**：Function 基类会处理
- ⚠️ **导入路径**：使用 `from tool_base import Function`
- 📌 **触发时机**：20轮对话或5个文件修改后
- 📌 **记录原则**：知识沉淀，不是日志

## 相关文件
- `core/tools/semantic_memory_tool.py` - 工具实现
- `knowledge/minimal/system/system_prompt_minimal.md` - 触发逻辑
- `docs/memory_architecture.md` - 架构文档
- `test_semantic_memory.py` - 测试脚本

## 验证结果
✅ 系统提示词成功触发写入
✅ 工具正确注册并可调用
✅ 文件成功创建和读取
✅ 级联加载机制正常

---
更新时间：2025-09-11 16:29:00
更新原因：完成语义记忆系统实现，验证自然语言驱动方案