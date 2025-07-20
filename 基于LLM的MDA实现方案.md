# 基于大语言模型的MDA实现方案

## 核心理念转变

### 从符号主义到连接主义

**传统方法（符号主义）**：
- 预定义的代码模板
- 规则化的转换逻辑
- 静态的映射关系

**LLM方法（连接主义）**：
- 自然语言理解PIM描述
- 上下文感知的代码生成
- 动态适应不同需求

## Claude Code Slash Commands实现架构

### 1. /mda-generate 命令实现

```markdown
# 命令定义
/mda-generate domain=<领域> service=<服务名>

# 执行流程
1. Claude读取并理解PIM模型（Markdown + Mermaid）
2. 基于上下文理解生成代码，而非模板填充
3. 考虑业务规则和最佳实践
4. 生成符合项目特定需求的代码
```

### 2. 提示词工程

```markdown
## MDA代码生成提示词

你是一个专业的FastAPI开发专家。请根据以下PIM模型生成微服务代码。

### 输入
- PIM模型文件：[文件内容]
- 服务名称：[service-name]

### 要求
1. 理解业务描述和实体关系
2. 根据业务规则生成合适的验证逻辑
3. 考虑性能和安全需求
4. 生成可扩展的代码结构
5. 包含必要的错误处理和日志

### 输出
生成完整的FastAPI项目，包括：
- 数据模型（Pydantic + SQLAlchemy）
- API路由（RESTful）
- 业务逻辑层
- 配置和依赖注入
- Docker支持
- 基础测试

### 特殊指令
- 使用MDA标记区分生成和自定义代码
- 遵循Python最佳实践
- 考虑微服务架构原则
```

### 3. 智能代码生成特性

#### 上下文理解
- 理解中文业务描述
- 推断隐含的业务逻辑
- 识别领域特定模式

#### 自适应生成
- 根据实体复杂度调整代码结构
- 自动选择合适的设计模式
- 智能处理实体关系

#### 代码质量
- 生成类型安全的代码
- 包含适当的文档和注释
- 遵循项目约定

## 实现方案

### 方案1：使用Claude Code API（推荐）

```python
# .mda/commands/mda-generate-llm.py
"""
基于LLM的MDA代码生成器
通过Claude Code API实现智能代码生成
"""

def generate_with_llm(domain: str, service: str):
    # 1. 读取PIM模型
    pim_content = read_pim_model(f"models/domain/{domain}.md")
    
    # 2. 构建生成提示
    prompt = build_generation_prompt(pim_content, service)
    
    # 3. 调用Claude生成代码
    # 注意：这里使用Claude的代码生成能力
    # 而不是预定义的模板
    
    # 4. 后处理和文件写入
    write_generated_files(generated_code)
```

### 方案2：Slash Command扩展

在Claude Code中创建自定义slash command：

```yaml
# .claude/commands.yaml
commands:
  - name: mda-generate
    description: "基于PIM模型生成FastAPI服务"
    handler: |
      1. 读取指定的PIM模型文件
      2. 理解业务需求和实体关系
      3. 生成符合需求的FastAPI代码
      4. 创建完整的项目结构
    parameters:
      - name: domain
        required: true
        description: "领域模型名称"
      - name: service
        required: true
        description: "服务名称"
```

### 方案3：交互式生成

```markdown
## 交互式MDA流程

1. **用户**: /mda-generate domain=用户管理 service=user-service

2. **Claude分析PIM**:
   - 识别到User、UserRole、Permission等实体
   - 理解认证、权限等业务规则
   - 注意到性能和安全要求

3. **Claude生成代码**:
   - 不是填充模板，而是基于理解生成
   - 考虑具体业务场景
   - 生成优化的代码实现

4. **迭代优化**:
   用户: "添加邮件验证功能"
   Claude: 理解需求并增量更新代码
```

## 优势对比

### 传统模板方法
- ❌ 僵化的代码结构
- ❌ 无法理解业务意图
- ❌ 难以处理特殊需求
- ❌ 生成的代码千篇一律

### LLM驱动方法
- ✅ 理解业务语境
- ✅ 生成定制化代码
- ✅ 考虑最佳实践
- ✅ 支持自然语言交互
- ✅ 持续学习和改进

## 实施步骤

### 第一步：创建Slash Command处理器

```python
# .mda/slash_commands.py
import os
from pathlib import Path

class MDASlashCommands:
    """处理MDA相关的slash命令"""
    
    def handle_mda_generate(self, domain: str, service: str):
        """
        /mda-generate命令处理
        使用Claude的理解能力生成代码
        """
        # 这里的关键是：让Claude理解模型并生成代码
        # 而不是使用预定义的模板
        
    def handle_mda_update(self, model: str, target: str):
        """
        /mda-update命令处理
        理解现有代码和新模型的差异
        """
        
    def handle_mda_reverse(self, source: str, model: str):
        """
        /mda-reverse命令处理
        从代码理解并生成模型
        """
```

### 第二步：集成Claude Code

```markdown
# 在CLAUDE.md中添加指令

## MDA代码生成指令

当用户使用/mda-generate命令时：

1. 深入理解PIM模型文件
2. 分析业务需求和约束
3. 生成高质量的FastAPI代码
4. 确保代码的可维护性和扩展性

不要使用固定模板，而是根据具体需求生成定制化代码。
```

### 第三步：提示词优化

```markdown
## 生成FastAPI服务的核心提示

基于以下PIM模型，生成一个生产级的FastAPI微服务：

### 关注点
1. **业务理解**：深入理解业务规则和约束
2. **代码质量**：生成清晰、可维护的代码
3. **性能优化**：考虑查询优化和缓存策略
4. **安全加固**：实现适当的认证和授权
5. **错误处理**：完善的异常处理机制

### 生成策略
- 使用依赖注入模式
- 实现仓储模式分离数据访问
- 添加适当的中间件
- 包含API版本控制
- 生成OpenAPI文档

### 代码风格
- 遵循PEP 8
- 使用类型注解
- 添加docstring
- 合理的文件组织
```

## 示例：LLM驱动的代码生成

### 输入（PIM模型片段）
```markdown
## 业务规则
- 用户邮箱必须唯一
- 新用户需要邮箱验证
- 密码强度要求：8位以上，包含大小写和数字
```

### LLM理解并生成
```python
# 不是模板填充，而是理解业务需求后生成

from pydantic import BaseModel, EmailStr, validator
import re

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    
    @validator('password')
    def validate_password_strength(cls, v):
        """基于业务规则的密码验证"""
        if len(v) < 8:
            raise ValueError('密码长度必须至少8位')
        if not re.search(r'[A-Z]', v):
            raise ValueError('密码必须包含大写字母')
        if not re.search(r'[a-z]', v):
            raise ValueError('密码必须包含小写字母')
        if not re.search(r'\d', v):
            raise ValueError('密码必须包含数字')
        return v
    
    @validator('email')
    def email_must_be_unique(cls, v):
        # LLM理解到需要唯一性检查
        # 并生成相应的验证逻辑
        pass
```

## 总结

基于LLM的MDA不是简单的模板替换，而是：
1. **理解**业务需求
2. **推理**最佳实现
3. **生成**高质量代码
4. **适应**特定场景

这种方法真正实现了从业务模型到代码的智能转换。