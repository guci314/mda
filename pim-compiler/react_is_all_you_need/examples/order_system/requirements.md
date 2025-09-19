# 订单系统需求文档

## 1. 业务背景
一个小型电商平台需要订单管理系统，处理用户下单、支付、发货、售后等流程。

## 2. 功能需求

### 2.1 订单创建
- **输入**：用户ID、商品列表、收货地址
- **处理**：
  - 验证用户身份
  - 检查商品库存
  - 计算订单总价（商品价格 + 运费 - 优惠）
  - 生成唯一订单号
- **输出**：订单对象（订单号、状态、总价、创建时间）

### 2.2 订单查询
- **按订单号查询**：返回订单详情
- **按用户查询**：返回用户的所有订单列表
- **按状态查询**：返回特定状态的订单（待支付、已支付、已发货、已完成）

### 2.3 订单支付
- **输入**：订单号、支付方式、支付金额
- **处理**：
  - 验证订单状态（必须是待支付）
  - 验证支付金额
  - 调用支付接口（模拟）
  - 更新订单状态为已支付
  - 扣减库存
- **输出**：支付结果

### 2.4 订单发货
- **输入**：订单号、物流公司、物流单号
- **处理**：
  - 验证订单状态（必须是已支付）
  - 记录物流信息
  - 更新订单状态为已发货
  - 发送通知给用户
- **输出**：发货结果

### 2.5 订单完成
- **输入**：订单号
- **处理**：
  - 验证订单状态（必须是已发货）
  - 更新订单状态为已完成
  - 触发用户积分增加
- **输出**：完成结果

### 2.6 订单取消
- **输入**：订单号、取消原因
- **处理**：
  - 验证订单状态（只能取消待支付订单）
  - 恢复库存
  - 更新订单状态为已取消
  - 记录取消原因
- **输出**：取消结果

## 3. 非功能需求

### 3.1 性能要求
- 订单创建：< 500ms
- 订单查询：< 100ms
- 支付处理：< 2s
- 并发处理：支持100个并发请求

### 3.2 可靠性要求
- 订单数据不能丢失
- 支付必须保证一致性
- 库存扣减必须准确

## 4. 数据模型

### 订单（Order）
```json
{
  "order_id": "ORD20241117001",
  "user_id": "USER123",
  "status": "PENDING|PAID|SHIPPED|COMPLETED|CANCELLED",
  "items": [
    {
      "product_id": "PROD001",
      "product_name": "iPhone 15",
      "quantity": 1,
      "price": 6999.00
    }
  ],
  "shipping_address": {
    "name": "张三",
    "phone": "13800138000",
    "address": "北京市朝阳区xxx路xxx号"
  },
  "payment": {
    "method": "ALIPAY|WECHAT|CARD",
    "amount": 6999.00,
    "paid_at": "2024-11-17T10:30:00Z"
  },
  "shipping": {
    "company": "顺丰",
    "tracking_no": "SF1234567890",
    "shipped_at": "2024-11-17T14:00:00Z"
  },
  "total_amount": 6999.00,
  "created_at": "2024-11-17T10:00:00Z",
  "updated_at": "2024-11-17T14:00:00Z"
}
```

### 库存（Inventory）
```json
{
  "product_id": "PROD001",
  "available": 100,
  "reserved": 10,
  "sold": 50
}
```

### 用户（User）
```json
{
  "user_id": "USER123",
  "name": "张三",
  "phone": "13800138000",
  "addresses": [...],
  "points": 1000
}
```

## 5. 接口规范

### 5.1 创建订单
```http
POST /orders
{
  "user_id": "USER123",
  "items": [
    {"product_id": "PROD001", "quantity": 1}
  ],
  "shipping_address": {...}
}

Response:
{
  "order_id": "ORD20241117001",
  "status": "PENDING",
  "total_amount": 6999.00
}
```

### 5.2 查询订单
```http
GET /orders/{order_id}
GET /orders?user_id=USER123
GET /orders?status=PENDING
```

### 5.3 支付订单
```http
POST /orders/{order_id}/pay
{
  "method": "ALIPAY",
  "amount": 6999.00
}
```

### 5.4 发货
```http
POST /orders/{order_id}/ship
{
  "company": "顺丰",
  "tracking_no": "SF1234567890"
}
```

### 5.5 完成订单
```http
POST /orders/{order_id}/complete
```

### 5.6 取消订单
```http
POST /orders/{order_id}/cancel
{
  "reason": "不想要了"
}
```

## 6. 测试场景

### 场景1：正常购物流程
1. 用户创建订单
2. 用户支付订单
3. 商家发货
4. 用户确认收货
5. 订单完成

### 场景2：取消订单流程
1. 用户创建订单
2. 用户取消订单
3. 库存恢复

### 场景3：库存不足
1. 用户创建订单
2. 系统检查库存不足
3. 返回错误提示

### 场景4：重复支付
1. 用户创建订单
2. 用户第一次支付成功
3. 用户尝试重复支付
4. 系统拒绝重复支付

## 7. 实施计划

### Phase 1: ADA实现（Agent建模）
1. 创建OrderAgent作为可执行模型
2. 用自然语言定义业务逻辑
3. 直接执行验证功能正确性
4. 客户确认满意度

### Phase 2: 编译到传统框架（如需要）
1. 将OrderAgent编译到FastAPI
2. 生成RESTful API
3. 部署到传统服务器

### Phase 3: AIA升级（Agent即系统）
1. OrderAgent直接作为生产系统
2. 高频操作创建External Tools
3. 80%请求走快速路径（JSON→Tool）
4. 20%请求走智能路径（NL→Agent）

## 8. 成功标准
- 所有功能测试通过
- 性能满足要求
- 客户试用满意
- 可以处理异常情况