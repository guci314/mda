# 电商订单处理领域模型

## 核心实体

### 1. Customer（客户）
**属性：**
- customer_id: string (唯一标识)
- name: string (客户姓名)
- level: enum (VIP, 普通会员, 非会员)

**职责：**
- 提供会员等级信息
- 关联订单历史

### 2. Product（商品）
**属性：**
- product_id: string (唯一标识)
- price: number (商品原价)
- stock_status: string (库存状态：充足/不足)

**职责：**
- 提供商品信息和价格
- 维护库存状态

### 3. Order（订单）
**属性：**
- order_id: string (唯一订单号，格式：ORD + 时间戳 + 随机数)
- customer_id: string (关联客户)
- product_id: string (关联商品)
- original_price: number (商品原价)
- discounted_price: number (折扣后价格)
- stock_status: string (订单时的库存状态)
- order_status: string (订单状态：已创建/失败)

**职责：**
- 记录订单信息
- 计算折扣价格
- 验证库存

## 实体关系

```
Customer --1:N--> Order
Order --1:1--> Product
```

- 一个客户可以有多个订单
- 一个订单对应一个商品（简化模型）
- 商品独立存在，可被多个订单引用

## 业务规则

### 会员等级折扣
- VIP客户：享受8折优惠 (discounted_price = original_price * 0.8)
- 普通会员：享受9折优惠 (discounted_price = original_price * 0.9)
- 非会员：原价购买 (discounted_price = original_price)

### 库存检查
- 创建订单前必须检查商品库存
- 如果库存不足，拒绝创建订单 (order_status = "失败")
- 库存充足时才生成订单号并创建订单

### 订单号生成
- 格式：ORD + 时间戳 + 随机数
- 保证唯一性

### 价格计算
- 基于会员等级自动计算折扣后价格
- 记录原价和折扣价

## 数据持久化
- 使用 JSON 文件 (orders.json) 存储订单列表
- 每个订单以 JSON 对象形式存储
- 支持查询和更新操作

## 扩展可能性
- 支持订单包含多个商品（OrderItem 实体）
- 添加支付状态和物流信息
- 实现库存扣减逻辑