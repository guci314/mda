# MCP工具使用知识

## 什么是MCP工具？
MCP (Model Context Protocol) 是Claude的扩展协议，提供额外的工具能力。这些工具以 `mcp__` 前缀命名。

## 可用的MCP工具

### 1. 深度思考工具
- **工具名**: `mcp__sequential-thinking__sequentialthinking`
- **用途**: 复杂问题的链式思考和推理
- **使用场景**:
  - 需要多步推理的问题
  - 需要反思和修正的任务
  - 复杂的架构设计

### 2. 知识图谱工具
- **创建实体**: `mcp__memory__create_entities`
- **创建关系**: `mcp__memory__create_relations`
- **搜索节点**: `mcp__memory__search_nodes`
- **用途**: 构建和查询知识图谱

### 3. UI组件工具
- **21st魔法组件**: `mcp__magic-mcp__21st_magic_component_builder`
- **Logo搜索**: `mcp__magic-mcp__logo_search`
- **用途**: 快速生成UI组件

### 4. 浏览器控制
- **导航**: `mcp__puppeteer__puppeteer_navigate`
- **截图**: `mcp__puppeteer__puppeteer_screenshot`
- **点击**: `mcp__puppeteer__puppeteer_click`
- **用途**: 自动化浏览器操作

## 使用原则

1. **直接调用**：MCP工具可以直接调用，无需额外包装
2. **参数传递**：严格按照工具要求传递参数
3. **错误处理**：MCP工具可能失败，需要降级策略

## 示例用法

### 深度思考
当遇到复杂问题时：
```
使用 mcp__sequential-thinking__sequentialthinking:
- thought: "分析问题的第一步..."
- nextThoughtNeeded: true
- thoughtNumber: 1
- totalThoughts: 5
```

### 创建知识实体
记录新知识时：
```
使用 mcp__memory__create_entities:
- entities: [
    {
      name: "React Agent",
      entityType: "架构组件",
      observations: ["图灵完备", "知识驱动"]
    }
  ]
```

## 注意事项

1. **不要包装MCP工具**：直接使用，不需要Function wrapper
2. **知识驱动**：通过知识文件指导使用，而非硬编码
3. **保持简单**：只在真正需要时使用MCP工具
4. **降级策略**：MCP工具失败时，使用Agent自身能力

## 核心理念
MCP工具是能力扩展，但不应该成为依赖。Agent的核心能力应该通过React + 知识文件实现，MCP只是锦上添花。