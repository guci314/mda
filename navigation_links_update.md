# 导航链接更新说明

## 问题
维基链接格式`[[页面名|显示名]]`在Markdown中无法点击导航

## 解决方案
将所有维基链接改为标准Markdown链接：

### 1. 相对路径链接（同目录）
```markdown
# 之前（不能点击）
[[ada自我实现|@ada自我实现]]

# 之后（可以点击）
[@ada自我实现](./agent_driven_architecture.md#契约函数-ada自我实现)
```

### 2. 锚点链接（页内跳转）
```markdown
# 链接到特定章节
[@ada自我实现](./agent_driven_architecture.md#契约函数-ada自我实现)
                                                   ^^^^^^^^^^^^^^^^
                                                   锚点到具体章节
```

### 3. 父目录链接
```markdown
# 链接到上级目录的文件
[修正@ada自我实现的执行方式](../../fix_ada_implementation.md)
```

## 已更新的链接

### 主要链接
- `@ada自我实现` → `./agent_driven_architecture.md#契约函数-ada自我实现`
- `@Agent驱动架构` → `./agent_driven_architecture.md`
- `修正文档` → `../../fix_ada_implementation.md`

### 导航效果
现在在VS Code中：
- **Ctrl+Click**（Windows/Linux）或 **Cmd+Click**（Mac）可以直接跳转
- 鼠标悬停会显示链接预览
- 支持返回导航（Alt+左箭头）

## 测试方法
1. 在VS Code中打开`self_awareness.md`
2. 按住Ctrl/Cmd，点击任意蓝色链接
3. 应该能跳转到对应文件和章节

## 注意事项
- 确保文件路径正确
- 锚点名称要与目标文件的标题完全匹配
- 中文锚点需要正确编码