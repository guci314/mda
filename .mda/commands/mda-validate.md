# /mda-validate

## 描述
验证PIM模型与生成代码之间的一致性，确保模型驱动开发的完整性。

## 语法
```
/mda-validate [scope=<验证范围>] [fix=<是否自动修复>] [report=<报告格式>]
```

## 参数
- `scope` (可选): 验证范围
  - `all`: 验证所有模型和服务（默认）
  - `domain`: 仅验证领域模型
  - `service`: 仅验证服务代码
  - 特定路径: 如 `services/user-service`
- `fix` (可选): 是否自动修复可修复的问题
  - `true`: 自动修复
  - `false`: 仅报告（默认）
- `report` (可选): 报告输出格式
  - `console`: 控制台输出（默认）
  - `markdown`: Markdown格式报告
  - `json`: JSON格式报告

## 功能说明

### 1. 验证检查项

#### 模型完整性检查
- 实体定义是否完整
- 属性类型是否明确
- 关系是否双向一致
- 业务规则是否有歧义

#### 代码一致性检查
- 模型中的实体是否都已生成代码
- 代码中的模型是否与PIM一致
- API端点是否符合设计意图
- 数据验证规则是否匹配

#### 同步标记检查
- MDA标记是否完整
- 自定义代码区域是否正确标记
- 版本信息是否最新

### 2. 问题分类

#### 错误级别（Error）
- 模型与代码不一致
- 缺失必要的实体或属性
- 类型定义冲突
- 关系定义错误

#### 警告级别（Warning）
- 代码中存在模型未定义的元素
- 业务规则实现不完整
- API设计偏离意图
- 性能相关问题

#### 信息级别（Info）
- 建议的改进项
- 最佳实践提醒
- 版本更新提示

### 3. 自动修复能力

#### 可自动修复的问题
- 缺失的MDA标记
- 简单的类型不匹配
- 缺失的import语句
- 格式问题

#### 需要人工处理的问题
- 业务逻辑冲突
- 复杂的类型变更
- API设计变更
- 数据库结构调整

## 使用示例

### 全量验证
```bash
# 验证所有模型和代码
/mda-validate
```

### 特定服务验证
```bash
# 仅验证用户服务
/mda-validate scope=services/user-service
```

### 自动修复模式
```bash
# 验证并自动修复可修复的问题
/mda-validate fix=true
```

### 生成Markdown报告
```bash
# 生成详细的Markdown格式报告
/mda-validate report=markdown > validation-report.md
```

## 验证报告示例

### 控制台输出格式
```
MDA验证报告
============
扫描时间: 2024-01-20 10:30:00
扫描范围: 全部

发现的问题:
-----------

❌ 错误 (3个):
1. [services/user-service] User实体缺少'phone'属性
   位置: app/models/domain.py:25
   模型定义: models/domain/用户管理.md:35
   
2. [services/order-service] OrderStatus枚举值不匹配
   代码: ['PENDING', 'PAID', 'SHIPPED']
   模型: ['PENDING', 'PAID', 'SHIPPED', 'COMPLETED']

⚠️ 警告 (5个):
1. [services/user-service] API端点'/users/bulk'未在模型中定义
2. [services/payment-service] 业务规则"退款时限"未实现

ℹ️ 信息 (2个):
1. 建议更新FastAPI到最新版本
2. 考虑添加缓存以提高性能

验证结果: ❌ 失败
需要修复3个错误和5个警告
```

### Markdown报告格式
```markdown
# MDA验证报告

## 概览
- **扫描时间**: 2024-01-20 10:30:00
- **扫描范围**: 全部
- **状态**: ❌ 失败

## 统计信息
| 级别 | 数量 | 可自动修复 |
|------|------|-----------|
| 错误 | 3    | 1         |
| 警告 | 5    | 3         |
| 信息 | 2    | 0         |

## 详细问题

### 🔴 错误

#### 1. User实体属性缺失
- **服务**: user-service
- **文件**: `app/models/domain.py:25`
- **问题**: 模型定义了'phone'属性但代码中缺失
- **修复建议**: 运行 `/mda-update` 更新代码

...
```

### JSON报告格式
```json
{
  "validation_report": {
    "timestamp": "2024-01-20T10:30:00Z",
    "scope": "all",
    "status": "failed",
    "summary": {
      "errors": 3,
      "warnings": 5,
      "info": 2
    },
    "issues": [
      {
        "level": "error",
        "service": "user-service",
        "type": "missing_attribute",
        "description": "User实体缺少'phone'属性",
        "location": {
          "file": "app/models/domain.py",
          "line": 25
        },
        "model_reference": {
          "file": "models/domain/用户管理.md",
          "line": 35
        },
        "auto_fixable": true
      }
    ]
  }
}
```

## 验证规则配置

在`.mda/validation.yml`中配置验证规则：

```yaml
validation:
  # 严格模式
  strict_mode: true
  
  # 检查规则
  rules:
    # 模型检查
    model:
      check_completeness: true
      check_relationships: true
      check_types: true
      
    # 代码检查
    code:
      check_imports: true
      check_markers: true
      check_naming: true
      
    # API检查
    api:
      check_routes: true
      check_methods: true
      check_responses: true
      
  # 忽略规则
  ignore:
    # 忽略特定文件
    files:
      - "**/*_test.py"
      - "**/conftest.py"
      
    # 忽略特定检查
    checks:
      - "unused_imports"
      - "line_length"
      
  # 自定义规则
  custom_rules:
    - name: "password_complexity"
      description: "检查密码复杂度规则"
      pattern: "password.*Field.*min_length=\\d+"
      expected: "min_length >= 8"
```

## 集成CI/CD

### GitHub Actions示例
```yaml
name: MDA Validation

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Run MDA Validation
        run: |
          claude code /mda-validate report=json > validation.json
          
      - name: Check Validation Result
        run: |
          if grep -q '"status": "failed"' validation.json; then
            echo "❌ MDA验证失败"
            exit 1
          fi
```

### Pre-commit Hook
```bash
#!/bin/bash
# .git/hooks/pre-commit

echo "运行MDA验证..."
claude code /mda-validate scope=all

if [ $? -ne 0 ]; then
    echo "❌ MDA验证失败，请修复问题后再提交"
    exit 1
fi
```

## 高级用法

### 1. 增量验证
```bash
# 只验证最近修改的文件
/mda-validate scope=changed
```

### 2. 验证特定规则
```bash
# 只验证API一致性
/mda-validate rules=api
```

### 3. 批量修复
```bash
# 修复所有可自动修复的问题
/mda-validate fix=true scope=all
```

### 4. 持续监控
```bash
# 监视模式，文件变化时自动验证
/mda-validate --watch
```

## 最佳实践

### 1. 定期验证
- 每次提交前运行验证
- 集成到CI/CD流程
- 定期全量验证

### 2. 渐进式修复
- 先修复错误级别问题
- 逐步处理警告
- 持续改进代码质量

### 3. 团队规范
- 统一验证配置
- 共享忽略规则
- 定期审查验证报告

## 注意事项

1. **性能影响**
   - 大型项目验证可能耗时
   - 可以使用scope限制范围
   - 考虑并行验证

2. **误报处理**
   - 合理配置忽略规则
   - 对特定代码添加忽略注释
   - 定期审查忽略列表

3. **版本兼容**
   - 确保MDA工具版本一致
   - 注意框架版本差异
   - 保持验证规则更新

## 相关命令
- `/mda-update`: 根据验证结果更新代码
- `/mda-diff`: 查看详细差异
- `/mda-fix`: 专门的修复命令