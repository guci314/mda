#!/usr/bin/env python3
"""
斜杠命令集成示例
展示如何让Agent支持斜杠命令条件反射
"""

import sys
import json
from pathlib import Path

# 添加项目路径
sys.path.append(str(Path(__file__).parent.parent))

from core.interceptors.slash_command_interceptor import SlashCommandInterceptor


class AgentWithSlashCommands:
    """支持斜杠命令的Agent"""

    def __init__(self, name):
        self.name = name
        self.home = Path(f"~/.agent/{name}").expanduser()
        self.home.mkdir(parents=True, exist_ok=True)

        # 初始化斜杠命令拦截器
        self.slash_interceptor = SlashCommandInterceptor(name)

        # 自动注册external_tools目录中的工具
        registered = self.slash_interceptor.auto_register_from_tools_dir()
        if registered > 0:
            print(f"✅ 自动注册了 {registered} 个工具")

    def process(self, message: str) -> str:
        """
        处理消息，优先尝试斜杠命令

        Args:
            message: 用户输入

        Returns:
            处理结果
        """
        # 1. 先尝试斜杠命令（条件反射）
        reflex_result = self.slash_interceptor.intercept(message)
        if reflex_result is not None:
            print("⚡ 条件反射执行")
            return reflex_result

        # 2. 不是斜杠命令，正常处理
        print("🤔 LLM推理处理")
        return self.llm_process(message)

    def llm_process(self, message: str) -> str:
        """模拟LLM处理"""
        return f"LLM理解并处理: {message}"

    def create_tool(self, tool_name: str, tool_code: str,
                   slash_command: str = None, description: str = "") -> str:
        """
        创建工具并自动注册斜杠命令

        Args:
            tool_name: 工具名称
            tool_code: 工具代码
            slash_command: 斜杠命令名（可选）
            description: 工具描述

        Returns:
            创建结果
        """
        # 1. 保存工具
        tools_dir = self.home / "external_tools"
        tools_dir.mkdir(exist_ok=True)

        tool_path = tools_dir / f"{tool_name}.py"
        tool_path.write_text(tool_code)
        tool_path.chmod(0o755)

        # 2. 注册斜杠命令
        if slash_command is None:
            slash_command = tool_name.replace("_", "-")

        self.slash_interceptor.register(
            command=slash_command,
            tool_path=str(tool_path),
            description=description or f"{tool_name} tool"
        )

        return f"✅ 工具已创建: {tool_path}\n✅ 斜杠命令已注册: /{slash_command}"


def create_inventory_tool_example():
    """创建库存管理工具示例"""

    tool_code = '''#!/usr/bin/env python3
import sys
import json
from pathlib import Path

# 模拟库存数据
INVENTORY_FILE = Path("~/.agent/inventory.json").expanduser()

def load_inventory():
    if INVENTORY_FILE.exists():
        return json.loads(INVENTORY_FILE.read_text())
    return {
        "001": {"name": "商品A", "stock": 50, "threshold": 10},
        "002": {"name": "商品B", "stock": 25, "threshold": 5},
        "003": {"name": "商品C", "stock": 0, "threshold": 10}
    }

def save_inventory(data):
    INVENTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    INVENTORY_FILE.write_text(json.dumps(data, indent=2))

def main():
    args = sys.argv[1:] if len(sys.argv) > 1 else ["list"]
    inventory = load_inventory()

    if args[0] == "list":
        print("📦 库存列表：")
        for pid, info in inventory.items():
            status = "⚠️ 库存预警" if info["stock"] <= info["threshold"] else "✅"
            print(f"  {pid}: {info['name']}, 库存: {info['stock']} {status}")

    elif args[0] == "query" and len(args) > 1:
        pid = args[1]
        if pid in inventory:
            info = inventory[pid]
            print(f"商品 {pid}: {info['name']}")
            print(f"库存: {info['stock']}")
            print(f"阈值: {info['threshold']}")
            if info['stock'] <= info['threshold']:
                print("⚠️ 库存预警！")
        else:
            print(f"❌ 商品 {pid} 不存在")

    elif args[0] == "update" and len(args) > 2:
        pid = args[1]
        change = args[2]
        if pid in inventory:
            if change.startswith("+"):
                inventory[pid]["stock"] += int(change[1:])
            elif change.startswith("-"):
                inventory[pid]["stock"] -= int(change[1:])
            else:
                inventory[pid]["stock"] = int(change)
            save_inventory(inventory)
            print(f"✅ 更新成功: {pid} 库存现在是 {inventory[pid]['stock']}")
        else:
            print(f"❌ 商品 {pid} 不存在")

    elif args[0] == "check":
        print("🔍 库存检查：")
        warnings = []
        for pid, info in inventory.items():
            if info["stock"] <= info["threshold"]:
                warnings.append(f"  ⚠️ {pid}: {info['name']} (库存: {info['stock']})")
        if warnings:
            print("\\n".join(warnings))
        else:
            print("  ✅ 所有商品库存正常")

    else:
        print("用法：")
        print("  list              - 列出所有库存")
        print("  query <id>        - 查询指定商品")
        print("  update <id> <±n>  - 更新库存")
        print("  check             - 检查库存预警")

if __name__ == "__main__":
    main()
'''

    return tool_code


def main():
    """主函数示例"""

    print("=" * 60)
    print("斜杠命令条件反射示例")
    print("=" * 60)

    # 1. 创建Agent
    agent = AgentWithSlashCommands("demo_agent")

    # 2. 创建库存管理工具
    print("\n📦 创建库存管理工具...")
    tool_code = create_inventory_tool_example()
    result = agent.create_tool(
        tool_name="inventory_manager",
        tool_code=tool_code,
        slash_command="inv",
        description="库存管理工具"
    )
    print(result)

    # 3. 注册别名
    agent.slash_interceptor.register(
        command="inventory",
        tool_path=str(agent.home / "external_tools" / "inventory_manager.py"),
        description="库存管理工具（完整命令）",
        aliases=["stock", "库存"]
    )

    # 4. 测试斜杠命令
    print("\n" + "=" * 60)
    print("测试斜杠命令")
    print("=" * 60)

    test_commands = [
        "/help",
        "/inv list",
        "/inv query 001",
        "/inv update 002 +10",
        "/inv check",
        "/list",
        "这不是斜杠命令，需要LLM处理",
        "/unknown_command",
    ]

    for cmd in test_commands:
        print(f"\n>>> {cmd}")
        result = agent.process(cmd)
        print(result)

    # 5. 显示使用建议
    print("\n" + "=" * 60)
    print("使用模式分析")
    print("=" * 60)

    suggestions = agent.slash_interceptor.suggest_new_commands()
    if suggestions:
        print("💡 基于使用模式的建议：")
        for s in suggestions:
            print(f"  - {s['pattern']} (使用{s['count']}次)")
            print(f"    {s['suggestion']}")
    else:
        print("暂无使用建议")

    print("\n" + "=" * 60)
    print("示例完成！")
    print("=" * 60)
    print("\n关键特性展示：")
    print("1. ⚡ 斜杠命令直接执行（条件反射）")
    print("2. 🤔 非斜杠命令走LLM处理")
    print("3. 🔧 Agent可以自己创建工具并注册命令")
    print("4. 📊 自动统计使用情况")
    print("5. 💡 基于使用模式提供优化建议")


if __name__ == "__main__":
    main()