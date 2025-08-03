# Agent 主观视图模板

不同角色的 Agent 应该关注不同的方面，以下是各类 Agent 的主观视图指南。

## 1. Code Reviewer 视角

### 关注类别
- **code_quality**: 代码质量问题
- **maintainability**: 可维护性问题
- **testing**: 测试覆盖率和质量
- **documentation**: 文档完整性

### 观察示例
```python
pm.add_observation(
    category="code_quality",
    content="函数 process_data 超过 200 行，建议拆分",
    severity="warning",
    context="src/processors/data_processor.py"
)
```

### 洞察主题
- 代码复杂度分析
- 测试覆盖率评估
- 代码风格一致性
- 技术债务识别

## 2. Security Auditor 视角

### 关注类别
- **security_vulnerability**: 安全漏洞
- **authentication**: 认证问题
- **data_protection**: 数据保护
- **configuration**: 配置安全

### 观察示例
```python
pm.add_observation(
    category="security_vulnerability",
    content="SQL 查询使用字符串拼接，存在注入风险",
    severity="critical",
    context="api/user_handler.py:45"
)
```

### 洞察主题
- 安全风险评估
- 认证机制分析
- 数据加密状况
- 依赖安全性

## 3. Performance Optimizer 视角

### 关注类别
- **performance_bottleneck**: 性能瓶颈
- **resource_usage**: 资源使用
- **scalability**: 可扩展性
- **optimization_opportunity**: 优化机会

### 观察示例
```python
pm.add_observation(
    category="performance_bottleneck",
    content="数据库查询在循环中执行，导致 N+1 问题",
    severity="warning",
    context="services/report_generator.py"
)
```

### 洞察主题
- 性能热点分析
- 资源利用效率
- 扩展性评估
- 缓存策略建议

## 4. Software Architect 视角

### 关注类别
- **architecture_pattern**: 架构模式
- **module_coupling**: 模块耦合
- **design_principle**: 设计原则
- **technical_debt**: 技术债务

### 观察示例
```python
pm.add_observation(
    category="module_coupling",
    content="业务逻辑直接依赖数据库实现，违反依赖倒置原则",
    severity="warning",
    context="business/user_service.py"
)
```

### 洞察主题
- 架构演进方向
- 模块化改进
- 设计模式应用
- 技术栈评估

## 5. DevOps Engineer 视角

### 关注类别
- **deployment**: 部署配置
- **monitoring**: 监控覆盖
- **automation**: 自动化程度
- **infrastructure**: 基础设施

### 观察示例
```python
pm.add_observation(
    category="deployment",
    content="缺少健康检查端点，影响容器编排",
    severity="warning",
    context="Dockerfile"
)
```

### 洞察主题
- CI/CD 流程评估
- 监控完整性
- 基础设施即代码
- 容器化策略

## 使用指南

### 1. 初始化视角
```python
from perspective_manager import PerspectiveManager

# 根据 Agent 角色创建管理器
pm = PerspectiveManager(
    agent_name=self.name,
    agent_role=self.role,  # 如 "code_reviewer"
    work_dir=self.work_dir
)
```

### 2. 在任务执行中记录观察
```python
# 发现问题时立即记录
if self._detect_code_smell(code):
    pm.add_observation(
        category="code_quality",
        content=f"发现代码异味：{smell_type}",
        severity="warning",
        context=file_path
    )
```

### 3. 定期总结洞察
```python
# 任务完成后总结关键发现
if significant_findings:
    pm.update_insight(
        topic="整体代码质量",
        summary="代码库存在多处质量问题需要关注",
        details=findings_list,
        recommendations=improvement_suggestions
    )
```

### 4. 跨 Agent 协作
```python
# 查询其他 Agent 的视角
other_perspectives = pm.query_perspectives(
    ["security_auditor", "performance_optimizer"]
)

# 根据其他视角调整自己的关注点
if "authentication" in other_perspectives.get("security_auditor", {}).get("insights", []):
    # 特别关注认证相关的代码质量
    pass
```

## 最佳实践

1. **及时性**: 发现问题立即记录，不要等到任务结束
2. **具体性**: 提供明确的上下文和位置信息
3. **可操作性**: 洞察应包含具体的改进建议
4. **协作性**: 定期查看其他 Agent 的视角，形成全面认识
5. **演进性**: 随着对项目的深入了解，不断更新和完善洞察

## 主观视图的价值

- **知识传承**: 新 Agent 可以快速了解项目的专业评估
- **决策支持**: 为用户提供多角度的专业意见
- **持续改进**: 跟踪问题的发现和解决过程
- **团队协作**: 不同专业 Agent 的视角互补