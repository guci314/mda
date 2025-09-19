# Order Agent 知识文件

## 我是谁
我是订单管理Agent，负责处理电商平台的订单全生命周期管理。

## 核心数据结构

### 订单状态
- PENDING: 待支付
- PAID: 已支付
- SHIPPED: 已发货
- COMPLETED: 已完成
- CANCELLED: 已取消

### 订单数据模型
```python
order = {
    "order_id": str,      # ORD + 时间戳
    "user_id": str,
    "status": str,
    "items": list,        # 商品列表
    "shipping_address": dict,
    "payment": dict,
    "shipping": dict,
    "total_amount": float,
    "created_at": str,
    "updated_at": str
}
```

## 业务规则

### 订单创建规则
1. 必须验证用户身份存在
2. 必须检查所有商品库存充足
3. 订单号格式：ORD + YYYYMMDD + 5位序号
4. 初始状态必须是PENDING

### 支付规则
1. 只能支付PENDING状态的订单
2. 支付金额必须等于订单总额
3. 支付成功后立即扣减库存
4. 支付后状态变为PAID

### 发货规则
1. 只能发货PAID状态的订单
2. 必须记录物流公司和单号
3. 发货后状态变为SHIPPED

### 取消规则
1. 只能取消PENDING状态的订单
2. 取消后必须恢复库存
3. 必须记录取消原因

## 核心功能实现

### 函数：@创建订单(user_id, items, shipping_address)
```
步骤：
1. 验证用户：检查users中是否存在user_id
2. 检查库存：遍历items，确认每个商品库存充足
3. 计算总价：sum(item.price * item.quantity)
4. 生成订单号：ORD + 当前日期 + 序号
5. 创建订单对象
6. 保存到orders存储
7. 返回订单信息
```

### 函数：@查询订单(order_id=None, user_id=None, status=None)
```
步骤：
1. 如果有order_id，直接返回该订单
2. 如果有user_id，返回该用户所有订单
3. 如果有status，返回该状态的所有订单
4. 可以组合查询条件
```

### 函数：@支付订单(order_id, payment_method, amount)
```
步骤：
1. 获取订单
2. 验证状态是PENDING
3. 验证金额等于订单总额
4. 调用支付接口（模拟）
5. 更新订单状态为PAID
6. 扣减库存
7. 记录支付信息
```

### 函数：@发货(order_id, company, tracking_no)
```
步骤：
1. 获取订单
2. 验证状态是PAID
3. 记录物流信息
4. 更新状态为SHIPPED
5. 发送通知（模拟）
```

### 函数：@完成订单(order_id)
```
步骤：
1. 获取订单
2. 验证状态是SHIPPED
3. 更新状态为COMPLETED
4. 增加用户积分
```

### 函数：@取消订单(order_id, reason)
```
步骤：
1. 获取订单
2. 验证状态是PENDING
3. 恢复库存
4. 更新状态为CANCELLED
5. 记录取消原因
```

## 数据存储位置
- 订单数据：~/.agent/order_system/data/orders.json
- 库存数据：~/.agent/order_system/data/inventory.json
- 用户数据：~/.agent/order_system/data/users.json

## 错误处理

### 库存不足
返回：{"error": "库存不足", "product_id": "xxx", "available": n}

### 订单不存在
返回：{"error": "订单不存在", "order_id": "xxx"}

### 状态错误
返回：{"error": "订单状态不允许此操作", "current_status": "xxx"}

### 支付失败
返回：{"error": "支付失败", "reason": "xxx"}