# MDA订单系统开发备忘录

**日期**: 2025-01-10
**参与者**: guci, Claude

## 一、项目目标

### 最终目标
实现OMG标准的MDA（Model Driven Architecture）：
- 业务人员编写PIM（Platform Independent Model）
- 通过不同的知识文件，自动生成不同技术栈的实现
- 一个PIM → 多个PSM → 多种代码实现

### 技术栈目标
1. **FastAPI版本**（优先实现）
2. **Spring Cloud版本**（后续实现）

## 二、核心理念

### MDA三层转换
```
PIM (业务模型) → PSM (技术模型) → Code (代码实现)
```

### 关键原则
1. **PIM必须技术无关** - 纯业务语言，不包含微服务、API等技术概念
2. **PSM包含技术决策** - 微服务划分、API设计、数据库设计等
3. **Code是具体实现** - 可直接运行的代码

## 三、已完成工作

### 1. 修复了React Agent Minimal的问题
- 解决了ExecutionContext重构后的适配问题
- 修复了知识文件加载bug（knowledge/前缀重复问题）
- 添加了AppendFileTool避免heredoc语法错误
- 将ExecutionContext简化为纯内存操作
- 更新了UML文档

### 2. 修复了mda_workflow.py
- 将Project Manager的模型从grok改为kimi（解决重复set_data问题）
- 统一使用kimi-k2-turbo-preview（除debug_agent使用deepseek）

### 3. 编写了完整的订单系统PIM
- 包含5个业务领域：商品管理、库存管理、客户管理、订单处理、支付结算、配送管理
- 定义了完整的业务流程和业务规则
- 保持纯业务视角，无技术细节

## 四、下一步计划

### Phase 1: 知识文件编写
需要编写两个知识文件：

1. **`pim_to_fastapi_psm.md`** - PIM到PSM的转换规则
   - 业务领域 → 微服务划分
   - 业务实体 → 技术模型
   - 业务流程 → 技术方案

2. **`fastapi_psm_to_code.md`** - PSM到代码的生成规则
   - 技术模型 → SQLAlchemy/Pydantic
   - API设计 → FastAPI路由
   - 项目结构模板

### Phase 2: 实现顺序
1. **单服务验证** - 先实现订单服务一个微服务
2. **双服务协作** - 添加库存服务，实现服务间调用
3. **完整系统** - 逐步添加其他服务

### Phase 3: Agent配置
```python
# PIM → PSM转换Agent
psm_generator = ReactAgentMinimal(
    name="psm_generator",
    description="将PIM转换为FastAPI PSM",
    knowledge_files=["knowledge/pim_to_fastapi_psm.md"]
)

# PSM → Code生成Agent
code_generator = ReactAgentMinimal(
    name="code_generator",
    description="将PSM转换为FastAPI代码",
    knowledge_files=["knowledge/fastapi_psm_to_code.md"]
)
```

## 五、项目结构建议

```
mda-order-system/
├── pim/
│   └── order_system.md          # 业务PIM
├── knowledge/
│   ├── pim_to_fastapi_psm.md   # FastAPI PSM转换规则
│   ├── fastapi_psm_to_code.md  # FastAPI代码生成规则
│   └── pim_to_spring_psm.md    # Spring PSM转换规则（未来）
├── psm/
│   ├── order_system_fastapi.psm.md  # FastAPI PSM
│   └── order_system_spring.psm.md   # Spring PSM（未来）
├── output/
│   ├── fastapi/                # FastAPI生成的代码
│   └── spring/                 # Spring生成的代码（未来）
└── agents/
    └── mda_workflow.py         # MDA工作流Agent
```

## 六、技术决策记录

### 为什么不用事件驱动？
- 先简化目标，做概念验证
- 事件驱动可以在PSM层面添加，不影响PIM

### 为什么要分两个知识文件？
- PIM→PSM：业务到技术的映射，体现架构决策
- PSM→Code：技术到代码的模板，纯粹的代码生成
- 职责分离，易于维护和复用

### 为什么先做FastAPI？
- Python生态简单，Agent容易生成
- FastAPI文档完善，适合验证概念
- 可以快速看到效果

## 七、关键洞察

1. **PIM的纯粹性是MDA成功的关键** - 一旦PIM混入技术概念，就失去了平台无关性
2. **知识文件是技术决策的载体** - 不同的知识文件代表不同的技术选择
3. **Agent只是执行者** - 真正的智慧在知识文件中

## 八、明天的任务

1. 编写`pim_to_fastapi_psm.md`知识文件
2. 编写`fastapi_psm_to_code.md`知识文件  
3. 用Agent生成第一个微服务（订单服务）
4. 验证生成的代码能否运行

---

**备注**: 这个项目如果成功，将证明MDA不仅是理论，而是可以真正实践的软件工程方法。业务人员写PIM，技术人员写知识文件，Agent自动生成代码 - 这就是软件工程的未来。

晚安！💤