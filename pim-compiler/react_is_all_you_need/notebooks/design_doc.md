# 设计文档 (Design Document)

## 领域模型 (Domain Model)

### 实体定义

#### Customer (客户)
- **customer_id**: 客户ID (字符串，如"CUST001")
- **name**: 客户姓名 (字符串，如"张三")
- **level**: 会员等级 (枚举："VIP"、"普通会员"、"非会员")

#### Product (商品)
- **product_id**: 商品ID (字符串，如"PROD001")
- **name**: 商品名称 (字符串)
- **price**: 商品价格 (整数，单位：元)
- **stock_status**: 库存状态 (枚举："充足"、"不足")

#### Order (订单)
- **order_id**: 订单ID (字符串，如"ORD20241220123456ABC")
- **customer_id**: 客户ID (引用Customer)
- **product_id**: 商品ID (引用Product)
- **original_price**: 原价 (整数)
- **discounted_price**: 折扣后价格 (整数)
- **order_status**: 订单状态 (枚举："创建成功"、"库存不足"、"客户不存在")
- **created_at**: 创建时间 (时间戳)

### 业务规则

#### 会员折扣规则
- VIP客户：8折优惠
- 普通会员：9折优惠
- 非会员：原价

#### 库存检查规则
- 创建订单前必须检查商品库存状态
- 只有库存"充足"的商品才能创建订单

#### 订单号生成规则
- 格式：ORD + 时间戳 + 随机后缀
- 确保订单号唯一性

### 数据持久化
- 使用JSON文件存储：customers.json, products.json, orders.json
- 文件路径：工作目录下

## 服务模型 (Service Model)

### 服务接口定义

#### OrderService (订单服务)
- **createOrder(customerId, productId)**: 创建订单，返回订单对象
- **getOrders()**: 获取所有订单列表
- **getOrderById(orderId)**: 根据ID获取订单详情
- **updateOrderStatus(orderId, status)**: 更新订单状态

#### CustomerService (客户服务)
- **getCustomerById(customerId)**: 根据ID获取客户信息
- **getAllCustomers()**: 获取所有客户列表
- **validateCustomerLevel(customerId)**: 验证客户会员等级
- **addCustomer(name, level)**: 添加新客户，返回生成的customerId
- **updateCustomer(customerId, name, level)**: 更新客户信息

#### ProductService (商品服务)
- **getProductById(productId)**: 根据ID获取商品信息
- **checkStock(productId)**: 检查商品库存状态
- **addProduct(name, price, stockStatus)**: 添加新商品，返回生成的productId
- **updateProduct(productId, name, price, stockStatus)**: 更新商品信息
- **stockIn(productId, quantity)**: 商品入库
- **stockOut(productId, quantity)**: 商品出库

#### DiscountService (折扣服务)
- **calculateDiscount(price, level)**: 根据会员等级计算折扣价格
- **getDiscountRate(level)**: 获取会员等级对应的折扣率

### 服务实现

#### 数据访问层
- 使用JSON文件作为数据存储
- 提供统一的load_json和save_json方法

#### 业务逻辑层
- 实现会员折扣计算逻辑
- 实现库存检查逻辑
- 实现订单创建流程

#### 工具接口层
- 提供命令行工具order_tool.py
- 支持所有服务的CRUD操作