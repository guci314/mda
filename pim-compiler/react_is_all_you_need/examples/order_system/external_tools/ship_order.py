#!/usr/bin/env python3
"""
External Tool: 订单发货（符号主义执行）
"""

import json
from datetime import datetime
from pathlib import Path

def execute(order_id, company, tracking_no):
    """发货的符号主义实现"""

    # 加载数据
    data_dir = Path("~/.agent/order_system/data").expanduser()
    orders_file = data_dir / "orders.json"
    orders = json.loads(orders_file.read_text())

    # 查找订单
    order = None
    order_index = None
    for i, o in enumerate(orders):
        if o["order_id"] == order_id:
            order = o
            order_index = i
            break

    if not order:
        return {"error": "订单不存在", "order_id": order_id}

    # 验证状态
    if order["status"] != "PAID":
        return {
            "error": "订单状态不允许发货",
            "current_status": order["status"],
            "required_status": "PAID"
        }

    # 更新订单
    order["status"] = "SHIPPED"
    order["shipping"] = {
        "company": company,
        "tracking_no": tracking_no,
        "shipped_at": datetime.now().isoformat()
    }
    order["updated_at"] = datetime.now().isoformat()

    # 保存
    orders[order_index] = order
    orders_file.write_text(json.dumps(orders, ensure_ascii=False, indent=2))

    return {
        "success": True,
        "order_id": order_id,
        "status": "SHIPPED",
        "shipping": order["shipping"],
        "message": f"订单{order_id}已发货，{company}运单号：{tracking_no}"
    }

if __name__ == "__main__":
    result = execute(
        order_id="ORD2024111700001",
        company="顺丰",
        tracking_no="SF1234567890"
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))