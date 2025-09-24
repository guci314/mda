# 斜杠命令条件反射设计

## 核心理念

**Agent创建的工具应该可以通过斜杠命令直接触发，绕过LLM，实现脊髓反射**

## 系统架构

```
用户输入 → 斜杠命令检测 → 条件反射执行 → 直接返回结果
   ↓                          ↓
  /inventory list            不经过LLM
                            直接执行工具
```

## 实现设计

### 1. 斜杠命令注册表

```python
class SlashCommandRegistry:
    """斜杠命令注册中心"""

    def __init__(self, agent_home):
        self.agent_home = Path(agent_home)
        self.registry_file = self.agent_home / "slash_commands.json"
        self.load_registry()

    def load_registry(self):
        """从文件加载注册表"""
        if self.registry_file.exists():
            self.commands = json.loads(self.registry_file.read_text())
        else:
            self.commands = {}
            self.save_registry()

    def register(self, command, tool_path, description):
        """注册新命令"""
        self.commands[command] = {
            "tool": tool_path,
            "description": description,
            "created": datetime.now().isoformat()
        }
        self.save_registry()

    def save_registry(self):
        """保存注册表"""
        self.registry_file.write_text(json.dumps(self.commands, indent=2))
```

### 2. 条件反射拦截器

```python
class SlashCommandInterceptor:
    """斜杠命令拦截器（脊髓反射）"""

    def __init__(self, agent_name):
        self.agent_name = agent_name
        self.agent_home = Path(f"~/.agent/{agent_name}").expanduser()
        self.registry = SlashCommandRegistry(self.agent_home)

    def intercept(self, message: str) -> Optional[str]:
        """拦截斜杠命令，条件反射执行"""
        if not message.startswith("/"):
            return None  # 不是斜杠命令，交给LLM处理

        # 解析命令
        parts = message.strip().split()
        command = parts[0][1:]  # 去掉斜杠
        args = parts[1:] if len(parts) > 1 else []

        # 查找注册的命令
        if command in self.registry.commands:
            tool_info = self.registry.commands[command]
            tool_path = Path(tool_info["tool"]).expanduser()

            # 直接执行工具（条件反射）
            return self.execute_tool(tool_path, args)

        # 未知命令，可能需要LLM理解
        return None

    def execute_tool(self, tool_path: Path, args: list) -> str:
        """执行外部工具"""
        import subprocess

        try:
            cmd = [str(tool_path)] + args
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                return result.stdout
            else:
                return f"❌ 工具执行失败: {result.stderr}"
        except Exception as e:
            return f"❌ 执行错误: {str(e)}"
```

### 3. Agent自动注册工具

```python
class ToolCreatingAgent:
    """会创建工具并自动注册斜杠命令的Agent"""

    def create_external_tool(self, tool_name, tool_code, slash_command=None):
        """创建工具并注册斜杠命令"""

        # 1. 保存工具代码
        tool_path = self.home / "external_tools" / f"{tool_name}.py"
        tool_path.parent.mkdir(exist_ok=True)
        tool_path.write_text(tool_code)
        tool_path.chmod(0o755)  # 设置可执行

        # 2. 自动注册斜杠命令
        if slash_command is None:
            slash_command = tool_name.replace("_", "-")

        self.registry.register(
            command=slash_command,
            tool_path=str(tool_path),
            description=f"Execute {tool_name} tool"
        )

        # 3. 更新能力文档
        self.update_knowledge(f"""
        ## 新工具：/{slash_command}
        - 工具路径：{tool_path}
        - 使用方式：/{slash_command} [参数]
        - 这是条件反射命令，会直接执行，不经过推理
        """)

        return f"✅ 工具已创建并注册斜杠命令: /{slash_command}"
```

## 具体实例：库存管理

### 注册表配置
```json
{
  "inventory": {
    "tool": "~/.agent/inventory_manager_grok_code_fast__14279/external_tools/inventory_manager.py",
    "description": "库存管理工具",
    "created": "2025-09-23T21:39:07"
  },
  "inv": {
    "tool": "~/.agent/inventory_manager_grok_code_fast__14279/external_tools/inventory_manager.py",
    "description": "库存管理工具（简写）",
    "created": "2025-09-23T21:39:07"
  }
}
```

### 使用示例

```bash
# 用户输入斜杠命令
/inventory list

# 条件反射流程：
# 1. 拦截器识别"/inventory"
# 2. 查找注册表，找到inventory_manager.py
# 3. 直接执行: ~/.agent/.../inventory_manager.py list
# 4. 返回结果（不经过LLM）

# 输出：
所有库存记录:
- 商品ID: 001, 名称: 商品A, 库存: 50
- 商品ID: 002, 名称: 商品B, 库存: 25
- 商品ID: 003, 名称: 商品C, 库存: 0 ⚠️
```

### 其他命令示例

```bash
/inventory query 001          # 查询商品001
/inv update 002 +10           # 商品002增加10个
/inv check                    # 检查库存预警
/inventory help               # 显示帮助
```

## 高级特性

### 1. 命令别名

```python
class CommandAliases:
    """支持命令别名"""

    def add_alias(self, alias, target_command):
        """添加别名"""
        # /inv 是 /inventory 的别名
        self.registry.commands[alias] = self.registry.commands[target_command].copy()
        self.registry.commands[alias]["alias_of"] = target_command
```

### 2. 参数解析

```python
class SmartArgumentParser:
    """智能参数解析"""

    def parse(self, command, args):
        # /inv 001 +10
        # 智能理解为：inventory_manager.py update 001 +10

        if command == "inv" and len(args) == 2:
            if args[1].startswith("+") or args[1].startswith("-"):
                return ["update"] + args

        return args
```

### 3. 条件反射链

```python
class ReflexChain:
    """条件反射链"""

    def register_chain(self, trigger, commands):
        """注册反射链"""
        # /restock → 依次执行多个命令
        self.chains[trigger] = commands

    def execute_chain(self, trigger):
        """执行反射链"""
        for command in self.chains[trigger]:
            result = self.execute_command(command)
            if "error" in result.lower():
                break
```

### 4. 动态工具生成

```python
class DynamicToolGenerator:
    """Agent动态生成工具并注册"""

    def learn_pattern(self, user_requests):
        """从用户请求学习模式"""
        if self.is_frequent_pattern(user_requests):
            # 自动生成工具
            tool_code = self.generate_tool_code(user_requests)

            # 自动注册斜杠命令
            command = self.suggest_command_name(user_requests)

            self.create_external_tool(
                tool_name=command,
                tool_code=tool_code,
                slash_command=command
            )
```

## 系统集成

### 1. 与React Agent集成

```python
class ReactAgentWithSlashCommands:
    def __init__(self, name):
        self.name = name
        self.interceptor = SlashCommandInterceptor(name)

    def process_message(self, message):
        # 先尝试条件反射
        reflex_result = self.interceptor.intercept(message)
        if reflex_result:
            return reflex_result  # 快速返回，不用LLM

        # 不是斜杠命令，正常处理
        return self.llm_process(message)
```

### 2. 学习和优化

```python
class AdaptiveSlashCommands:
    """自适应斜杠命令系统"""

    def analyze_usage(self):
        """分析使用模式"""
        # 记录哪些操作频繁使用
        # 建议创建新的斜杠命令

    def suggest_new_commands(self):
        """建议新命令"""
        frequent_patterns = self.get_frequent_patterns()
        for pattern in frequent_patterns:
            print(f"💡 建议创建斜杠命令: /{pattern['suggested_name']}")
            print(f"   用于: {pattern['description']}")
```

## 实现步骤

### Phase 1: 基础实现
1. 创建SlashCommandRegistry
2. 实现SlashCommandInterceptor
3. 集成到现有Agent系统

### Phase 2: 工具注册
1. Agent创建工具时自动注册
2. 支持手动注册现有工具
3. 命令帮助系统

### Phase 3: 高级功能
1. 命令别名
2. 参数智能解析
3. 条件反射链
4. 使用分析和优化

## 配置文件示例

### ~/.agent/{name}/slash_commands.json
```json
{
  "inventory": {
    "tool": "external_tools/inventory_manager.py",
    "description": "库存管理",
    "usage_count": 156,
    "last_used": "2025-09-23T21:45:00",
    "average_time": "0.02s"
  },
  "report": {
    "tool": "external_tools/report_generator.py",
    "description": "生成报告",
    "usage_count": 23
  },
  "backup": {
    "tool": "external_tools/backup.sh",
    "description": "备份数据",
    "usage_count": 5
  }
}
```

## 优势

1. **速度**：毫秒级响应 vs 秒级LLM推理
2. **成本**：零token消耗
3. **可靠**：确定性执行，不会理解错误
4. **进化**：Agent可以自己创建和优化工具
5. **自主**：Agent管理自己的条件反射

## 哲学思考

这就像人类的技能习得：
- 初学：每个动作都要思考（LLM推理）
- 熟练：形成肌肉记忆（条件反射）
- 专家：大部分操作是自动的（斜杠命令）

Agent通过创建external tools和注册斜杠命令，**把经常使用的能力固化为条件反射**，实现了从"思考"到"本能"的进化。

## 结论

斜杠命令系统让Agent能够：
1. **自主进化**：创建工具，注册命令
2. **提高效率**：条件反射，快速响应
3. **降低成本**：不消耗LLM tokens
4. **保持灵活**：未知命令仍可LLM处理

这是Agent从**纯推理**到**推理+反射**的关键进化。