# 服务模型 (Service Model)

## 服务接口定义

### OrderService (订单服务)
- **createOrder(customerId, productId)**: 创建订单，返回订单对象
- **getOrders()**: 获取所有订单列表
- **getOrderById(orderId)**: 根据ID获取订单详情
- **updateOrderStatus(orderId, status)**: 更新订单状态

### CustomerService (客户服务)
- **getCustomerById(customerId)**: 根据ID获取客户信息
- **getAllCustomers()**: 获取所有客户列表
- **validateCustomerLevel(customerId)**: 验证客户会员等级
- **addCustomer(name, level)**: 添加新客户，返回生成的customerId
- **updateCustomer(customerId, name, level)**: 更新客户信息

### ProductService (商品服务)
- **getProductById(productId)**: 根据ID获取商品信息
- **checkStock(productId)**: 检查商品库存状态
- **addProduct(name, price, stockStatus)**: 添加新商品，返回生成的productId
- **updateProduct(productId, name, price, stockStatus)**: 更新商品信息
- **stockIn(productId, quantity)**: 商品入库
- **stockOut(productId, quantity)**: 商品出库

### DiscountService (折扣服务)
- **calculateDiscount(price, level)**: 根据会员等级计算折扣价格
- **getDiscountRate(level)**: 获取会员等级对应的折扣率

## 服务实现

### 数据访问层
- 使用JSON文件作为数据存储
- 提供统一的load_json和save_json方法

### 业务逻辑层
- 实现会员折扣计算逻辑
- 实现库存检查逻辑
- 实现订单创建流程

### 工具接口层
- 提供命令行工具order_tool.py
- 支持所有服务的CRUD操作