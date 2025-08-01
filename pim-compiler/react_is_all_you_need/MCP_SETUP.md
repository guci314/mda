# MCP (Model Context Protocol) 设置说明 - Claude Code 版本

## 已安装的 MCP 服务器

我已经为您安装并配置了以下 MCP 服务器：

### 1. Memory Server (知识图谱记忆)
- **功能**：通过知识图谱为 Claude 提供持久记忆能力
- **路径**：`~/.mcp-servers/src/memory`
- **用途**：存储和检索对话中的重要信息、实体关系等

### 2. Filesystem Server
- **功能**：安全的文件系统访问
- **路径**：`~/.mcp-servers/src/filesystem`
- **权限**：只能访问 `/home/guci/aiProjects` 目录
- **用途**：读写文件、创建目录等操作

### 3. Git Server
- **功能**：Git 仓库操作
- **路径**：`~/.mcp-servers/src/git`
- **用途**：查看提交历史、diff、分支等信息

### 4. Context7 Server (最新安装)
- **功能**：为 AI 提供最新的代码文档和技术信息
- **类型**：HTTP MCP 服务器
- **URL**：`https://mcp.context7.com/mcp`
- **用途**：获取最新的框架文档、API 参考、最佳实践等

## 配置文件位置

配置文件已创建在：
- 项目级配置：`/home/guci/aiProjects/mda/.mcp.json`
- 用户级配置：`~/.claude.json`

## 使用说明

1. **重新加载 MCP 服务器**
   - 在 Claude Code 中，MCP 服务器应该会自动加载
   - 如果没有，可以尝试重新打开项目

2. **验证安装**
   - 在 Claude 中，您应该能看到新的 MCP 工具
   - 可以使用 `ListMcpResourcesTool` 查看可用资源

3. **Memory Server 使用示例**
   ```
   - "记住我叫张三，是一名软件工程师"
   - "创建一个关于项目架构的知识图谱"
   - "我之前告诉过你什么信息？"
   ```

4. **Context7 Server 使用示例**
   ```
   - "创建一个 Next.js app router 项目 use context7"
   - "如何在 Next.js 15 中实现认证？use context7"
   - "React 19 的新特性是什么？use context7"
   ```
   
   **重要**：在提示词末尾添加 `use context7` 来激活该服务器

## Claude Code 命令行管理

查看已安装的 MCP 服务器：
```bash
claude mcp list
```

添加新服务器（项目范围）：
```bash
claude mcp add --scope project <name> <command> [args...]
```

添加新服务器（用户范围）：
```bash
claude mcp add --scope user <name> <command> [args...]
```

删除服务器：
```bash
claude mcp remove <name>
```

## 其他可用的 MCP 服务器

在 `~/.mcp-servers/src` 目录下还有其他服务器可以安装：
- `everything` - 测试服务器，包含所有功能
- `fetch` - 网页内容获取
- `time` - 时间相关功能
- `sequentialthinking` - 顺序思考辅助
- `git` - Git 操作功能

## 故障排除

如果 MCP 服务器无法正常工作：

1. 列出当前配置：
   ```bash
   claude mcp list
   ```

2. 手动测试服务器：
   ```bash
   node ~/.mcp-servers/src/memory/dist/index.js
   ```

3. 确保 Node.js 版本 >= 18：
   ```bash
   node --version
   ```

4. 检查项目配置文件：
   ```bash
   cat /home/guci/aiProjects/mda/.mcp.json
   ```

## 添加更多服务器示例

添加 Git 服务器：
```bash
claude mcp add --scope project git node ~/.mcp-servers/src/git/dist/index.js
```

添加时间服务器：
```bash
cd ~/.mcp-servers/src/time && npm install && npm run build
claude mcp add --scope project time node ~/.mcp-servers/src/time/dist/index.js
```

---

**注意**：MCP 功能是 Claude Code 的核心特性之一。服务器配置会在下次打开项目时自动加载。