# 电商订单处理服务模型

## 核心服务

### 1. OrderService（订单服务）
**职责：**
- 创建新订单
- 查询订单列表
- 更新订单状态
- 验证订单完整性

**接口方法：**
- `createOrder(customerId, productId)` - 创建订单，返回订单详情或错误
- `getOrders()` - 获取所有订单列表
- `getOrderById(orderId)` - 根据ID获取订单
- `updateOrderStatus(orderId, status)` - 更新订单状态

**依赖：**
- CustomerService（获取客户信息）
- ProductService（获取商品信息和库存）
- DiscountService（计算折扣价格）

### 2. CustomerService（客户服务）
**职责：**
- 管理客户信息
- 验证客户等级
- 提供客户查询功能

**接口方法：**
- `getCustomerById(customerId)` - 根据ID获取客户信息
- `validateCustomerLevel(customerId)` - 验证客户等级，返回折扣率
- `addCustomer(customerId, name, level)` - 添加新客户
- `updateCustomer(customerId, level)` - 修改客户等级
- `updateCustomerLevel(customerId, level)` - 更新客户等级（别名）

**数据源：**
- customers.json

### 3. ProductService（商品服务）
**职责：**
- 管理商品信息
- 检查库存状态
- 提供商品查询功能
- 处理商品入库和出库

**接口方法：**
- `getProductById(productId)` - 根据ID获取商品信息
- `checkStock(productId)` - 检查商品库存，返回true/false
- `addProduct(productData)` - 添加新商品
- `updateProduct(productId, productData)` - 修改商品信息
- `updateStock(productId, status)` - 更新库存状态
- `stockIn(productId)` - 商品入库（设置为充足）
- `stockOut(productId)` - 商品出库（设置为不足）

**数据源：**
- products.json

### 4. DiscountService（折扣服务）
**职责：**
- 计算会员折扣
- 应用促销规则
- 返回最终价格

**接口方法：**
- `calculateDiscount(originalPrice, customerLevel)` - 计算折扣价格
- `getDiscountRate(customerLevel)` - 获取折扣率（0.8, 0.9, 1.0）

**业务规则：**
- VIP: 0.8
- 普通会员: 0.9
- 非会员: 1.0

## 服务交互流程

### 订单创建流程
```
OrderService.createOrder(customerId, productId)
  ↓
CustomerService.getCustomerById(customerId) → 获取客户等级
  ↓
ProductService.getProductById(productId) → 获取商品价格和库存
  ↓
ProductService.checkStock(productId) → 验证库存充足
  ↓
DiscountService.calculateDiscount(price, level) → 计算折扣价格
  ↓
生成订单号，保存到orders.json
```

### 查询订单流程
```
OrderService.getOrders()
  ↓
读取orders.json
  ↓
为每个订单调用CustomerService和ProductService获取详细信息
  ↓
返回完整订单列表
```

## 数据访问层
- **Repository模式**：每个服务有对应的Repository处理JSON文件读写
- **OrderRepository**：orders.json
- **CustomerRepository**：customers.json  
- **ProductRepository**：products.json

## 异常处理
- **StockInsufficientException**：库存不足
- **CustomerNotFoundException**：客户不存在
- **ProductNotFoundException**：商品不存在
- **InvalidOrderException**：订单数据无效

## 扩展点
- 添加支付服务 (PaymentService)
- 添加物流服务 (ShippingService)
- 添加通知服务 (NotificationService)
- 支持批量订单处理