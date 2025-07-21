# PIM 编译器增强功能

## 新增功能概述

PIM 编译器现在支持以下增强功能：

1. **单元测试生成** - 自动为生成的代码创建单元测试
2. **Lint 检查** - 自动检查代码质量并修复问题
3. **测试执行** - 运行生成的测试并自动修复失败
4. **Gemini CLI 集成** - 使用 AI 自动修复代码问题

## PIM 中定义单元测试

在 PIM 文档中添加 `## 单元测试` 部分：

```markdown
## 单元测试

### 实体测试
#### 测试：用户实体验证
- 测试用户名验证
  - 输入：空用户名 → 期望：验证失败
  - 输入：用户名 "valid_user123" → 期望：验证成功

### 服务测试  
#### 测试：用户注册
- 测试正常注册
  - 准备：清空测试数据库
  - 输入：有效的用户数据
  - 期望：用户创建成功，返回用户ID
```

## 使用方法

### 1. 基本编译（生成 PSM）
```bash
./pimc compile user_management.md
```

### 2. 生成代码和测试
```bash
./pimc compile user_management.md --generate-code
```

### 3. 跳过 lint 检查
```bash
./pimc compile user_management.md --generate-code --no-lint
```

### 4. 跳过测试运行
```bash
./pimc compile user_management.md --generate-code --no-run-tests
```

## 配置选项

在 `pimc.yaml` 中配置：

```yaml
# 代码质量选项
enable_lint: true          # 启用 lint 检查
auto_fix_lint: true        # 自动修复 lint 错误
enable_unit_tests: true    # 生成单元测试
run_tests: true           # 运行测试
auto_fix_tests: true      # 自动修复失败的测试
min_test_coverage: 80.0   # 最低测试覆盖率
```

## 工作流程

```
1. PIM → PSM 转换
   ↓
2. PSM → 代码生成（包含测试）
   ↓
3. Lint 检查
   ↓ (如有错误)
4. Gemini 自动修复
   ↓
5. 运行单元测试
   ↓ (如有失败)
6. Gemini 自动修复测试
   ↓
7. 完成
```

## 支持的平台和工具

### Python (FastAPI/Django)
- **Linter**: black + flake8
- **测试框架**: pytest
- **覆盖率**: pytest-cov

### JavaScript/TypeScript
- **Linter**: eslint
- **测试框架**: jest
- **覆盖率**: jest --coverage

### Java (Spring)
- **Linter**: checkstyle
- **测试框架**: JUnit
- **覆盖率**: JaCoCo

## Gemini CLI 集成

### 安装 Gemini CLI
```bash
# 假设 Gemini CLI 的安装方法
pip install gemini-cli
# 或
npm install -g gemini-cli
```

### 配置 API Key
```bash
export GEMINI_API_KEY=your-api-key
```

### 手动调用修复
```bash
gemini fix --file src/user.py --prompt "Fix flake8 errors"
```

## 示例输出

编译带测试的 PIM 文件后，会生成：

```
output/
├── user_management_fastapi.psm.md    # PSM 文件
└── generated/
    └── user_management_fastapi/
        ├── models.py                  # 数据模型
        ├── test_models.py             # 模型测试
        ├── services.py                # 业务服务
        ├── test_services.py           # 服务测试
        ├── api.py                     # API 端点
        └── test_api.py                # API 测试
```

## 错误处理

### Lint 错误示例
```
Lint 错误: models.py:10:80: E501 line too long (85 > 79 characters)
使用 Gemini 修复 python lint 错误
Gemini 修复成功: models.py
```

### 测试失败示例
```
测试失败: FAILED test_user.py::test_create_user - AssertionError
使用 Gemini 修复 pytest failures
Gemini 修复成功: test_user.py
重新运行测试...
测试通过！
```

## 最佳实践

1. **详细的测试定义** - 在 PIM 中明确定义测试场景
2. **使用 CI/CD** - 集成到持续集成流程
3. **版本控制** - 将生成的测试纳入版本控制
4. **定期更新** - 保持 linter 和测试工具最新

## 注意事项

1. 需要安装相应的 lint 和测试工具
2. Gemini CLI 需要有效的 API Key
3. 自动修复可能需要人工审核
4. 某些复杂错误可能无法自动修复