# GEMINI.md 设计说明

## 设计原则

Gemini CLI 是一个通用的 AI 编程助手，它不需要了解 PIM Compiler 的内部实现。因此：

1. **不在 PIM Compiler 项目根目录创建 GEMINI.md**
   - Gemini CLI 在生成代码时不会读取编译器项目的文件
   - 避免混淆和不必要的耦合

2. **只在生成的项目中创建 GEMINI.md**
   - 每个生成的项目都有自己的 GEMINI.md
   - 包含通用的 Python/FastAPI 编程指导
   - 不包含 PIM Compiler 相关的内容

## GEMINI.md 内容

生成项目的 GEMINI.md 应该包含：

### 1. 项目上下文
- 项目类型（FastAPI）
- 技术栈（SQLAlchemy, Pydantic v2）
- 数据库配置

### 2. 常见问题和解决方案
- 导入错误
- 循环依赖
- 缺失的依赖包
- 数据库类型问题
- Pydantic v2 兼容性
- 测试技巧（如 curl --noproxy）

### 3. 修复优先级
- 语法错误（最高优先级）
- 导入错误
- 类型错误
- 代码风格警告（最低优先级）

### 4. 项目结构说明
- 标准的 FastAPI 项目结构
- 各个目录的用途

### 5. 快速启动指南
- 安装依赖
- 初始化数据库
- 启动应用

## 为什么这样设计？

1. **关注点分离**
   - Gemini CLI 只需要知道如何处理 Python/FastAPI 代码
   - 不需要了解 MDA、PIM、PSM 等概念

2. **通用性**
   - 生成的项目可以独立于 PIM Compiler 存在
   - 任何了解 FastAPI 的开发者都能理解 GEMINI.md 的内容

3. **维护性**
   - 更新通用编程知识比更新特定工具知识更容易
   - 减少了文档维护的复杂度

## 实现细节

在 `pure_gemini_compiler.py` 中：

```python
def _create_project_gemini_md(self, code_dir: Path) -> None:
    """为生成的项目创建 GEMINI.md 文件
    
    注意：这个文件是为了指导 Gemini CLI 修复生成的代码，
    包含的是通用的 Python/FastAPI 编程知识，而不是 PIM Compiler 特定的知识。
    """
```

这个方法在编译过程的早期被调用，确保 Gemini CLI 在后续步骤中能够读取到适当的指导。