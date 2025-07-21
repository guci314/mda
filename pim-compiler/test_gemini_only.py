#!/usr/bin/env python3
"""
实验：仅使用 Gemini CLI 完成整个编译流程
PIM -> PSM -> Code 全部由 Gemini CLI 完成
"""
import os
import sys
import shutil
import subprocess
import time
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
project_root = Path(__file__).parent.parent
env_file = project_root / ".env"
if env_file.exists():
    load_dotenv(env_file)
    print(f"✓ 已加载环境变量文件: {env_file}")

print("\n实验：仅使用 Gemini CLI 的编译流程")
print("=" * 60)

# 创建实验目录
exp_dir = Path("./experiment_gemini_only")
if exp_dir.exists():
    shutil.rmtree(exp_dir)
exp_dir.mkdir()

pim_dir = exp_dir / "pim"
pim_dir.mkdir()
psm_dir = exp_dir / "psm"
psm_dir.mkdir()
code_dir = exp_dir / "generated"
code_dir.mkdir()

print(f"\n1. 创建目录结构:")
print(f"   - PIM 目录: {pim_dir}")
print(f"   - PSM 目录: {psm_dir}")
print(f"   - 代码目录: {code_dir}")

# 创建 PIM 文件
pim_content = """# 博客系统

## 业务实体

### 文章 (Article)
博客文章实体。

属性：
- 标题：文章标题
- 内容：文章正文（Markdown格式）
- 作者：作者名称
- 标签：文章标签列表
- 发布时间：文章发布时间
- 更新时间：最后更新时间
- 状态：草稿/已发布

### 评论 (Comment)
文章评论。

属性：
- 文章ID：关联的文章
- 作者：评论者名称
- 内容：评论内容
- 创建时间：评论时间

## 业务服务

### 文章服务 (ArticleService)
管理文章的业务操作。

方法：
1. 创建文章（草稿）
2. 发布文章
3. 更新文章
4. 删除文章
5. 获取文章列表（支持分页、标签筛选）
6. 获取文章详情

### 评论服务 (CommentService)
管理评论的业务操作。

方法：
1. 添加评论
2. 删除评论
3. 获取文章的评论列表
"""

pim_file = pim_dir / "blog_system.md"
with open(pim_file, 'w', encoding='utf-8') as f:
    f.write(pim_content)

print(f"\n2. 创建 PIM 文件: {pim_file}")

# 步骤 1: 使用 Gemini CLI 生成 PSM
print("\n3. 使用 Gemini CLI 生成 PSM...")

psm_prompt = f"""你是一个专业的软件架构师，精通模型驱动架构（MDA）。

我有一个平台无关模型（PIM）文件，位于：pim/blog_system.md

请将这个 PIM 转换为 FastAPI 平台的平台特定模型（PSM），并保存到 psm/blog_system_psm.md

要求：
1. 读取 PIM 文件，理解业务需求
2. 生成详细的 PSM 文档，包含：
   - 技术架构说明（FastAPI + SQLAlchemy + PostgreSQL）
   - 数据模型设计（包含具体字段类型、索引、关系）
   - API 接口设计（RESTful，包含路由、请求/响应格式）
   - 业务逻辑实现方案
   - 项目结构说明
   - 依赖列表
3. 使用 Markdown 格式，包含代码示例
4. 保存到 psm/blog_system_psm.md

注意：
- 使用最新版本的库（Pydantic v2, SQLAlchemy 2.0）
- 遵循 FastAPI 最佳实践
- 考虑性能和安全性
"""

# 准备环境变量
env = os.environ.copy()
if "GOOGLE_API_KEY" in env and "GEMINI_API_KEY" in env:
    del env["GOOGLE_API_KEY"]

gemini_cli_path = "/home/guci/.nvm/versions/node/v22.17.0/bin/gemini"
if not os.path.exists(gemini_cli_path):
    gemini_cli_path = "gemini"

model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")

# 调用 Gemini CLI 生成 PSM
start_time = time.time()
result = subprocess.run(
    [gemini_cli_path, "-m", model, "-p", psm_prompt, "-y"],
    capture_output=True,
    text=True,
    env=env,
    cwd=exp_dir,
    timeout=300  # 5分钟超时
)

psm_time = time.time() - start_time
print(f"\n   PSM 生成耗时: {psm_time:.2f} 秒")
print(f"   返回码: {result.returncode}")

# 检查 PSM 文件
psm_file = psm_dir / "blog_system_psm.md"
if psm_file.exists():
    print(f"   ✓ PSM 文件已生成")
    size = psm_file.stat().st_size
    print(f"   文件大小: {size} 字节")
else:
    print(f"   ✗ PSM 文件未找到")
    sys.exit(1)

# 步骤 2: 使用 Gemini CLI 生成代码
print("\n4. 使用 Gemini CLI 生成代码...")

code_prompt = f"""你是一个专业的 FastAPI 开发工程师。

我有一个平台特定模型（PSM）文件，位于：psm/blog_system_psm.md

请根据这个 PSM 文件生成完整的 FastAPI 代码实现。

要求：
1. 读取 PSM 文件，理解所有技术细节
2. 在 generated/ 目录下创建完整的项目结构
3. 实现所有功能：
   - 数据模型（SQLAlchemy）
   - Pydantic schemas
   - API 路由
   - 业务逻辑服务
   - 数据库配置
   - 主应用文件
4. 生成 requirements.txt
5. 生成 README.md
6. 生成基础的单元测试

注意：
- 使用 Pydantic v2（pattern 而不是 regex）
- 使用 SQLAlchemy 2.0 语法
- 包含错误处理和日志
- 遵循 PEP 8 规范
"""

# 调用 Gemini CLI 生成代码
start_time = time.time()
result = subprocess.run(
    [gemini_cli_path, "-m", model, "-p", code_prompt, "-y"],
    capture_output=True,
    text=True,
    env=env,
    cwd=exp_dir,
    timeout=600  # 10分钟超时
)

code_time = time.time() - start_time
print(f"\n   代码生成耗时: {code_time:.2f} 秒")
print(f"   返回码: {result.returncode}")

# 检查生成的文件
print(f"\n5. 检查生成的文件...")

if code_dir.exists():
    all_files = list(code_dir.rglob("*"))
    py_files = [f for f in all_files if f.suffix == ".py" and f.is_file()]
    
    print(f"\n   ✓ 成功生成文件:")
    print(f"   - 总文件数: {len([f for f in all_files if f.is_file()])}")
    print(f"   - Python 文件数: {len(py_files)}")
    
    # 检查关键文件
    key_files = [
        "requirements.txt",
        "README.md",
        "main.py",
        "models/article.py",
        "schemas/article.py",
        "api/articles.py",
        "services/article_service.py"
    ]
    
    print(f"\n   关键文件检查:")
    for key_file in key_files:
        found = False
        for f in all_files:
            if key_file in str(f):
                if f.is_file():
                    size = f.stat().st_size
                    print(f"   ✓ {key_file} ({size} 字节)")
                    found = True
                    break
        if not found:
            print(f"   ✗ {key_file} 未找到")

# 显示总结
print(f"\n6. 实验总结:")
print(f"   - PSM 生成时间: {psm_time:.2f} 秒")
print(f"   - 代码生成时间: {code_time:.2f} 秒")
print(f"   - 总时间: {psm_time + code_time:.2f} 秒")
print(f"\n   相比原方案（DeepSeek + Gemini）:")
print(f"   - 只需要一个 API（Gemini）")
print(f"   - 减少了网络延迟")
print(f"   - 保持了上下文一致性")

print(f"\n实验完成！")
print(f"实验目录: {exp_dir}")