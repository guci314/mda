#!/usr/bin/env python3
"""
External Tool: 取消订单（符号主义执行）
"""

import json
from datetime import datetime
from pathlib import Path

def execute(order_id, reason):
    """取消订单的符号主义实现"""

    # 加载数据
    data_dir = Path("~/.agent/order_system/data").expanduser()
    orders_file = data_dir / "orders.json"
    inventory_file = data_dir / "inventory.json"

    orders = json.loads(orders_file.read_text())
    inventory = json.loads(inventory_file.read_text())

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
    if order["status"] != "PENDING":
        return {
            "error": "只能取消待支付订单",
            "current_status": order["status"],
            "required_status": "PENDING"
        }

    # 恢复库存（如果之前有预留）
    # 注意：在PENDING状态我们还没有扣减库存，所以这里不需要恢复

    # 更新订单
    order["status"] = "CANCELLED"
    order["cancel_reason"] = reason
    order["cancelled_at"] = datetime.now().isoformat()
    order["updated_at"] = datetime.now().isoformat()

    # 保存
    orders[order_index] = order
    orders_file.write_text(json.dumps(orders, ensure_ascii=False, indent=2))

    return {
        "success": True,
        "order_id": order_id,
        "status": "CANCELLED",
        "reason": reason,
        "message": f"订单{order_id}已取消，原因：{reason}"
    }

if __name__ == "__main__":
    result = execute(
        order_id="ORD2024111700001",
        reason="不想要了"
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))