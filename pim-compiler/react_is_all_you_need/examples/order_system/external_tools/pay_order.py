#!/usr/bin/env python3
"""
External Tool: 支付订单（高频操作，符号主义执行）
"""

import json
from datetime import datetime
from pathlib import Path

def execute(order_id, payment_method, amount):
    """支付订单的符号主义实现"""

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
            "error": "订单状态不允许支付",
            "current_status": order["status"],
            "required_status": "PENDING"
        }

    # 验证金额
    if abs(amount - order["total_amount"]) > 0.01:  # 允许1分钱误差
        return {
            "error": "支付金额不正确",
            "order_amount": order["total_amount"],
            "paid_amount": amount
        }

    # 模拟支付（实际应调用支付接口）
    # 这里直接返回成功

    # 更新订单状态
    order["status"] = "PAID"
    order["payment"] = {
        "method": payment_method,
        "amount": amount,
        "paid_at": datetime.now().isoformat()
    }
    order["updated_at"] = datetime.now().isoformat()

    # 扣减库存
    for item in order["items"]:
        product_id = item["product_id"]
        quantity = item["quantity"]
        if product_id in inventory:
            inventory[product_id]["available"] -= quantity
            inventory[product_id]["reserved"] += quantity

    # 保存更新
    orders[order_index] = order
    orders_file.write_text(json.dumps(orders, ensure_ascii=False, indent=2))

    inventory_file = data_dir / "inventory.json"
    inventory_file.write_text(json.dumps(inventory, ensure_ascii=False, indent=2))

    return {
        "success": True,
        "order_id": order_id,
        "status": "PAID",
        "payment_method": payment_method,
        "amount": amount,
        "message": f"支付成功，订单{order_id}已支付{amount}元"
    }

if __name__ == "__main__":
    # 测试支付
    result = execute(
        order_id="ORD2024111700001",
        payment_method="ALIPAY",
        amount=6999.00
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))