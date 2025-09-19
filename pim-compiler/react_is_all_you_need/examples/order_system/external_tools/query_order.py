#!/usr/bin/env python3
"""
External Tool: 查询订单（高频操作，符号主义执行）
"""

import json
from pathlib import Path

def execute(order_id=None, user_id=None, status=None):
    """查询订单的符号主义实现"""

    # 加载订单数据
    data_dir = Path("~/.agent/order_system/data").expanduser()
    orders_file = data_dir / "orders.json"

    if not orders_file.exists():
        return {"orders": [], "count": 0}

    orders = json.loads(orders_file.read_text())

    # 过滤订单
    result = orders

    if order_id:
        result = [o for o in result if o["order_id"] == order_id]
        if result:
            return result[0]  # 单个订单直接返回对象
        else:
            return {"error": "订单不存在", "order_id": order_id}

    if user_id:
        result = [o for o in result if o["user_id"] == user_id]

    if status:
        result = [o for o in result if o["status"] == status]

    return {
        "orders": result,
        "count": len(result)
    }

if __name__ == "__main__":
    # 测试查询所有订单
    result = execute()
    print(f"所有订单：{json.dumps(result, ensure_ascii=False, indent=2)}")

    # 测试按用户查询
    result = execute(user_id="USER123")
    print(f"用户订单：{json.dumps(result, ensure_ascii=False, indent=2)}")