# PIM → FastAPI PSM 转换规则

## 微服务划分策略

### 服务划分原则
1. **按业务领域划分**：一个业务领域 = 一个微服务
2. **高内聚低耦合**：相关功能放在同一服务
3. **独立部署**：每个服务可独立开发部署

### 具体服务划分
1. **product-service** - 商品管理、分类管理
2. **inventory-service** - 库存管理、库存操作
3. **customer-service** - 客户信息管理
4. **order-service** - 订单处理、订单状态管理
5. **payment-service** - 支付处理、交易记录
6. **delivery-service** - 配送管理、物流跟踪

## 技术模型映射

### 数据库设计
- 每个服务使用独立的PostgreSQL数据库
- 表名使用复数形式：products, orders, customers
- 包含标准字段：id, created_at, updated_at

### API设计规范
- RESTful风格，资源导向
- URL格式：/api/{resource}/{id}
- HTTP方法：GET(查询), POST(创建), PUT(更新), DELETE(删除)

### 服务间通信
- 使用HTTP REST调用
- 服务发现通过Consul
- 熔断机制使用Hystrix

## 具体转换规则

### 商品领域 → product-service
```yaml
service: product-service
database:
  tables:
    products:
      columns:
        id: uuid primary key
        name: varchar(255)
        description: text
        price: decimal(10,2)
        category_id: uuid
        status: varchar(20)
        created_at: timestamp
        updated_at: timestamp

apis:
  - path: /api/products
    methods: [GET, POST]
  - path: /api/products/{id}
    methods: [GET, PUT, DELETE]
```

### 订单领域 → order-service
```yaml
service: order-service
database:
  tables:
    orders:
      columns:
        id: uuid primary key
        customer_id: uuid
        total_amount: decimal(10,2)
        status: varchar(20)
        created_at: timestamp
        updated_at: timestamp
    order_items:
      columns:
        id: uuid primary key
        order_id: uuid
        product_id: uuid
        quantity: integer
        unit_price: decimal(10,2)

apis:
  - path: /api/orders
    methods: [GET, POST]
  - path: /api/orders/{id}
    methods: [GET, PUT, DELETE]
  - path: /api/orders/{id}/items
    methods: [GET, POST]
```

## 异常处理
- 统一错误码规范
- 全局异常处理器
- 日志记录和监控