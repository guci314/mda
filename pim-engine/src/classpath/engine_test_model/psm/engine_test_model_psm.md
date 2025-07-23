# 引擎测试模型 PSM (FastAPI)

## 技术架构说明

本 PSM 基于 FastAPI 框架构建，采用 RESTful API 设计风格。使用 Pydantic v2 进行数据验证和序列化，SQLAlchemy 2.0 作为 ORM 与数据库交互。项目结构清晰，易于维护和扩展。

## 数据模型设计

### Product

```python
from sqlalchemy import Column, Integer, String, Numeric, Identity
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, Identity(), primary_key=True)
    name = Column(String(100), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    stock = Column(Integer, default=0)
```

- **id**: 整数, 主键, 自增
- **name**: 字符串, 必填, 最大长度100
- **price**: 小数, 必填, 大于0
- **stock**: 整数, 默认0

### Order

```python
from sqlalchemy import Column, Integer, String, Numeric, DateTime, Enum, ForeignKey, Identity
from sqlalchemy.orm import relationship
import datetime
import enum

class OrderStatus(enum.Enum):
    pending = "pending"
    paid = "paid"
    shipped = "shipped"
    completed = "completed"

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, Identity(), primary_key=True)
    customerName = Column(String, nullable=False)
    totalAmount = Column(Numeric(10, 2), nullable=False)
    status = Column(Enum(OrderStatus), default=OrderStatus.pending)
    createdAt = Column(DateTime, default=datetime.datetime.utcnow)

    order_items = relationship("OrderItem", back_populates="order")
```

- **id**: 整数, 主键, 自增
- **customerName**: 字符串, 必填
- **totalAmount**: 小数, 必填
- **status**: 枚举[pending, paid, shipped, completed]
- **createdAt**: 日期时间, 必填

### OrderItem

```python
from sqlalchemy import Column, Integer, Numeric, ForeignKey, Identity
from sqlalchemy.orm import relationship

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, Identity(), primary_key=True)
    orderId = Column(Integer, ForeignKey("orders.id"))
    productId = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)

    order = relationship("Order", back_populates="order_items")
    product = relationship("Product")
```

- **id**: 整数, 主键, 自增
- **orderId**: 整数, 外键(Order)
- **productId**: 整数, 外键(Product)
- **quantity**: 整数, 必填, 大于0
- **price**: 小数, 必填

## API 接口设计

### ProductService

1.  **createProduct(productData)**

    -   路由: `POST /products/`
    -   请求格式: JSON, 包含 Product 数据
    -   响应格式: JSON, 创建的 Product 对象
    -   状态码: 201 (Created)

    ```python
    from fastapi import FastAPI, Depends, HTTPException
    from pydantic import BaseModel
    from sqlalchemy.orm import Session
    from . import models, database

    app = FastAPI()

    # Pydantic model for Product
    class ProductCreate(BaseModel):
        name: str
        price: float
        stock: int = 0

    @app.post("/products/", response_model=ProductCreate, status_code=201)
    def create_product(product: ProductCreate, db: Session = Depends(database.get_db)):
        db_product = models.Product(**product.dict())
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        return db_product
    ```

2.  **getProduct(id)**

    -   路由: `GET /products/{id}`
    -   请求格式: 无
    -   响应格式: JSON, Product 对象
    -   状态码: 200 (OK), 404 (Not Found)

    ```python
    @app.get("/products/{id}", response_model=ProductCreate)
    def read_product(id: int, db: Session = Depends(database.get_db)):
        db_product = db.query(models.Product).filter(models.Product.id == id).first()
        if db_product is None:
            raise HTTPException(status_code=404, detail="Product not found")
        return db_product
    ```

3.  **updateStock(id, quantity)**

    -   路由: `PATCH /products/{id}/stock`
    -   请求格式: JSON, 包含 quantity 字段
    -   响应格式: JSON, 更新后的 Product 对象
    -   状态码: 200 (OK), 404 (Not Found)

    ```python
    class StockUpdate(BaseModel):
        quantity: int

    @app.patch("/products/{id}/stock", response_model=ProductCreate)
    def update_product_stock(id: int, stock_update: StockUpdate, db: Session = Depends(database.get_db)):
        db_product = db.query(models.Product).filter(models.Product.id == id).first()
        if db_product is None:
            raise HTTPException(status_code=404, detail="Product not found")
        db_product.stock += stock_update.quantity
        db.commit()
        db.refresh(db_product)
        return db_product
    ```

### OrderService

1.  **createOrder(orderData)**

    -   路由: `POST /orders/`
    -   请求格式: JSON, 包含 Order 数据和 OrderItem 列表
    -   响应格式: JSON, 创建的 Order 对象及其 OrderItems
    -   状态码: 201 (Created)

2.  **getOrder(id)**

    -   路由: `GET /orders/{id}`
    -   请求格式: 无
    -   响应格式: JSON, Order 对象及其 OrderItems
    -   状态码: 200 (OK), 404 (Not Found)

## 业务逻辑实现方案

### 服务层设计

-   **ProductService**: 负责 Product 相关的业务逻辑，包括创建、查询、更新库存等。
-   **OrderService**: 负责 Order 相关的业务逻辑，包括创建订单、查询订单等。在创建订单时，需要调用 ProductService 检查库存，并更新产品库存。

## 项目结构说明

```
engine_test_model/
├── app/
│   ├── __init__.py
│   ├── database.py  # 数据库连接和配置
│   ├── models.py      # SQLAlchemy 模型定义
│   ├── schemas.py     # Pydantic 数据模型
│   ├── services.py    # 业务逻辑服务
│   ├── api.py         # API 路由定义
│   └── main.py        # FastAPI 应用入口
├── tests/
│   ├── __init__.py
│   └── test_api.py    # API 接口测试
├── README.md
├── poetry.lock
└── pyproject.toml
```

## 技术栈和依赖列表

-   FastAPI
-   SQLAlchemy 2.0
-   Pydantic v2
-   PostgreSQL 或 SQLite
-   pytest
-   Poetry (依赖管理)

**依赖安装 (使用 Poetry):**

```bash
poetry install
```

**测试 (使用 pytest):**

```bash
pytest tests/test_api.py
```