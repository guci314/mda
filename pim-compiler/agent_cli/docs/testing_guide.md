# Agent CLI 测试指南

## 概述

Agent CLI 提供了完整的测试框架，支持智能体的单元测试、集成测试和性能测试。测试框架支持多种报告格式，并提供可视化分析工具。

## 测试架构

### 核心组件

1. **TestRunner**: 测试运行器，负责执行测试套件
2. **TestCase**: 测试用例定义
3. **TestSuite**: 测试套件，包含多个测试用例
4. **TestReport**: 测试报告，包含执行结果
5. **ReportViewer**: 报告查看器，提供可视化功能

### 测试流程

```
测试套件 → 测试运行器 → 执行智能体 → 验证结果 → 生成报告
```

## 测试用例定义

### 基本结构

```json
{
  "name": "test_case_name",
  "description": "测试用例描述",
  "input": {
    // 输入参数
  },
  "expected_output": {
    // 期望输出（可选）
  },
  "expected_actions": [
    // 期望的动作序列（可选）
  ],
  "timeout": 60,  // 超时时间（秒）
  "tags": ["tag1", "tag2"]  // 标签
}
```

### 验证规则

1. **输出验证**
   - 精确匹配：期望值与实际值完全相同
   - 通配符：使用 `"*"` 匹配任意值
   - 正则表达式：使用 `"regex:pattern"` 进行模式匹配

2. **动作验证**
   - 精确匹配：动作名称完全相同
   - 前缀匹配：使用 `"action*"` 匹配以特定前缀开始的动作
   - 通配符：使用 `"*"` 匹配任意动作

## 测试套件定义

### 完整示例

```json
{
  "name": "comprehensive_test_suite",
  "description": "综合测试套件",
  "agent_name": "my_agent",
  "tags": ["integration", "v1.0"],
  "setup": {
    "action": "shell",
    "command": "mkdir -p test_workspace"
  },
  "teardown": {
    "action": "shell",
    "command": "rm -rf test_workspace"
  },
  "test_cases": [
    // 测试用例列表
  ]
}
```

### Setup 和 Teardown

- **Setup**: 在测试开始前执行，用于准备测试环境
- **Teardown**: 在测试结束后执行，用于清理测试环境
- 支持 `shell` 命令和 `python` 代码执行

## 命令行使用

### 1. 生成测试模板

```bash
# 为指定智能体生成测试模板
./agent-cli test generate <agent_name>

# 指定输出文件和测试用例数量
./agent-cli test generate code_generator -o my_test.json -c 10
```

### 2. 运行测试

```bash
# 运行测试套件
./agent-cli test run test_suite.json

# 指定输出格式和路径
./agent-cli test run test_suite.json -o report.html -f html

# 按标签过滤测试
./agent-cli test run test_suite.json -t unit -t basic

# 显示详细输出
./agent-cli test run test_suite.json -v
```

### 3. 查看报告

```bash
# 查看测试报告摘要
./agent-cli test show report.json

# 查看详细结果
./agent-cli test show report.json -f detailed

# 只查看失败的测试
./agent-cli test show report.json -f failed
```

### 4. 统计分析

```bash
# 统计最近7天的测试结果
./agent-cli test stats

# 统计特定智能体的结果
./agent-cli test stats -a code_generator -d 30
```

## 报告格式

### 1. JSON 报告

结构化的测试结果，适合程序化处理：

```json
{
  "suite": {
    "name": "...",
    "agent_name": "..."
  },
  "summary": {
    "total_tests": 10,
    "passed_tests": 8,
    "failed_tests": 2,
    "success_rate": 80.0
  },
  "results": [...]
}
```

### 2. HTML 报告

交互式的网页报告，包含：
- 测试摘要仪表板
- 可展开的测试用例详情
- 日志查看器
- 进度条和状态指示器

### 3. Markdown 报告

适合在文档中嵌入的报告格式：
- 清晰的标题层级
- 表格形式的测试结果
- 代码块格式的日志

## 高级功能

### 1. 批量测试

创建批量测试脚本：

```python
#!/usr/bin/env python3
import glob
from agent_cli.core.test_runner import TestRunner
from agent_cli.core.agent_registry import AgentRegistry

registry = AgentRegistry()
runner = TestRunner(registry)

# 运行所有测试套件
for test_file in glob.glob("tests/*.json"):
    suite = runner.load_test_suite(test_file)
    report = runner.run_test_suite(suite)
    runner.save_report(report, f"reports/{suite.name}.json")
```

### 2. 自定义验证器

扩展测试框架以支持自定义验证：

```python
class CustomValidator:
    def validate_response_time(self, actual, expected):
        """验证响应时间是否在预期范围内"""
        return actual <= expected * 1.2  # 允许20%的误差
    
    def validate_output_format(self, actual, expected_format):
        """验证输出格式"""
        if expected_format == "json":
            try:
                json.loads(actual)
                return True
            except:
                return False
```

### 3. 性能测试

使用测试框架进行性能测试：

```json
{
  "name": "performance_test",
  "test_cases": [
    {
      "name": "test_throughput",
      "description": "测试吞吐量",
      "input": {
        "batch_size": 100,
        "concurrent": true
      },
      "expected_output": {
        "status": "success",
        "processed": 100
      },
      "timeout": 10,  // 严格的时间限制
      "tags": ["performance"]
    }
  ]
}
```

### 4. 测试报告可视化

使用 ReportViewer 生成图表：

```python
from agent_cli.utils.report_viewer import ReportViewer

viewer = ReportViewer()

# 生成测试趋势图
viewer.generate_trend_chart("code_generator", days=30)

# 生成对比图表
reports = viewer.load_multiple_reports()
viewer.generate_summary_chart(reports)

# 分析失败模式
analysis = viewer.analyze_failure_patterns(reports)
```

## 最佳实践

### 1. 测试用例设计

- **原子性**: 每个测试用例应该独立，不依赖其他测试
- **明确性**: 清晰定义输入和期望输出
- **覆盖性**: 覆盖正常情况、边界情况和错误情况
- **标签化**: 使用标签对测试进行分类

### 2. 测试组织

```
tests/
├── unit/              # 单元测试
│   ├── test_basic.json
│   └── test_edge_cases.json
├── integration/       # 集成测试
│   └── test_workflow.json
└── performance/       # 性能测试
    └── test_load.json
```

### 3. CI/CD 集成

在 CI/CD 流程中集成测试：

```yaml
# .github/workflows/test.yml
name: Agent Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: |
          ./agent-cli test run tests/unit/*.json
          ./agent-cli test run tests/integration/*.json
      - name: Upload reports
        uses: actions/upload-artifact@v2
        with:
          name: test-reports
          path: test_report_*.html
```

### 4. 测试驱动开发

1. 先编写测试用例
2. 运行测试（预期失败）
3. 实现智能体功能
4. 运行测试（预期通过）
5. 重构和优化

## 故障排除

### 常见问题

1. **测试超时**
   - 增加 timeout 值
   - 检查智能体是否有死循环
   - 使用 `-v` 查看详细日志

2. **动作不匹配**
   - 使用通配符匹配动态动作名
   - 检查动作执行顺序
   - 查看实际执行的动作列表

3. **输出验证失败**
   - 使用正则表达式匹配变化的值
   - 检查数据类型是否匹配
   - 考虑使用部分匹配

### 调试技巧

1. **使用详细模式**: `./agent-cli test run -v`
2. **查看完整日志**: 在 HTML 报告中展开测试用例
3. **单独运行失败的测试**: 创建只包含失败用例的测试套件
4. **使用交互模式**: 手动执行智能体查看行为

## 示例测试套件

查看 `agent_cli/examples/` 目录下的示例测试套件：

- `code_generator_test.json`: 代码生成智能体测试
- `web_searcher_test.json`: 网络搜索智能体测试
- `data_analyzer_test.json`: 数据分析智能体测试

## 总结

Agent CLI 测试框架提供了完整的测试解决方案，从简单的单元测试到复杂的集成测试。通过合理使用测试框架，可以确保智能体的质量和可靠性。

记住：好的测试是智能体成功的关键！