# 调用 Gemini CLI 修复代码的正确方法

## 概述

Gemini CLI 是 Google 推出的开源 AI 代理，能够直接在终端中使用 Gemini 的能力。它使用推理和行动（ReAct）循环，结合内置工具和本地/远程 MCP 服务器来完成复杂的任务，如修复错误、创建新功能和提高测试覆盖率。

## 核心能力

### 1. 自修复能力
Gemini CLI 最强大的功能之一是自修复能力。如果它引入了缺陷或错误配置，只要它能访问终端输出或日志，通常能够自行修复。

### 2. 测试驱动修复
- 自动生成 pytest 测试用例
- 识别测试失败原因
- 提供修复建议并自动应用

### 3. 上下文感知
- 使用 1M token 的超大上下文窗口
- 能够理解整个代码库的结构
- 基于提示构建多步骤计划

## 正确的调用方法

### 方法 1：在项目目录中使用交互模式（推荐）

```bash
# 1. 进入生成的代码目录
cd /path/to/generated/code

# 2. 启动 Gemini CLI
gemini

# 3. 告诉 Gemini 测试失败的情况
> 运行 pytest test_main.py 失败了，提示 "ModuleNotFoundError: No module named 'email_validator'"，请修复这个问题

# 4. Gemini 会：
#    - 分析错误信息
#    - 查看相关代码文件
#    - 自动运行测试
#    - 识别根本原因
#    - 提供修复方案
#    - 应用修复（需要确认）
```

### 方法 2：使用 -p 参数进行非交互式调用

```bash
# 在代码目录中直接执行修复命令
cd /path/to/generated/code

# 传递详细的修复请求
gemini -p "pytest test_main.py 失败，错误是 'ModuleNotFoundError: No module named email_validator'。请：
1. 分析为什么会缺少这个模块
2. 检查 requirements.txt 是否包含必要的依赖
3. 修复代码或更新依赖
4. 重新运行测试确保通过"
```

### 方法 3：编程集成（适合 CI/CD）- 推荐方式

```python
import subprocess
import os
from pathlib import Path

def fix_with_gemini_cli(project_dir: str, test_error: str, error_type: str = "pytest"):
    """使用 Gemini CLI 修复代码错误 - 使用 cwd 参数"""
    
    # 准备环境变量
    env = os.environ.copy()
    
    # 如果同时存在 GOOGLE_API_KEY 和 GEMINI_API_KEY，只保留 GEMINI_API_KEY
    if "GOOGLE_API_KEY" in env and "GEMINI_API_KEY" in env:
        del env["GOOGLE_API_KEY"]
    
    # 根据错误类型构建提示
    if error_type == "lint":
        fix_prompt = f"""在当前目录中有 Python 代码需要修复 lint 错误。

错误信息：
{test_error}

请执行以下步骤：
1. 根据错误信息找到对应的文件和行号
2. 修复所有报告的问题：
   - E501 (line too long): 将长行拆分到多行
   - F841 (unused variable): 删除未使用的变量或使用它
   - F821 (undefined name): 定义缺失的变量或导入
3. 对于 Pydantic 的 'regex' 参数，改为 'pattern'
4. 修改文件后，再次运行 flake8 确认没有错误"""
    
    elif error_type == "pytest":
        fix_prompt = f"""运行 pytest 失败，错误信息：
{test_error}

请：
1. 分析错误原因
2. 如果缺少依赖（如 email_validator），创建或更新 requirements.txt
3. 如果是代码错误，修复相关文件
4. 如果是测试错误，修复测试文件
5. 重新运行 pytest 确保所有测试通过

注意：
- 对于 Pydantic，使用 'pattern' 而不是 'regex'
- 对于 SQLAlchemy，从 sqlalchemy.orm 导入 declarative_base
- 确保所有导入路径正确"""
    
    else:
        fix_prompt = f"修复以下错误：\n{test_error}"
    
    # 构建命令
    gemini_cli_path = "/home/guci/.nvm/versions/node/v22.17.0/bin/gemini"
    if not os.path.exists(gemini_cli_path):
        gemini_cli_path = "gemini"  # 使用系统 PATH
    
    model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
    
    # 调用 Gemini CLI（使用 cwd 参数，添加 -y 自动确认）
    result = subprocess.run(
        [gemini_cli_path, "-m", model, "-p", fix_prompt, "-y"],
        capture_output=True,
        text=True,
        env=env,
        cwd=project_dir,  # 关键：使用 cwd 参数指定工作目录
        timeout=300  # 5分钟超时
    )
    
    return result.returncode == 0
```

## 最佳实践

### 1. 提供充分的上下文
```bash
# 好的提示
gemini -p "运行 pytest test_user.py::test_create_user 失败，错误是 'email_validator' 模块未找到。这是一个 FastAPI 项目，使用 Pydantic 进行数据验证。"

# 不够好的提示
gemini -p "测试失败了，请修复"
```

### 2. 让 Gemini 自己运行测试
Gemini CLI 能够：
- 自动识别项目中的测试框架（pytest、unittest 等）
- 运行特定的测试文件或测试函数
- 查看测试输出并理解失败原因
- 迭代修复直到测试通过

### 3. 处理依赖问题
对于缺少依赖的情况，Gemini 会：
```python
# 1. 检查 requirements.txt
# 2. 识别缺失的包（如 email-validator）
# 3. 建议安装命令或更新 requirements.txt
# 4. 可能会建议使用 pip install pydantic[email] 而不是单独安装
```

### 4. 处理代码质量问题
```bash
# 修复 lint 错误
gemini -p "运行 flake8 发现多个 E501 错误（行太长），请修复这些格式问题"

# 修复类型错误
gemini -p "Pydantic 报错说 'regex' 参数已弃用，应该使用 'pattern'，请更新所有相关代码"
```

## 实际案例

### 案例 1：修复 Pydantic 版本兼容性问题
```bash
cd /tmp/generated_code
gemini

> schemas.py 中使用了 regex 参数，但新版 Pydantic 需要 pattern 参数，请修复

# Gemini 会：
# 1. 打开 schemas.py
# 2. 找到所有使用 regex 的地方
# 3. 替换为 pattern
# 4. 运行测试验证修复
```

### 案例 2：修复测试依赖问题
```bash
> pytest 失败，提示缺少 email_validator 模块

# Gemini 会：
# 1. 分析错误堆栈
# 2. 理解这是 Pydantic EmailStr 类型的依赖
# 3. 建议运行 pip install "pydantic[email]"
# 4. 或者修改代码使用普通 str 类型
# 5. 重新运行测试确认修复
```

### 案例 3：修复多个相关问题
```bash
> 代码有多个问题：
> 1. 缺少 email_validator
> 2. SQLAlchemy 导入路径过时
> 3. 一些行超过 79 字符
> 请全部修复并确保测试通过

# Gemini 会制定多步骤计划并逐一解决
```

## 集成到编译器工作流

### 更智能的自动修复实现
```python
def _fix_with_gemini_advanced(self, code_dir: str, error_info: Dict[str, Any]):
    """使用 Gemini CLI 进行智能修复"""
    
    # 保存当前目录
    original_dir = os.getcwd()
    
    try:
        # 切换到代码目录（重要！）
        os.chdir(code_dir)
        
        # 根据错误类型构建不同的提示
        if "lint" in error_info["type"]:
            prompt = f"修复以下 lint 错误：\n{error_info['message']}"
        elif "test" in error_info["type"]:
            prompt = f"""
            测试 {error_info['test_file']} 失败：
            {error_info['message']}
            
            请：
            1. 运行失败的测试
            2. 分析并修复问题
            3. 确保所有测试通过
            """
        else:
            prompt = f"修复错误：{error_info['message']}"
        
        # 调用 Gemini CLI
        result = subprocess.run(
            ["gemini", "-p", prompt, "-m", "gemini-2.0-flash-exp"],
            capture_output=True,
            text=True,
            timeout=300  # 5分钟超时
        )
        
        return result.returncode == 0
        
    finally:
        # 恢复原始目录
        os.chdir(original_dir)
```

## 注意事项

1. **始终在正确的目录中运行**
   - Gemini CLI 需要在项目根目录或代码目录中运行
   - 它会基于当前目录理解项目结构

2. **提供清晰的错误信息**
   - 包含完整的错误堆栈
   - 说明是哪个测试失败
   - 提供相关的上下文信息

3. **允许 Gemini 访问必要的工具**
   - 确保 pytest、flake8 等工具已安装
   - Gemini 需要能够运行这些工具来验证修复

4. **生产环境使用建议**
   - 在 CI/CD 中使用时，考虑只读模式进行分析
   - 人工审核 Gemini 的修改建议
   - 设置合理的超时时间

## 限制和使用配额

- 免费版本：每分钟 60 次请求，每天 1,000 次请求
- 上下文窗口：100 万 token
- 模型：Gemini 2.5 Pro

## 新发现：使用 Gemini CLI 从 PSM 生成代码

### 实验成果
我们发现 Gemini CLI 不仅可以修复代码，还能够根据 PSM（平台特定模型）文件生成完整的代码实现。

### 方法：基于文件位置的代码生成

```python
def generate_code_from_psm_with_gemini(psm_file: Path, output_dir: Path) -> bool:
    """使用 Gemini CLI 从 PSM 文件生成代码"""
    
    # 准备工作目录
    work_dir = psm_file.parent.parent  # PSM 文件的上级目录
    
    # 构建提示
    prompt = f"""你是一个专业的 {platform} 开发工程师。

我有一个平台特定模型（PSM）文件，位于：{psm_file.relative_to(work_dir)}

请你根据这个 PSM 文件生成完整的 {platform} 代码实现。

要求：
1. 读取 PSM 文件了解需求
2. 在 {output_dir.relative_to(work_dir)} 目录下创建完整的项目结构
3. 实现所有的模型、API、服务和配置
4. 生成 requirements.txt 文件
5. 确保代码可以直接运行

注意：
- 使用最新版本的库语法（Pydantic v2+, SQLAlchemy 2.0+）
- 包含完整的错误处理和日志记录
- 实现必要的安全功能（如密码哈希）
- 生成完整的测试文件

请开始实现。
"""
    
    # 准备环境变量
    env = os.environ.copy()
    if "GOOGLE_API_KEY" in env and "GEMINI_API_KEY" in env:
        del env["GOOGLE_API_KEY"]
    
    # 调用 Gemini CLI
    result = subprocess.run(
        ["gemini", "-m", "gemini-2.0-flash-exp", "-p", prompt, "-y"],
        capture_output=True,
        text=True,
        env=env,
        cwd=work_dir,  # 在包含 PSM 文件的目录中执行
        timeout=600    # 10分钟超时
    )
    
    return result.returncode == 0
```

### 实验结果
在我们的实验中，Gemini CLI 成功地：
1. 读取了指定位置的 PSM 文件
2. 生成了完整的 FastAPI 项目结构（16 个文件）
3. 实现了所有指定的功能
4. 使用了正确的现代语法（Pydantic v2 的 pattern 参数）
5. 创建了完整的 requirements.txt

生成的项目结构：
```
generated/
├── requirements.txt
├── src/
│   ├── __init__.py
│   ├── main.py              # FastAPI 应用入口
│   ├── models/
│   │   ├── __init__.py
│   │   └── user.py          # SQLAlchemy 模型
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── user.py          # Pydantic schemas
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── users.py     # API 路由
│   ├── services/
│   │   ├── __init__.py
│   │   ├── security.py      # 安全相关服务
│   │   └── user_service.py  # 业务逻辑
│   └── core/
│       ├── __init__.py
│       ├── config.py        # 配置管理
│       └── database.py      # 数据库连接
```

### 集成到编译器的新架构

这个发现可以简化编译器的架构：

```python
class GeminiCompiler(BaseCompiler):
    """使用 Gemini CLI 的新型编译器"""
    
    def compile(self, pim_file: Path) -> CompilationResult:
        # 步骤 1: 使用 DeepSeek 将 PIM 转换为 PSM
        psm_content = self._transform_pim_to_psm(pim_file)
        
        # 步骤 2: 保存 PSM 到文件
        psm_file = self.output_dir / "psm" / f"{pim_file.stem}_psm.md"
        psm_file.parent.mkdir(exist_ok=True)
        psm_file.write_text(psm_content)
        
        # 步骤 3: 使用 Gemini CLI 生成代码
        code_dir = self.output_dir / "generated"
        success = self._generate_code_with_gemini(psm_file, code_dir)
        
        # 步骤 4: 运行测试和修复（如果需要）
        if success and self.config.auto_test:
            self._run_tests_and_fix(code_dir)
        
        return CompilationResult(
            success=success,
            psm_file=psm_file,
            code_dir=code_dir
        )
```

### 优势
1. **简化架构**：不需要在 Python 中解析和生成代码
2. **更强大的生成能力**：Gemini CLI 可以生成完整的项目结构
3. **更好的代码质量**：生成的代码包含错误处理、日志等最佳实践
4. **易于调试**：PSM 文件保存在磁盘上，便于查看和调试

## 总结

Gemini CLI 的正确使用方法是：
1. 在生成的代码目录中运行
2. 提供详细的错误信息和上下文
3. 让它自主运行测试和验证修复
4. 利用其自修复能力处理连锁问题
5. 将其视为一个需要指导的初级开发者
6. **新发现**：可以通过文件位置引用让 Gemini CLI 读取 PSM 文件并生成完整代码

通过正确使用 Gemini CLI，可以大大提高代码修复的效率和准确性，同时简化整个编译流程。