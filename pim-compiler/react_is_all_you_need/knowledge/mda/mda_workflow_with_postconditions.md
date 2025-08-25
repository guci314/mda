# MDA工作流程与后置断言

## 核心原则

每个MDA步骤都必须定义明确的**后置断言**（成功条件）。后置断言失败意味着任务失败，需要触发自适应分解或修复。

## MDA工作流步骤与后置断言

### 步骤1：PIM到PSM转换

**任务**：读取PIM文件，生成PSM文档

**后置断言**：
- ✅ PSM文件存在于指定路径
- ✅ PSM包含所有5个必需章节（Domain Models, Service Layer, REST API Design, Application Configuration, Testing Specifications）
- ✅ 每个PIM实体在PSM中都有对应的定义
- ✅ PSM文档格式符合Markdown规范

**验证命令**：
```bash
# 检查文件存在
test -f psm_output.md && echo "PSM文件存在"

# 检查章节完整性
grep -q "Domain Models" psm_output.md && \
grep -q "Service Layer" psm_output.md && \
grep -q "REST API Design" psm_output.md && \
grep -q "Application Configuration" psm_output.md && \
grep -q "Testing Specifications" psm_output.md && \
echo "所有章节完整"
```

### 步骤2：生成项目结构

**任务**：根据PSM创建FastAPI项目目录结构

**后置断言**：
- ✅ 目录结构创建完成：app/, tests/, app/api/, app/models/, app/services/
- ✅ requirements.txt文件存在且包含FastAPI, SQLAlchemy, Pydantic
- ✅ __init__.py文件在所有Python包目录中存在

**验证命令**：
```bash
# 检查目录结构
test -d app && test -d tests && test -d app/api && test -d app/models && test -d app/services && \
echo "目录结构完整"

# 检查requirements.txt
grep -q "fastapi" requirements.txt && \
grep -q "sqlalchemy" requirements.txt && \
grep -q "pydantic" requirements.txt && \
echo "依赖定义完整"
```

### 步骤3：生成数据模型

**任务**：生成SQLAlchemy模型和Pydantic schemas

**后置断言**：
- ✅ app/models.py存在且包含所有实体的SQLAlchemy模型
- ✅ app/schemas.py存在且每个实体有Create, Update, Response schemas
- ✅ Python语法正确（可通过compile验证）
- ✅ 所有模型继承自正确的基类

**验证命令**：
```python
# Python语法验证
import py_compile
try:
    py_compile.compile('app/models.py', doraise=True)
    py_compile.compile('app/schemas.py', doraise=True)
    print("Python语法正确")
except:
    print("语法错误")
```

### 步骤4：生成API路由

**任务**：为每个实体生成CRUD路由

**后置断言**：
- ✅ 每个实体有对应的路由文件 app/api/{entity}.py
- ✅ 每个路由文件包含5个基本操作（list, get, create, update, delete）
- ✅ 路由使用正确的HTTP方法和状态码
- ✅ 路由函数有正确的类型注解

**验证命令**：
```bash
# 检查路由文件
for entity in user product order; do
    test -f "app/api/${entity}.py" || exit 1
    grep -q "@router.get" "app/api/${entity}.py" || exit 1
    grep -q "@router.post" "app/api/${entity}.py" || exit 1
    grep -q "@router.put" "app/api/${entity}.py" || exit 1
    grep -q "@router.delete" "app/api/${entity}.py" || exit 1
done
echo "所有路由完整"
```

### 步骤5：生成主应用

**任务**：生成app/main.py整合所有组件

**后置断言**：
- ✅ app/main.py存在
- ✅ FastAPI应用实例已创建
- ✅ 所有路由已注册（include_router）
- ✅ CORS中间件已配置
- ✅ 应用可以成功启动（uvicorn不报错）

**验证命令**：
```bash
# 检查应用启动
timeout 5 uvicorn app.main:app --host 0.0.0.0 --port 8000 &
sleep 3
curl -s http://localhost:8000/docs > /dev/null && echo "应用启动成功"
pkill uvicorn
```

### 步骤6：生成测试代码

**任务**：生成pytest测试用例

**后置断言**：
- ✅ tests/目录包含测试文件
- ✅ 每个API端点至少有一个测试用例
- ✅ 测试文件语法正确
- ✅ conftest.py包含必要的fixtures

**验证命令**：
```bash
# 检查测试文件
test -f tests/conftest.py && \
ls tests/test_*.py | wc -l | grep -q "^[1-9]" && \
echo "测试文件存在"
```

### 步骤7：运行测试验证

**任务**：执行所有测试确保功能正确

**后置断言**：
- ✅ pytest执行返回码为0
- ✅ 输出包含"0 failed"
- ✅ 所有测试通过（100% passed）
- ✅ 没有import错误

**验证命令**：
```bash
# 运行测试
pytest tests/ -v
# 检查结果
if [ $? -eq 0 ]; then
    echo "所有测试通过"
else
    echo "测试失败，需要调试"
fi
```

## 失败处理策略

### 当后置断言失败时

1. **识别失败类型**：
   - 完全失败：任务根本没有执行
   - 部分失败：部分内容生成但不完整
   - 质量失败：内容存在但不符合要求

2. **选择处理策略**：
   - 如果是模型能力问题 → 触发任务分解
   - 如果是环境问题 → 修复环境后重试
   - 如果是逻辑错误 → 调用调试Agent

3. **分解示例**：
   ```
   原任务：生成所有API路由
   失败：输出被截断
   
   分解为：
   - 子任务1：生成User实体的路由
   - 子任务2：生成Product实体的路由
   - 子任务3：生成Order实体的路由
   - 子任务4：在main.py中注册所有路由
   ```

## 后置断言设计原则

1. **可测量**：必须能通过命令或代码验证
2. **具体**：避免"代码质量好"这样的模糊描述
3. **原子性**：每个断言只验证一个方面
4. **快速**：验证应该在几秒内完成

## 与自适应分解的集成

当后置断言失败时，系统会：
1. 记录失败的断言和原因
2. 参考 `adaptive_task_decomposition.md` 知识
3. 根据失败类型选择分解策略
4. 为每个子任务生成新的后置断言
5. 继续执行直到所有断言满足

## 示例：处理Kimi的能力限制

```markdown
场景：Kimi执行"生成完整FastAPI应用"任务

第1次尝试：
- 执行：生成完整应用
- 后置断言检查：app/main.py不完整，路由注册缺失
- 结果：失败

触发分解：
- 子任务1：生成基础应用结构
  后置断言：app/main.py存在，FastAPI()实例创建
  
- 子任务2：逐个生成路由文件
  后置断言：每个路由文件存在且包含CRUD操作
  
- 子任务3：在main.py中注册路由
  后置断言：所有include_router语句存在

第2次尝试（分解后）：
- 执行子任务1：成功 ✅
- 执行子任务2：成功 ✅
- 执行子任务3：成功 ✅
- 最终验证：所有后置断言满足 ✅
```

## 总结

后置断言是MDA工作流的**质量保证机制**：
- 每个步骤都有明确的成功标准
- 失败立即可检测
- 自动触发适应性调整
- 确保最终交付质量

这种方式让即使是能力较弱的模型（如Kimi）也能通过分解和重试最终完成复杂任务。