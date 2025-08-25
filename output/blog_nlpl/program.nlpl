程序: PSM文档生成任务
  目标: 根据PIM生成完整的PSM文档

  状态:
    输入:
      pim_file: null                              # PIM文件路径
      psm_file: "output_psm.md"                   # 目标PSM文件名
      project_name: null                          # 项目名称（从PIM中提取）
      platform_stack: "FastAPI + PostgreSQL + SQLAlchemy 2.0"  # 默认技术栈
    进度:
      当前步骤: 0                                  # 当前执行的步骤
      已完成步骤: []                              # 已完成的步骤列表
      内容缓存: {}                                # 各章节内容缓存
    输出:
      psm_内容: ""                                # 完整的PSM文档内容
      验证结果: null                              # 章节完整性验证
    完成: false

  必需章节:
    - "Domain Models"                             # 领域模型
    - "Service Layer"                             # 服务层  
    - "REST API Design"                           # API设计
    - "Application Configuration"                 # 应用配置
    - "Testing Specifications"                    # 测试规范

  主流程:
    步骤1_读取分析PIM:
      动作: 读取并分析PIM文件
      子任务:
        - 读取PIM文件内容
        - 识别项目名称和描述
        - 分析领域实体和关系
        - 识别业务规则和约束
        - 使用默认技术栈 FastAPI (可根据PIM内容调整)
      工具: read_file
      参数: 状态.输入.pim_file
      输出:
        - 状态.输入.pim_内容
        - 状态.输入.project_name
        - 状态.输入.platform_stack（默认: FastAPI + PostgreSQL + SQLAlchemy 2.0）
      失败时: 报告错误并终止

    步骤2_生成文档头:
      动作: 创建PSM文档头部
      策略: 根据PIM内容动态生成
      内容模板: |
        # [项目名称] PSM (Platform Specific Model)
        
        基于 [技术栈] 的 [项目描述]
        
        生成时间: [当前时间]
        基于PIM: [pim_file]
      保存到: 状态.输出.psm_内容
      更新: 状态.进度.当前步骤 = 2

    步骤3_生成领域模型:
      动作: 基于PIM生成Domain Models章节
      策略: 
        - 从PIM中提取所有实体定义
        - 转换为SQLAlchemy 2.0 ORM模型
        - 生成PostgreSQL数据库表结构
        - 添加关系映射（一对多、多对多等）
        - 生成Pydantic验证模式
      内容结构: |
        ## 1. Domain Models（领域模型）
        
        ### 1.1 Entity Definitions（实体定义）
        [根据PIM中的实体生成SQLAlchemy模型]
        
        ### 1.2 Schema Definitions（模式定义）
        [生成Pydantic验证模式用于FastAPI]
        
        ### 1.3 Relationships（关系映射）
        [定义实体间的relationship和ForeignKey]
        
        ### 1.4 Constraints（约束条件）
        [唯一性、非空、检查约束等]
      追加到: 状态.输出.psm_内容
      更新: 
        - 状态.进度.已完成步骤.添加("Domain Models")
        - 状态.进度.当前步骤 = 3

    步骤4_生成服务层:
      动作: 基于PIM生成Service Layer章节
      策略:
        - 从PIM中提取业务操作
        - 为每个实体生成服务类
        - 实现CRUD操作
        - 添加业务逻辑方法
        - 包含事务管理
      内容结构: |
        ## 2. Service Layer（服务层）
        
        ### 2.1 Service Interfaces（服务接口）
        [为每个领域实体生成服务接口]
        
        ### 2.2 Business Logic（业务逻辑）
        [实现复杂的业务规则]
        
        ### 2.3 Transaction Management（事务管理）
        [定义事务边界和处理]
        
        ### 2.4 Service Dependencies（服务依赖）
        [服务间的依赖关系]
      追加到: 状态.输出.psm_内容
      更新:
        - 状态.进度.已完成步骤.添加("Service Layer")
        - 状态.进度.当前步骤 = 4

    步骤5_生成API设计:
      动作: 基于PIM生成REST API Design章节
      策略:
        - 从PIM中提取API需求
        - 设计FastAPI路由端点
        - 使用Pydantic模型定义请求/响应
        - 配置JWT认证（如需要）
        - 自动生成OpenAPI文档
      内容结构: |
        ## 3. REST API Design（API设计）
        
        ### 3.1 Endpoints（端点）
        [使用FastAPI装饰器定义RESTful端点]
        
        ### 3.2 Request/Response Models（请求响应模型）
        [Pydantic模型定义输入输出格式]
        
        ### 3.3 Authentication & Authorization（认证授权）
        [FastAPI Security和JWT实现]
        
        ### 3.4 API Documentation（API文档）
        [FastAPI自动生成的OpenAPI/Swagger文档]
        
        ### 3.5 Error Handling（错误处理）
        [HTTPException和自定义错误处理]
      追加到: 状态.输出.psm_内容
      更新:
        - 状态.进度.已完成步骤.添加("REST API Design")
        - 状态.进度.当前步骤 = 5

    步骤6_生成配置:
      动作: 基于FastAPI技术栈生成Application Configuration章节
      策略:
        - PostgreSQL数据库连接配置
        - FastAPI应用初始化
        - Uvicorn服务器配置
        - 环境变量配置
        - 中间件和CORS配置
      内容结构: |
        ## 4. Application Configuration（应用配置）
        
        ### 4.1 Database Configuration（数据库配置）
        [PostgreSQL连接和SQLAlchemy配置]
        
        ### 4.2 Main Application（主应用）
        [FastAPI应用实例和中间件配置]
        
        ### 4.3 Environment Variables（环境变量）
        [使用os.getenv配置环境变量]
        
        ### 4.4 Dependencies（依赖项）
        [requirements.txt: fastapi, uvicorn, sqlalchemy, psycopg2等]
        
        ### 4.5 Middleware Configuration（中间件配置）
        [CORS、认证、日志等中间件配置]
      追加到: 状态.输出.psm_内容
      更新:
        - 状态.进度.已完成步骤.添加("Application Configuration")
        - 状态.进度.当前步骤 = 6

    步骤7_生成测试规范:
      动作: 生成Testing Specifications章节
      策略:
        - pytest测试框架
        - FastAPI TestClient
        - SQLite内存数据库测试
        - pytest-asyncio异步测试
        - 测试数据准备
      内容结构: |
        ## 5. Testing Specifications（测试规范）
        
        ### 5.1 Unit Tests（单元测试）
        [使用pytest测试服务层和业务逻辑]
        
        ### 5.2 Integration Tests（集成测试）
        [使用TestClient测试FastAPI端点]
        
        ### 5.3 Test Fixtures（测试夹具）
        [pytest fixtures和测试数据库配置]
      追加到: 状态.输出.psm_内容
      更新:
        - 状态.进度.已完成步骤.添加("Testing Specifications")
        - 状态.进度.当前步骤 = 7

    步骤8_组装文档:
      动作: 组装完整的PSM文档
      任务:
        - 整合所有章节内容
        - 格式化代码块
        - 添加目录索引
        - 检查内容完整性
      保存到: 状态.输出.psm_内容
      更新: 状态.进度.当前步骤 = 8

    步骤9_写入文件:
      动作: 将完整的PSM内容写入文件
      工具: write_file
      参数:
        file_path: 状态.输入.psm_file
        content: 状态.输出.psm_内容
      验证: 文件是否成功创建
      更新: 状态.进度.当前步骤 = 9

    步骤10_验证完整性:
      动作: 验证PSM文档的完整性
      工具: read_file
      参数: 状态.输入.psm_file
      检查:
        - 包含所有必需章节
        - 代码示例完整
        - 配置文件齐全
        - 测试用例覆盖
      验证项:
        - "Domain Models" 存在
        - "Service Layer" 存在
        - "REST API Design" 存在
        - "Application Configuration" 存在
        - "Testing Specifications" 存在
      保存到: 状态.输出.验证结果
      更新: 状态.进度.当前步骤 = 10
      
    步骤11_完成:
      条件: 所有章节都已完成且验证通过
      设置: 状态.完成 = true
      报告: |
        PSM生成完成报告：
        - 项目名称: [状态.输入.project_name]
        - 技术栈: [状态.输入.platform_stack]
        - 生成文件: [状态.输入.psm_file]
        - 完成章节: [状态.进度.已完成步骤]
        - 验证结果: [状态.输出.验证结果]