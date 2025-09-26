# 领域模型 (Domain Model)

## 实体定义

### Customer (客户)
- **customer_id**: 客户ID (字符串，如"CUST001")
- **name**: 客户姓名 (字符串，如"张三")
- **level**: 会员等级 (枚举："VIP"、"普通会员"、"非会员")

### Product (商品)
- **product_id**: 商品ID (字符串，如"PROD001")
- **name**: 商品名称 (字符串)
- **price**: 商品价格 (整数，单位：元)
- **stock_status**: 库存状态 (枚举："充足"、"不足")

### Order (订单)
- **order_id**: 订单ID (字符串，如"ORD20241220123456ABC")
- **customer_id**: 客户ID (引用Customer)
- **product_id**: 商品ID (引用Product)
- **original_price**: 原价 (整数)
- **discounted_price**: 折扣后价格 (整数)
- **order_status**: 订单状态 (枚举："创建成功"、"库存不足"、"客户不存在")
- **created_at**: 创建时间 (时间戳)

## 业务规则

### 会员折扣规则
- VIP客户：8折优惠
- 普通会员：9折优惠  
- 非会员：原价

### 库存检查规则
- 创建订单前必须检查商品库存状态
- 只有库存"充足"的商品才能创建订单

### 订单号生成规则
- 格式：ORD + 时间戳 + 随机后缀
- 确保订单号唯一性

## 数据持久化
- 使用JSON文件存储：customers.json, products.json, orders.json
- 文件路径：工作目录下