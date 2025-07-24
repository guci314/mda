# DeepSeek CLI 使用指南

## 安装和配置

### 1. 配置 API Key

```bash
# 方式1：使用交互式配置
python -m deepseek_cli setup

# 方式2：使用快捷命令（如果在项目根目录）
./deepseek setup

# 方式3：手动设置环境变量
export DEEPSEEK_API_KEY="your-api-key"
```

### 2. 查看价格信息

```bash
python -m deepseek_cli setup --prices
# 或
./deepseek setup --prices
```

## 命令行使用

### 运行演示

```bash
# 查看功能演示
python -m deepseek_cli demo
# 或
./deepseek demo
```

### 运行测试

```bash
# 运行完整测试
python -m deepseek_cli test
# 或
./deepseek test
```

### 执行任务

```bash
# 执行任意任务
python -m deepseek_cli run "你的任务描述"

# 详细输出模式
python -m deepseek_cli run "分析 main.py 的代码质量" -v

# 使用快捷命令
./deepseek run "创建用户认证系统"
```

### PIM 到 PSM 转换

```bash
# 基本转换（默认 FastAPI）
python -m deepseek_cli convert models/user.md

# 指定输出文件
python -m deepseek_cli convert models/user.md -o output/user_psm.md

# 指定目标平台
python -m deepseek_cli convert models/user.md -p django

# 使用快捷命令
./deepseek convert examples/hospital.md -p flask
```

## Python API 使用

### 基础用法

```python
from deepseek_cli import DeepSeekCLI

# 创建实例
cli = DeepSeekCLI()

# 执行任务
success, message = cli.execute_task("你的任务")

if success:
    print("任务完成！")
else:
    print(f"任务失败: {message}")
```

### 获取执行详情

```python
from deepseek_cli import DeepSeekCLI

cli = DeepSeekCLI()
success, message = cli.execute_task("分析代码")

# 获取执行摘要
summary = cli.get_execution_summary()
print(f"总动作数: {summary['total_actions']}")
print(f"成功动作: {summary['successful_actions']}")

# 查看执行日志
for action in summary['execution_log']:
    print(f"{action['type']}: {action['description']}")
```

### 任务规划

```python
from deepseek_cli import DeepSeekLLM

llm = DeepSeekLLM()
plan = llm.plan("创建完整的用户管理系统")

print(f"执行步骤 ({len(plan.steps)} 步):")
for i, step in enumerate(plan.steps):
    print(f"{i+1}. {step}")
```

### 代码分析

```python
from deepseek_cli import DeepSeekLLM

llm = DeepSeekLLM()

# 读取代码
with open("app.py", "r") as f:
    code = f.read()

# 分析代码
result = llm.analyze_content(
    code,
    "分析代码质量，找出潜在问题和优化建议"
)

print("分析结果:", result)
```

### 代码生成

```python
from deepseek_cli import DeepSeekLLM

llm = DeepSeekLLM()

# 生成代码
code = llm.generate_code(
    "创建一个 FastAPI 用户认证端点，支持 JWT",
    context={"framework": "fastapi", "auth": "jwt"}
)

print(code)
```

## 批处理示例

### 批量转换 PIM 文件

```python
import glob
from deepseek_cli import DeepSeekCLI

# 找到所有 PIM 文件
pim_files = glob.glob("models/*.md")

# 批量转换
for pim_file in pim_files:
    cli = DeepSeekCLI()
    psm_file = pim_file.replace(".md", "_psm.md")
    
    task = f"将 {pim_file} 转换为 FastAPI PSM，输出到 {psm_file}"
    success, message = cli.execute_task(task)
    
    print(f"{pim_file}: {'✅' if success else '❌'} {message}")
```

### 并发处理

```python
import concurrent.futures
from deepseek_cli import DeepSeekCLI

def convert_pim(pim_file):
    cli = DeepSeekCLI()
    psm_file = pim_file.replace(".md", "_psm.md")
    task = f"将 {pim_file} 转换为 FastAPI PSM，输出到 {psm_file}"
    return cli.execute_task(task)

# 并发转换多个文件
files = ["user.md", "product.md", "order.md"]
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
    results = list(executor.map(convert_pim, files))

for file, (success, message) in zip(files, results):
    print(f"{file}: {'✅' if success else '❌'}")
```

## 环境变量

支持的环境变量：

- `DEEPSEEK_API_KEY`: DeepSeek API Key（必需）
- `DEEPSEEK_BASE_URL`: API 地址（可选，默认 https://api.deepseek.com）
- `DEEPSEEK_MODEL`: 模型名称（可选，默认 deepseek-chat）

## 故障排除

### API Key 错误

```bash
# 重新配置
python -m deepseek_cli setup

# 检查环境变量
echo $DEEPSEEK_API_KEY
```

### 网络超时

```python
# 增加超时时间
cli = DeepSeekCLI()
cli.llm.timeout = 120  # 2分钟
```

### Token 限制

```python
# 分块处理大文件
def process_large_file(file_path, chunk_size=4000):
    with open(file_path, 'r') as f:
        content = f.read()
    
    # 分块
    chunks = [content[i:i+chunk_size] 
              for i in range(0, len(content), chunk_size)]
    
    # 处理每个块
    for i, chunk in enumerate(chunks):
        cli = DeepSeekCLI()
        cli.execute_task(f"处理第 {i+1} 部分内容: {chunk[:50]}...")
```

## 更多信息

- 详细文档：查看 `deepseek_cli/README.md`
- API 参考：查看源代码 `deepseek_cli/core.py`
- 示例代码：运行 `python -m deepseek_cli demo`