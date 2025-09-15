# 外部工具使用指南

## 核心理念
- **Tool（身体）**：基础能力，保持稳定（ExecuteCommand, WriteFile等）
- **External Tools（外部工具）**：独立进化的Python程序
- **Knowledge（知识）**：描述如何使用外部工具

## 架构类比
```
人类文明                    Agent系统
---------                  -----------
大脑思考            →      Agent + LLM
身体能力（手、眼）   →      Tool（内置工具）
外部工具（锤子、车） →      External Tools（Python程序）
使用知识（说明书）   →      Knowledge Files
```

## 订单系统外部工具

### 工具位置
`/home/guci/aiProjects/mda/pim-compiler/react_is_all_you_need/external_tools/order_system.py`

### 使用方式

#### 函数：创建订单（使用外部工具）
```
调用外部工具创建订单：
python /home/guci/aiProjects/mda/pim-compiler/react_is_all_you_need/external_tools/order_system.py create "{客户名}" "{电话}" '{商品JSON}' {折扣}

示例：
python order_system.py create "张三" "13800138000" '[{"name":"MacBook Pro","price":15999,"quantity":1}]' 0.2
```

#### 函数：查询订单（使用外部工具）
```
调用外部工具查询订单：
python order_system.py query [客户名|all] [状态]

示例：
- 查询所有：python order_system.py query
- 查询张三：python order_system.py query "张三"
- 查询待支付：python order_system.py query all pending
```

#### 函数：更新订单状态（使用外部工具）
```
调用外部工具更新状态：
python order_system.py update_status {订单号} {新状态}

状态流转规则：
pending → paid/cancelled
paid → shipped/refunded
shipped → completed/returned

示例：
python order_system.py update_status "ORD-20250115-143022" "paid"
```

## 设计原则

### 1. 外部工具独立性
- 外部工具是完整的Python程序
- 有自己的数据存储（SQLite）
- 通过命令行接口交互
- 可以独立测试和进化

### 2. Tool的稳定性
- ExecuteCommand不变（执行外部工具）
- WriteFile不变（创建外部工具）
- ReadFile不变（读取结果）

### 3. 知识的进化
- 知识文件描述工具的使用方法
- 随着外部工具更新，知识文件也更新
- 知识包含最佳实践和经验

## 进化模式

1. **身体不进化**：Tool保持简单稳定
2. **工具进化**：创建新的外部工具，改进现有工具
3. **知识进化**：更新使用方法，积累经验

## 为什么这样设计？

1. **关注点分离**：Agent专注理解，工具专注执行
2. **独立进化**：外部工具可以用任何语言实现
3. **可测试性**：外部工具可以独立测试
4. **可替换性**：可以换用不同的订单系统实现
5. **符合人类认知**：就像人类使用锤子一样自然

## 实践示例

当Agent收到"创建订单"任务时：
1. 理解任务意图（Agent + LLM）
2. 查找知识文件了解如何操作（Knowledge）
3. 使用ExecuteCommand调用外部工具（Tool）
4. 外部工具执行具体操作（External Tool）
5. 返回结果给用户

这就像人类：
1. 大脑理解"需要钉钉子"
2. 知识告诉我们"用锤子"
3. 手去拿锤子（Tool）
4. 锤子钉钉子（External Tool）
5. 完成任务