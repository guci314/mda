# 🛒 MDA订单系统

基于Model Driven Architecture (MDA) 和Agent Builder实现的订单管理系统。

## 🏗️ 架构设计

### MDA三层转换
```
PIM (业务模型) → PSM (技术模型) → Code (代码实现)
```

### 微服务划分
1. **product-service** - 商品管理
2. **inventory-service** - 库存管理  
3. **customer-service** - 客户管理
4. **order-service** - 订单处理
5. **payment-service** - 支付结算
6. **delivery-service** - 配送管理

## 📁 项目结构

```
mda-order-system/
├── pim/                    # 平台无关模型
│   └── order_system.md     # 业务模型定义
├── knowledge/              # 知识文件
│   ├── mda_concepts.md     # MDA核心概念
│   ├── pim_to_fastapi_psm.md    # PIM→PSM转换规则
│   └── fastapi_psm_to_code.md   # PSM→代码生成规则
├── psm/                    # 平台特定模型
│   └── order_system_fastapi.psm.md  # FastAPI技术模型
├── output/                 # 生成的代码
│   └── fastapi/
│       ├── product-service/
│       ├── order-service/
│       └── ...
├── agents/                 # Agent定义
│   └── mda_workflow.py     # MDA工作流Agent
├── run_mda.py             # 执行脚本
└── README.md              # 说明文档
```

## 🚀 快速开始

### 1. 安装依赖
确保已安装React Agent Minimal项目：
```bash
cd ../react_is_all_you_need
pip install -r requirements.txt
```

### 2. 生成代码
```bash
# 进入MDA订单系统目录
cd mda-order-system

# 运行生成脚本
python run_mda.py
```

### 3. 启动服务
```bash
# 进入某个服务目录
cd output/fastapi/product-service

# 安装依赖
pip install -r requirements.txt

# 启动服务
uvicorn app.main:app --reload
```

## 🔧 自定义配置

### 修改业务模型
编辑 `pim/order_system.md` 文件来修改业务需求。

### 调整技术决策
修改知识文件来改变技术选择：
- `knowledge/pim_to_fastapi_psm.md` - 调整微服务划分和API设计
- `knowledge/fastapi_psm_to_code.md` - 调整代码生成规则

### 添加新的技术栈
1. 创建新的PSM转换规则：`pim_to_spring_psm.md`
2. 创建新的代码生成规则：`spring_psm_to_code.md`
3. 更新Agent配置

## 🧠 核心概念

### PIM (Platform Independent Model)
- 纯业务描述，不包含技术细节
- 定义业务实体、流程、规则
- 格式：Markdown/YAML

### PSM (Platform Specific Model) 
- 包含技术决策和架构设计
- 微服务划分、API设计、数据库设计
- 格式：结构化数据（JSON/YAML）

### Code
- 根据PSM生成的可执行代码
- 完整的应用程序实现

## 📋 开发流程

1. **业务建模**：在PIM中定义业务需求
2. **技术设计**：在知识文件中定义转换规则  
3. **自动生成**：通过Agent自动生成代码
4. **手动完善**：在生成代码基础上完善业务逻辑
5. **测试部署**：测试并部署生成的系统

## 🎯 优势特点

- **平台无关性**：业务模型与技术实现分离
- **自动化程度高**：大部分代码自动生成
- **易于维护**：修改业务模型即可重新生成
- **技术栈灵活**：支持多种技术栈生成
- **一致性保证**：所有服务遵循相同规范

## 🔮 未来扩展

- [ ] Spring Cloud版本支持
- [ ] 事件驱动架构
- [ ] 分布式事务支持
- [ ] 监控和日志集成
- [ ] CI/CD流水线集成

## 📝 注意事项

1. **代理配置**：访问localhost时需要禁用代理（详见agent.md）
2. **知识文件更新**：修改业务需求后需要更新知识文件
3. **生成代码审查**：自动生成的代码需要人工审查和测试
4. **数据库配置**：生成后需要配置真实的数据库连接

## 📞 支持

如有问题，请参考：
- `./MDA订单系统开发备忘录.md` - 详细设计文档
- `../react_is_all_you_need/agent.md` - React Agent使用指南
- 知识文件中的详细注释说明