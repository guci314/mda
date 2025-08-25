# React Agent 多模型支持文档

## 概述

本项目支持三种主流LLM模型的React Agent实现：
- **DeepSeek** - 高效实用，性价比高
- **Kimi** - 详细全面，上下文长
- **Qwen3 Coder** - 代码能力强，专为agent优化

## 环境配置

### 1. API密钥设置

在项目根目录的 `.env` 文件中配置相应的API密钥：

```bash
# DeepSeek配置
DEEPSEEK_API_KEY=your_deepseek_api_key

# Kimi配置 (Moonshot AI)
MOONSHOT_API_KEY=your_moonshot_api_key

# Qwen配置 (通过OpenRouter)
OPENROUTER_API_KEY=your_openrouter_api_key
```

### 2. 获取API密钥

- **DeepSeek**: https://platform.deepseek.com
- **Kimi (Moonshot)**: https://platform.moonshot.cn
- **OpenRouter (for Qwen)**: https://openrouter.ai

## 使用方法

### 运行NLPL演示

```bash
# 使用DeepSeek (默认)
python demo_nlpl_complete.py

# 使用Kimi
python demo_nlpl_complete.py --model kimi

# 使用Qwen3 Coder
python demo_nlpl_complete.py --model qwen
```

### 测试模型功能

```bash
# 测试所有配置的模型
python test_nlpl_models.py

# 测试Qwen Agent
python test_qwen_agent.py
```

## 模型对比

### DeepSeek
- **优势**：
  - 执行速度快（比Kimi快约48%）
  - 输出简洁高效
  - 成本低廉
  - 适合批量任务
- **特点**：
  - 温度设置：0（确定性输出）
  - 上下文：标准
  - 输出风格：精简直接

### Kimi (Moonshot AI)
- **优势**：
  - 输出详细完整
  - 128k超长上下文
  - 适合复杂推理
  - 文档生成质量高
- **特点**：
  - 温度设置：0.6（创造性输出）
  - 上下文：128k tokens
  - 输出风格：详尽解释

### Qwen3 Coder
- **优势**：
  - 专为agent编码任务优化
  - 原生支持function calling和tool use
  - 代码生成能力出色
  - 长上下文推理（repository级别）
  - 数学和算法能力强
- **特点**：
  - 温度设置：0.3（平衡准确性和创造性）
  - 上下文：32k tokens
  - 输出风格：代码优先
  - 特有功能：execute_python工具

## 技术实现

### Agent架构

每个Agent都实现了相同的核心接口：

```python
class ReactAgent:
    def __init__(self, work_dir, model, knowledge_files, interface):
        # 初始化Agent
        pass
    
    def execute_task(self, task):
        # 执行任务
        pass
```

### 工具系统

所有Agent都支持以下基础工具：
- `read_file` - 读取文件
- `write_file` - 写入文件（覆盖）
- `append_file` - 追加文件
- `list_directory` - 列出目录
- `execute_command` - 执行shell命令

Qwen Agent额外支持：
- `execute_python` - 直接执行Python代码

### 内容长度限制

不同模型的单次内容长度限制：
- **DeepSeek**: write_file 4000字符, append_file 3000字符
- **Kimi**: write_file 4000字符, append_file 3000字符
- **Qwen**: write_file 8000字符, append_file 6000字符

## 选择建议

### 场景推荐

1. **快速原型开发** → DeepSeek
   - 需要快速迭代
   - 成本敏感
   - 标准化任务

2. **复杂文档生成** → Kimi
   - 需要详细解释
   - 教学或文档场景
   - 需要创造性内容

3. **代码开发任务** → Qwen3 Coder
   - 复杂代码生成
   - Agent系统开发
   - 需要代码调试和优化
   - Repository级别的代码理解

### 性能基准

基于NLPL数组分析任务的实测数据：

| 模型 | 执行时间 | 输出大小(Level 4) | 准确性 |
|------|----------|-------------------|--------|
| DeepSeek | 426秒 | 1,596 bytes | ✅ 准确 |
| Kimi | 830秒 | 8,324 bytes | ✅ 准确 |
| Qwen | 待测 | 待测 | 待测 |

## 扩展开发

### 添加新模型

1. 创建新的Agent类文件：`core/your_model_react_agent.py`
2. 实现必要的接口方法
3. 在`demo_nlpl_complete.py`中添加模型选项
4. 更新测试文件

### 自定义工具

在Agent的`_define_tools()`方法中添加新工具定义，并在`_execute_tool()`方法中实现工具逻辑。

## 故障排除

### 常见问题

1. **API密钥未设置**
   - 检查`.env`文件中的密钥配置
   - 确保环境变量名称正确

2. **工具调用失败**
   - 检查模型是否支持function calling
   - 验证工具定义格式是否正确

3. **内容截断**
   - 注意不同模型的字符长度限制
   - 使用append_file分段写入长内容

## 更新日志

- 2024-01 - 添加Qwen3 Coder支持，优化agent编码任务
- 2024-01 - 实现多模型切换功能
- 2024-01 - 初始版本，支持DeepSeek和Kimi