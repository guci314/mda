# 知识库

## 元知识
- **React规则循环**：使用状态变量（code_generated, test_failed_count, debug_attempts, current_task）驱动执行，IF-THEN规则触发工具调用
- **测试验证策略**：先运行pytest发现失败，再针对性修复；测试失败时优先检查语法错误（缩进、async/await、方法定义）
- **调试模式**：当自动修复工具失效时，手动重写整个文件比局部修补更高效
- **状态跟踪**：使用coordinator_todo.json记录任务状态，避免重复执行

## 原理与设计
- **PSM到FastAPI的映射**：PSM文件定义领域模型，自动生成包含models、repositories、routers、schemas、services的完整FastAPI结构
- **测试驱动修复**：测试失败触发调试循环，直到test_failed_count == 0
- **分层架构**：app/目录下按功能分层（models/数据模型, repositories/数据访问, services/业务逻辑, routers/HTTP接口）

## 接口与API
- **pytest配置**：pytest.ini定义测试配置，tests/目录包含测试文件
- **测试工具**：使用AsyncClient进行异步API测试，@pytest.mark.asyncio标记异步测试
- **FastAPI测试模式**：测试文件使用client.post("/reservations/", json=data)进行HTTP调用
- **状态文件**：coordinator_todo.json格式：{"code_generated": bool, "test_failed_count": int, "debug_attempts": int, "current_task": str}

## 实现细节（需验证）
- **测试文件位置**：tests/test_reservations.py（可能已变化）
- **常见测试错误**：
  - 缺少async def导致语法错误
  - 缩进混乱（方法嵌套错误）
  - 重复的装饰器（如@pytest.mark.asyncio）
  - 未定义变量（如isbn）
- **修复策略**：完全重写测试文件比局部修复更可靠
- **目录结构**：output/mda_dual_agent_demo/包含app/、tests/、pytest.ini

## 用户偏好与项目特点
- **100%测试通过**：严格的成功标准（test_failed_count == 0）
- **React式执行**：条件反射式规则执行，不解释"为什么"
- **PSM驱动**：从PSM文件自动生成完整应用，无需手动编码
- **调试循环**：测试失败→调试→再测试，直到通过