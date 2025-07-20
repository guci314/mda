# /mda-update

## 描述
增量更新已有的FastAPI微服务代码，保留用户自定义的修改。

## 语法
```
/mda-update model=<模型文件路径> target=<目标代码路径> [merge-strategy=<合并策略>]
```

## 参数
- `model` (必需): PIM模型文件的相对路径
- `target` (必需): 目标服务代码的根目录路径
- `merge-strategy` (可选): 合并策略，可选值：
  - `override`: 覆盖所有MDA生成的代码（默认）
  - `merge`: 智能合并，保留自定义代码
  - `ask`: 遇到冲突时询问用户

## 功能说明

### 1. 变更检测
- 比较新旧模型差异
- 识别新增、修改、删除的实体和属性
- 检测业务规则变化
- 分析API设计变更

### 2. 更新范围

#### 自动更新的内容
- Pydantic模型定义
- SQLAlchemy实体结构
- 基础CRUD API路由
- 数据验证规则
- API文档注释

#### 保护的内容（不会被覆盖）
- 自定义业务逻辑（标记为CUSTOM区域）
- 用户添加的辅助函数
- 自定义配置和中间件
- 手动编写的测试用例

### 3. 代码标记系统

生成的代码包含特殊注释标记：

```python
# MDA-GENERATED-START: User.model
class User(BaseModel):
    id: str
    username: str
    email: EmailStr
# MDA-GENERATED-END: User.model

# MDA-CUSTOM-START: User.validation
# 这里的代码不会被覆盖
def custom_email_validator(email: str) -> str:
    # 自定义验证逻辑
    return email
# MDA-CUSTOM-END: User.validation
```

### 4. 数据库迁移

当模型结构发生变化时，自动生成Alembic迁移文件：

```bash
# 自动生成的迁移文件
alembic/versions/xxxx_update_user_model.py
```

## 使用示例

### 基础更新
```bash
# 更新用户服务
/mda-update model=models/domain/用户管理.md target=services/user-service
```

### 使用智能合并
```bash
# 保留自定义代码的更新
/mda-update model=models/domain/订单系统.md target=services/order-service merge-strategy=merge
```

### 交互式更新
```bash
# 遇到冲突时询问
/mda-update model=models/domain/支付流程.md target=services/payment-service merge-strategy=ask
```

## 更新流程

### 1. 前置检查
- 验证目标目录是MDA生成的项目
- 检查是否有未提交的更改
- 备份当前代码（可选）

### 2. 差异分析
```
分析结果示例：
- 新增实体: UserActivity
- 修改属性: User.email (添加唯一约束)
- 删除属性: User.nickname
- 新增API: GET /users/activities
- 修改规则: 密码长度从8改为10
```

### 3. 代码生成
- 生成新的模型代码
- 更新API路由
- 调整Service层
- 创建数据库迁移

### 4. 合并处理
- 根据策略处理冲突
- 保留用户自定义代码
- 更新import语句
- 格式化代码

### 5. 后置操作
- 运行代码格式化
- 执行类型检查
- 生成更新报告

## 冲突处理

### Override策略
- 直接覆盖MDA标记区域
- 保留CUSTOM标记区域
- 适用于模型主导的开发

### Merge策略
- 智能识别用户修改
- 尝试自动合并
- 无法自动合并时保留两个版本

### Ask策略
显示冲突详情并提供选项：
```
检测到冲突：User.validate_email方法
1. 使用新模型版本
2. 保留当前版本
3. 查看差异
4. 手动编辑
请选择 [1-4]:
```

## 最佳实践

### 1. 版本控制
- 更新前提交所有更改
- 使用特性分支进行更新
- 更新后进行代码审查

### 2. 自定义代码组织
```python
# 使用CUSTOM标记保护自定义代码
# MDA-CUSTOM-START: business-logic
def complex_business_logic():
    # 这部分代码不会被更新覆盖
    pass
# MDA-CUSTOM-END: business-logic
```

### 3. 测试驱动
- 更新前运行所有测试
- 更新后验证测试通过
- 为新功能添加测试

### 4. 数据库同步
```bash
# 更新后执行数据库迁移
alembic upgrade head

# 或者先检查迁移脚本
alembic upgrade --sql
```

## 配置选项

在`.mda/update.yml`中配置更新行为：

```yaml
update:
  # 备份配置
  backup:
    enabled: true
    directory: .mda/backups
    
  # 代码格式化
  formatting:
    tool: black  # black | autopep8 | yapf
    
  # 验证配置
  validation:
    type_check: true  # 运行mypy
    lint: true        # 运行flake8
    test: true        # 运行pytest
    
  # 自定义标记
  markers:
    custom_start: "MDA-CUSTOM-START"
    custom_end: "MDA-CUSTOM-END"
    generated_start: "MDA-GENERATED-START"
    generated_end: "MDA-GENERATED-END"
```

## 注意事项

1. **数据安全**
   - 建议在更新前备份数据库
   - 测试环境先行验证
   - 准备回滚方案

2. **代码兼容性**
   - 注意破坏性变更
   - 检查API版本兼容
   - 更新相关文档

3. **性能考虑**
   - 大型项目更新可能耗时
   - 建议分批更新
   - 监控更新后性能

## 相关命令
- `/mda-generate-fastapi`: 初始生成FastAPI代码
- `/mda-reverse`: 代码反向同步到模型
- `/mda-validate`: 验证一致性
- `/mda-diff`: 查看模型差异