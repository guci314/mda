#!/usr/bin/env python3
"""
订单系统的AIA实现
Agent IS Architecture - Agent就是生产系统

双轨执行：
- 80% JSON请求 → External Tools（微秒级）
- 20% 自然语言 → Agent（毫秒级）
"""

import sys
import os
import json
import importlib.util
from pathlib import Path
from typing import Dict, Any

# 添加父目录到路径
sys.path.insert(0, '/home/guci/aiProjects/mda/pim-compiler/react_is_all_you_need')

from core.react_agent_minimal import ReactAgentMinimal


class OrderAIASystem:
    """订单系统的AIA实现"""

    def __init__(self):
        """初始化AIA系统"""
        # 创建OrderAgent（处理复杂请求）
        self.agent = ReactAgentMinimal(
            name="order_agent",
            description="订单管理系统Agent",
            work_dir="/tmp/order_system",
            model="x-ai/grok-code-fast-1",  # 或其他模型
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY"),
            knowledge_files=[
                str(Path(__file__).parent / "order_agent_knowledge.md")
            ],
            max_rounds=10
        )

        # External Tools目录
        self.tools_dir = Path(__file__).parent / "external_tools"

        # 工具映射（从需求直接推断）
        self.tool_mapping = {
            "create_order": "create_order",
            "query_order": "query_order",
            "pay_order": "pay_order",
            "ship_order": "ship_order",
            "cancel_order": "cancel_order",
            "complete_order": "complete_order"
        }

        print("🚀 OrderAIA系统已启动")
        print(f"  📁 External Tools: {self.tools_dir}")
        print(f"  🤖 Agent: {self.agent.name}")
        print("  ⚡ 双轨模式：JSON快速路径 + 自然语言智能路径")

    def handle_message(self, message: str) -> Dict[str, Any]:
        """
        AIA核心：双轨消息处理
        """
        try:
            # 尝试JSON解析（快速路径）
            json_msg = json.loads(message)

            # 检查是否是工具调用
            if "action" in json_msg and "params" in json_msg:
                action = json_msg["action"]
                params = json_msg["params"]

                # 路由到External Tool（符号主义，不经过LLM）
                if action in self.tool_mapping:
                    return self._call_external_tool(action, params)
                else:
                    return {
                        "error": f"未知操作：{action}",
                        "available_actions": list(self.tool_mapping.keys())
                    }
            else:
                # JSON格式但不是工具调用，转为自然语言让Agent处理
                nl_message = self._json_to_natural_language(json_msg)
                return self._call_agent(nl_message)

        except json.JSONDecodeError:
            # 自然语言请求（智能路径）
            return self._call_agent(message)

    def _call_external_tool(self, action: str, params: Dict) -> Dict[str, Any]:
        """调用External Tool（快速路径，微秒级）"""
        tool_name = self.tool_mapping[action]
        tool_path = self.tools_dir / f"{tool_name}.py"

        if not tool_path.exists():
            # 如果工具不存在，让Agent创建它
            task = f"""
            创建external tool: {tool_name}
            功能：{action}
            参数：{params}
            保存到：{tool_path}
            """
            self.agent.execute(task=task)
            return {"error": f"工具{tool_name}正在创建中，请稍后重试"}

        # 动态加载Python模块
        spec = importlib.util.spec_from_file_location(tool_name, tool_path)
        if spec is None or spec.loader is None:
            return {"error": f"无法加载工具{tool_name}"}

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # 直接执行，不经过LLM
        if hasattr(module, 'execute'):
            result = module.execute(**params)
            print(f"⚡ External Tool执行：{action} → {result.get('message', 'success')}")
            return result
        else:
            return {"error": f"工具{tool_name}没有execute函数"}

    def _call_agent(self, message: str) -> Dict[str, Any]:
        """调用Agent处理（智能路径，毫秒级）"""
        print(f"🤖 Agent处理：{message[:50]}...")
        result = self.agent.execute(task=message)

        # 尝试解析Agent返回的JSON
        try:
            return json.loads(result)
        except:
            # 如果不是JSON，包装成JSON返回
            return {
                "success": True,
                "response": result,
                "handled_by": "agent"
            }

    def _json_to_natural_language(self, json_msg: Dict) -> str:
        """将JSON转换为自然语言（用于Agent处理非标准请求）"""
        # 简单的转换逻辑
        parts = []
        for key, value in json_msg.items():
            parts.append(f"{key}: {value}")
        return "处理请求：" + ", ".join(parts)


def demo():
    """演示AIA系统"""
    print("\n" + "="*60)
    print("订单系统AIA演示")
    print("="*60)

    # 创建AIA系统
    aia = OrderAIASystem()

    # 测试场景1：JSON请求（快速路径）
    print("\n📝 场景1：创建订单（JSON快速路径）")
    request1 = json.dumps({
        "action": "create_order",
        "params": {
            "user_id": "USER123",
            "items": [{"product_id": "PROD001", "quantity": 1}],
            "shipping_address": {
                "name": "张三",
                "phone": "13800138000",
                "address": "北京市朝阳区xxx路xxx号"
            }
        }
    })
    result1 = aia.handle_message(request1)
    print(f"结果：{json.dumps(result1, ensure_ascii=False, indent=2)}")

    # 测试场景2：自然语言请求（智能路径）
    print("\n📝 场景2：自然语言查询（智能路径）")
    request2 = "查询用户USER123的所有订单"
    result2 = aia.handle_message(request2)
    print(f"结果：{json.dumps(result2, ensure_ascii=False, indent=2)}")

    # 测试场景3：复杂业务逻辑（需要Agent推理）
    print("\n📝 场景3：复杂业务逻辑（Agent推理）")
    request3 = "用户USER123想要购买2个iPhone，但如果库存不足就买1个，帮他创建订单"
    result3 = aia.handle_message(request3)
    print(f"结果：{json.dumps(result3, ensure_ascii=False, indent=2)}")

    # 测试场景4：支付订单（JSON快速路径）
    if result1.get("success"):
        print("\n📝 场景4：支付订单（JSON快速路径）")
        order_id = result1.get("order_id")
        request4 = json.dumps({
            "action": "pay_order",
            "params": {
                "order_id": order_id,
                "payment_method": "ALIPAY",
                "amount": result1.get("total_amount", 0)
            }
        })
        result4 = aia.handle_message(request4)
        print(f"结果：{json.dumps(result4, ensure_ascii=False, indent=2)}")

    print("\n" + "="*60)
    print("AIA系统演示完成")
    print("="*60)
    print("""
    总结：
    ✅ JSON请求直接调用External Tools（微秒级）
    ✅ 自然语言请求由Agent处理（毫秒级）
    ✅ Agent可以处理复杂业务逻辑
    ✅ 系统同时支持API调用和人类对话
    """)


if __name__ == "__main__":
    # 运行演示
    demo()