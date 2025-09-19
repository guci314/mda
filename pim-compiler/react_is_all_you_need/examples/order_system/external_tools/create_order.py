#!/usr/bin/env python3
"""
External Tool: 创建订单（高频操作，符号主义执行）
直接执行，不经过LLM，微秒级响应
"""

import json
import os
from datetime import datetime
from pathlib import Path

def execute(user_id, items, shipping_address):
    """创建订单的符号主义实现"""

    # 设置数据目录
    data_dir = Path("~/.agent/order_system/data").expanduser()
    data_dir.mkdir(parents=True, exist_ok=True)

    # 加载数据
    orders_file = data_dir / "orders.json"
    inventory_file = data_dir / "inventory.json"
    users_file = data_dir / "users.json"

    # 初始化数据文件
    if not orders_file.exists():
        orders_file.write_text("[]")
    if not inventory_file.exists():
        inventory_file.write_text(json.dumps({
            "PROD001": {"available": 100, "reserved": 0, "price": 6999.00, "name": "iPhone 15"},
            "PROD002": {"available": 50, "reserved": 0, "price": 4999.00, "name": "iPad Pro"}
        }))
    if not users_file.exists():
        users_file.write_text(json.dumps({
            "USER123": {"name": "张三", "phone": "13800138000", "points": 1000}
        }))

    orders = json.loads(orders_file.read_text())
    inventory = json.loads(inventory_file.read_text())
    users = json.loads(users_file.read_text())

    # 1. 验证用户
    if user_id not in users:
        return {"error": "用户不存在", "user_id": user_id}

    # 2. 检查库存并计算总价
    total_amount = 0.0
    for item in items:
        product_id = item["product_id"]
        quantity = item["quantity"]

        if product_id not in inventory:
            return {"error": "商品不存在", "product_id": product_id}

        if inventory[product_id]["available"] < quantity:
            return {
                "error": "库存不足",
                "product_id": product_id,
                "requested": quantity,
                "available": inventory[product_id]["available"]
            }

        # 添加商品名称和价格到item
        item["product_name"] = inventory[product_id]["name"]
        item["price"] = inventory[product_id]["price"]
        total_amount += item["price"] * quantity

    # 3. 生成订单号
    now = datetime.now()
    date_str = now.strftime("%Y%m%d")
    # 查找当天最大序号
    today_orders = [o for o in orders if o["order_id"].startswith(f"ORD{date_str}")]
    if today_orders:
        max_seq = max([int(o["order_id"][-5:]) for o in today_orders])
        seq = max_seq + 1
    else:
        seq = 1
    order_id = f"ORD{date_str}{seq:05d}"

    # 4. 创建订单
    order = {
        "order_id": order_id,
        "user_id": user_id,
        "status": "PENDING",
        "items": items,
        "shipping_address": shipping_address,
        "payment": None,
        "shipping": None,
        "total_amount": total_amount,
        "created_at": now.isoformat(),
        "updated_at": now.isoformat()
    }

    # 5. 保存订单
    orders.append(order)
    orders_file.write_text(json.dumps(orders, ensure_ascii=False, indent=2))

    return {
        "success": True,
        "order_id": order_id,
        "status": "PENDING",
        "total_amount": total_amount,
        "message": f"订单创建成功，总金额：{total_amount}元"
    }

if __name__ == "__main__":
    # 测试
    result = execute(
        user_id="USER123",
        items=[{"product_id": "PROD001", "quantity": 1}],
        shipping_address={
            "name": "张三",
            "phone": "13800138000",
            "address": "北京市朝阳区xxx路xxx号"
        }
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))