#!/usr/bin/env python3
"""
订单系统 - 外部工具
独立的Python程序，通过命令行接口与Agent交互
"""

import sqlite3
import json
import sys
from datetime import datetime
from pathlib import Path

class OrderSystem:
    """订单管理外部工具"""
    
    def __init__(self, db_path="/tmp/simple_order_system/orders.db"):
        """初始化数据库"""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self._init_tables()
    
    def _init_tables(self):
        """创建表结构"""
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                order_id TEXT PRIMARY KEY,
                customer_name TEXT NOT NULL,
                customer_phone TEXT,
                items TEXT NOT NULL,
                total_amount REAL NOT NULL,
                discount REAL DEFAULT 0,
                status TEXT DEFAULT 'pending',
                created_at TEXT NOT NULL,
                updated_at TEXT
            )
        """)
        self.conn.commit()
    
    def create_order(self, customer_name, customer_phone, items, discount=0):
        """创建订单"""
        order_id = f"ORD-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        total_amount = sum(item['price'] * item.get('quantity', 1) for item in items)
        final_amount = total_amount * (1 - discount)
        
        self.conn.execute("""
            INSERT INTO orders (order_id, customer_name, customer_phone, items, 
                              total_amount, discount, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (order_id, customer_name, customer_phone, json.dumps(items), 
              final_amount, discount, datetime.now().isoformat()))
        self.conn.commit()
        
        return {
            "order_id": order_id,
            "customer": customer_name,
            "total": final_amount,
            "status": "created"
        }
    
    def query_orders(self, customer_name=None, status=None):
        """查询订单"""
        query = "SELECT * FROM orders WHERE 1=1"
        params = []
        
        if customer_name:
            query += " AND customer_name = ?"
            params.append(customer_name)
        if status:
            query += " AND status = ?"
            params.append(status)
        
        query += " ORDER BY created_at DESC"
        
        cursor = self.conn.execute(query, params)
        orders = []
        for row in cursor:
            orders.append({
                "order_id": row["order_id"],
                "customer": row["customer_name"],
                "items": json.loads(row["items"]),
                "total": row["total_amount"],
                "status": row["status"],
                "created": row["created_at"]
            })
        return orders
    
    def update_status(self, order_id, new_status):
        """更新订单状态"""
        valid_transitions = {
            "pending": ["paid", "cancelled"],
            "paid": ["shipped", "refunded"],
            "shipped": ["completed", "returned"],
        }
        
        cursor = self.conn.execute("SELECT status FROM orders WHERE order_id = ?", (order_id,))
        row = cursor.fetchone()
        if not row:
            return {"error": f"订单{order_id}不存在"}
        
        current_status = row["status"]
        if new_status not in valid_transitions.get(current_status, []):
            return {"error": f"无法从{current_status}转换到{new_status}"}
        
        self.conn.execute("""
            UPDATE orders SET status = ?, updated_at = ?
            WHERE order_id = ?
        """, (new_status, datetime.now().isoformat(), order_id))
        self.conn.commit()
        
        return {"order_id": order_id, "status": new_status, "updated": True}

def main():
    """命令行接口"""
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: order_system.py <command> [args...]"}))
        sys.exit(1)
    
    command = sys.argv[1]
    order_system = OrderSystem()
    
    try:
        if command == "create":
            # order_system.py create "张三" "13800138000" '[{"name":"MacBook","price":15999}]' 0.2
            result = order_system.create_order(
                sys.argv[2], sys.argv[3], 
                json.loads(sys.argv[4]), 
                float(sys.argv[5]) if len(sys.argv) > 5 else 0
            )
        elif command == "query":
            # order_system.py query [customer_name] [status]
            result = order_system.query_orders(
                sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] != "all" else None,
                sys.argv[3] if len(sys.argv) > 3 else None
            )
        elif command == "update_status":
            # order_system.py update_status <order_id> <new_status>
            result = order_system.update_status(sys.argv[2], sys.argv[3])
        else:
            result = {"error": f"Unknown command: {command}"}
        
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)

if __name__ == "__main__":
    main()