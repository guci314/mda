# 极简订单系统（自然语言函数版）

## 核心理念
不需要MDA三层转换，直接用自然语言函数实现订单系统。

## 订单系统自然语言函数

### 函数：创建订单
```
接收客户信息和商品列表，
验证库存是否充足，
计算总价（考虑折扣和税费），
生成订单号，
扣减库存，
保存订单到数据库，
发送确认邮件。
```

### 函数：查询订单
```
根据订单号或客户ID查询订单，
返回订单详情包括状态、商品、金额等。
```

### 函数：更新订单状态
```
验证状态转换的合法性（待支付→已支付→已发货→已完成），
更新订单状态，
记录状态变更日志，
触发相应的业务流程（如发货通知）。
```

### 函数：处理退款
```
验证退款条件（时间限制、订单状态），
计算退款金额，
恢复库存，
更新订单状态为已退款，
发起财务退款流程。
```

## 使用方式

```python
from core.react_agent_minimal import ReactAgentMinimal

# 创建订单Agent
order_agent = ReactAgentMinimal(
    work_dir="/tmp/order_system",
    model="gemini-2.5-flash",
    knowledge_files=["knowledge/simple_order_system.md"]
)

# 直接用自然语言调用
result = order_agent.execute("""
为客户张三创建订单：
- 商品：iPhone 15 Pro x1, AirPods Pro x2
- 收货地址：北京市朝阳区xxx
- 使用VIP折扣
""")
```

## 优势
1. **零代码生成**：不需要生成任何代码
2. **灵活适应**：自动处理各种边界情况
3. **易于修改**：直接修改函数描述即可
4. **自然交互**：业务人员可直接使用

## 数据持久化配置

### 数据文件位置
- **订单数据**：`/tmp/simple_order_system/orders.json`
- **库存数据**：`/tmp/simple_order_system/inventory.json`
- **客户数据**：`/tmp/simple_order_system/customers.json`
- **订单序号**：`/tmp/simple_order_system/order_sequence.txt`

### 数据格式
- 所有数据使用JSON格式存储
- 订单号格式：`ORD-YYYYMMDD-XXXXX`（日期+序号）
- 时间戳使用ISO 8601格式

## 这才是真正的MDA
Model = 自然语言描述
Driven = LLM驱动执行
Architecture = 知识文件组织

不是Model → Code，而是Model → Execution！