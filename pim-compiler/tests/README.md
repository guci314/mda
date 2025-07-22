# PIM Compiler 测试套件

本目录包含 PIM Compiler 的所有测试。

## 测试结构

```
tests/
├── conftest.py              # pytest 配置
├── test_config.py           # 配置模块测试
├── test_compiler_factory.py # 编译器工厂测试
├── test_pure_gemini_compiler.py # 纯 Gemini 编译器测试
├── test_logger.py           # 日志模块测试
├── test_cli.py             # CLI 工具测试
├── test_integration.py      # 集成测试
└── README.md               # 本文件
```

## 运行测试

### 运行所有测试
```bash
pytest
```

### 只运行单元测试（快速）
```bash
pytest -m "not integration"
```

### 运行特定测试文件
```bash
pytest tests/test_config.py
```

### 运行并生成覆盖率报告
```bash
pytest --cov=src --cov-report=html
```

### 详细输出
```bash
pytest -v
```

## 测试类型

### 单元测试
- 快速、独立的测试
- 不需要外部资源
- 使用 mock 对象模拟依赖

### 集成测试
- 测试完整的编译流程
- 需要 Gemini API 密钥
- 标记为 `@pytest.mark.integration`
- 使用 `-m "not integration"` 跳过

## 编写新测试

### 单元测试示例
```python
def test_feature():
    """测试某个功能"""
    # Arrange
    config = CompilerConfig()
    
    # Act
    result = some_function(config)
    
    # Assert
    assert result == expected_value
```

### Mock 示例
```python
@patch('subprocess.Popen')
def test_with_mock(mock_popen):
    """使用 mock 测试外部调用"""
    mock_process = MagicMock()
    mock_process.returncode = 0
    mock_popen.return_value = mock_process
    
    # 测试代码
```

### 集成测试示例
```python
@pytest.mark.integration
@pytest.mark.slow
def test_full_compilation():
    """测试完整编译流程"""
    # 需要真实的 API 调用
    pass
```

## 测试配置

### 环境变量
测试时会自动设置 `TESTING=true`，代码可以据此调整行为。

### pytest.ini
配置文件定义了：
- 测试路径
- 输出格式
- 覆盖率设置
- 自定义标记

## 持续集成

建议在 CI/CD 中运行：
```bash
# 只运行快速测试
pytest -m "not integration" --cov=src

# 如果有 API 密钥，运行所有测试
pytest --cov=src
```