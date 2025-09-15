# 库存服务知识库

## 服务职责
库存服务负责管理商品库存，包括库存查询、扣减、补充等操作。

## 自然语言函数

### 函数：检查库存
```
接收商品列表（包含商品ID和需求数量），
从 /tmp/microservices/inventory/stock.json 读取库存数据，
检查每个商品的库存是否充足，
返回检查结果：
- 如果全部充足：返回"库存充足"和具体库存数
- 如果不足：返回"库存不足"和缺货商品列表
```

### 函数：扣减库存
```
接收商品列表和数量，
检查库存是否充足，
如果充足则扣减相应数量，
更新 /tmp/microservices/inventory/stock.json，
记录库存变动到 /tmp/microservices/inventory/stock_log.json，
返回扣减结果。
```

### 函数：补充库存
```
接收商品ID和补充数量，
增加对应商品的库存，
更新库存文件，
记录补充日志，
返回新的库存数量。
```

### 函数：查询库存
```
接收商品ID列表（可选，为空则查询所有），
从库存文件读取数据，
返回商品的当前库存信息。
```

### 函数：设置库存预警
```
接收商品ID和预警阈值，
当库存低于阈值时标记为需要补货，
保存预警设置到 /tmp/microservices/inventory/alerts.json。
```

## 与其他服务的协作

### 响应订单服务请求
```
当收到订单服务的库存检查请求时：
1. 解析商品列表
2. 调用 检查库存 函数
3. 返回库存状态给订单服务
```

### 响应产品服务请求
```
当收到产品服务的库存查询请求时：
1. 调用 查询库存 函数
2. 返回库存数据给产品服务
```

## 数据存储位置
- 库存数据：`/tmp/microservices/inventory/stock.json`
- 库存日志：`/tmp/microservices/inventory/stock_log.json`
- 预警设置：`/tmp/microservices/inventory/alerts.json`

## 库存数据格式
```json
{
  "PROD001": {
    "name": "iPhone 15 Pro",
    "stock": 50,
    "reserved": 0,
    "available": 50,
    "alert_threshold": 10
  },
  "PROD002": {
    "name": "AirPods Pro",
    "stock": 100,
    "reserved": 5,
    "available": 95,
    "alert_threshold": 20
  }
}
```

## 业务规则
1. 库存不能为负数
2. 扣减时需要检查可用库存（available = stock - reserved）
3. 库存低于预警阈值时需要提醒
4. 所有库存变动必须记录日志
5. 支持批量操作（一次扣减多个商品）