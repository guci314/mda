# PSM 生成知识库 V2

## 基础知识定义



## 章节生成算法

def_nl @@generateDomainChapter(pim) {
    1. 初始化章节内容 = "# Domain Models\n\n"
    
    2. 实体列表 = extractEntityList(pim)
    
    3. 对每个实体 in 实体列表:
        a. generateEntityDefinition(实体)
        b. generateSQLAlchemyModel(实体)
        c. generatePydanticModel(实体)
        d. generateEnumConstants(实体)
    
    4. call_tool('save_chapter', 'domain', 完整的Domain章节内容)
}

def_nl @@generateEntityDefinition(entity) {
    1. 添加标题 "## Entity Definition - {entity.名称}"
    2. 添加描述文档字符串
    3. 对每个属性:
        - 生成属性定义行
        - 包含类型信息
        - 包含约束说明
    4. 返回实体定义内容
}

def_nl @@generateSQLAlchemyModel(entity) {
    1. 导入必要的SQLAlchemy模块
    2. 创建类定义 "class {entity.名称}DB(Base):"
    3. 设置表名 "__tablename__ = '{entity.名称.lower()}s'"
    4. 对每个属性:
        a. 确定SQLAlchemy列类型
        b. 添加约束（primary_key, unique, nullable等）
        c. 如果是UUID，添加默认值生成器
        d. 如果是时间戳，添加自动更新
    5. 返回SQLAlchemy模型代码
}

def_nl @@generatePydanticModel(entity) {
    1. 导入Pydantic相关模块
    2. 生成基础模型 "{entity.名称}Base"
        - 包含所有可编辑字段
        - 添加字段验证器
    3. 生成创建模型 "{entity.名称}Create"
        - 继承自Base
        - 排除自动生成字段
    4. 生成更新模型 "{entity.名称}Update"
        - 所有字段可选
        - 使用Optional包装
    5. 生成响应模型 "{entity.名称}Response"
        - 包含所有字段
        - 添加 ConfigDict(from_attributes=True)
    6. 返回所有Pydantic模型代码
}

def_nl @@generateServiceChapter(pim) {
    1. 初始化章节内容 = "# Service Layer\n\n"
    
    2. 服务列表 = extractServiceList(pim)
    
    3. 对每个服务 in 服务列表:
        a. generateServiceClass(服务)
        b. generateRepositoryInterface(服务.实体)
        c. generateRepositoryImplementation(服务.实体)
        d. generateTransactionDecorator()
    
    4. call_tool('save_chapter', 'service', 完整的Service章节内容)
}

def_nl @@generateServiceClass(service) {
    1. 创建类定义 "class {service.名称}:"
    2. 添加依赖注入构造函数
    3. 对每个服务方法:
        a. 分析方法的业务逻辑
        b. 生成async方法签名
        c. 实现业务规则验证
        d. 调用仓储方法
        e. 添加错误处理
        f. 返回响应模型
    4. 返回服务类代码
}

def_nl @@generateAPIChapter(pim, service_layer) {
    1. 初始化章节内容 = "# REST API Design\n\n"
    
    2. 资源列表 = extractResourceList(pim)
    
    3. 对每个资源 in 资源列表:
        a. generateRouteDefinition(资源)
        b. generateCRUDEndpoints(资源, service_layer)
        c. generateRequestValidation(资源)
        d. generateResponseFormat(资源)
    
    4. 生成API文档说明
    5. 返回完整的API章节内容
}

def_nl @@generateCRUDEndpoints(resource, service_layer) {
    1. 创建路由器 "router = APIRouter(prefix='/api/{resource}', tags=['{resource}'])"
    
    2. 生成列表端点:
        - GET /api/{resource}
        - 支持分页参数
        - 支持过滤参数
        - 调用service.list方法
    
    3. 生成获取端点:
        - GET /api/{resource}/{id}
        - 路径参数验证
        - 调用service.get方法
        - 404错误处理
    
    4. 生成创建端点:
        - POST /api/{resource}
        - 请求体验证
        - 调用service.create方法
        - 返回201状态码
    
    5. 生成更新端点:
        - PUT /api/{resource}/{id}
        - 部分更新支持
        - 调用service.update方法
    
    6. 生成删除端点:
        - DELETE /api/{resource}/{id}
        - 调用service.delete方法
        - 返回204状态码
    
    7. 返回所有端点代码
}

def_nl @@generateAppChapter(pim, all_chapters) {
    1. 初始化章节内容 = "# Application Configuration\n\n"
    
    2. 生成主应用文件:
        a. FastAPI实例创建
        b. 中间件配置
        c. 路由注册
        d. 异常处理器
        e. 启动和关闭事件
    
    3. 生成数据库配置:
        a. 连接字符串配置
        b. 会话工厂设置
        c. 依赖注入函数
    
    4. 生成环境配置:
        a. Settings类定义
        b. 环境变量加载
        c. 配置验证
    
    5. 生成项目结构说明
    6. 返回完整的App章节内容
}

def_nl @@generateTestChapter(pim, all_code) {
    1. 初始化章节内容 = "# Testing Specifications\n\n"
    
    2. 生成测试配置:
        a. pytest配置
        b. 测试数据库设置
        c. 测试客户端创建
    
    3. 对每个服务生成单元测试:
        a. 测试所有业务方法
        b. 测试边界条件
        c. 测试错误处理
    
    4. 对每个API端点生成集成测试:
        a. 测试正常请求
        b. 测试验证错误
        c. 测试权限控制
    
    5. 生成测试数据工厂:
        a. 使用Factory Boy或类似工具
        b. 创建测试数据生成器
    
    6. 返回完整的Test章节内容
}

## 辅助算法

def_nl @@determineFieldType(field_description) {
    如果 包含("标识符" 或 "ID"):
        返回 "UUID"
    否则如果 包含("名称" 或 "姓名"):
        返回 "String(50)"
    否则如果 包含("邮箱" 或 "email"):
        返回 "String(100), unique=True"
    否则如果 包含("电话" 或 "phone"):
        返回 "String(20)"
    否则如果 包含("时间" 或 "日期"):
        返回 "DateTime"
    否则如果 包含("状态"):
        返回 "Enum"
    否则如果 包含("数量" 或 "数字"):
        返回 "Integer"
    否则如果 包含("金额" 或 "价格"):
        返回 "Decimal"
    否则:
        返回 "String"
}

def_nl @@generateValidationRules(field, business_rules) {
    1. 分析字段的业务约束
    2. 如果是邮箱，添加邮箱格式验证
    3. 如果是电话，添加电话格式验证
    4. 如果有长度限制，添加长度验证
    5. 如果有唯一性要求，在数据库层添加唯一索引
    6. 如果有业务规则，生成自定义验证器
    7. 返回验证代码
}

def_nl @@generateErrorHandling(operation_type) {
    如果 operation_type == "创建":
        处理唯一性冲突 -> 返回409
        处理验证错误 -> 返回400
    否则如果 operation_type == "查询":
        处理未找到 -> 返回404
    否则如果 operation_type == "更新":
        处理未找到 -> 返回404
        处理并发冲突 -> 返回409
    否则如果 operation_type == "删除":
        处理未找到 -> 返回404
        处理关联数据 -> 返回400
    
    通用处理:
        处理数据库错误 -> 返回500
        记录错误日志
        返回用户友好的错误消息
}

## 代码风格规范

def_nl @@applyCodeStyle(code) {
    1. 确保所有类名使用PascalCase
    2. 确保所有函数名使用snake_case
    3. 确保所有常量使用UPPER_SNAKE_CASE
    4. 添加类型注解到所有函数参数和返回值
    5. 添加docstring到所有类和函数
    6. 使用中文注释解释业务逻辑
    7. 确保适当的空行分隔
    8. 返回格式化后的代码
}

## 质量检查

def_nl @@checkGenerationQuality(chapter_content) {
    1. 检查是否包含所有必需的部分
    2. 检查代码是否可运行（语法正确）
    3. 检查是否遵循平台最佳实践
    4. 检查是否有适当的错误处理
    5. 检查是否有必要的注释
    6. 返回质量报告和改进建议
}

## 辅助提取函数

def_nl @@extractEntityList(pim) {
    1. 在PIM中查找"领域对象"或"实体"章节
    2. 识别所有以"###"开头的实体定义
    3. 对每个实体:
        - 提取实体名称（中英文）
        - 提取实体描述
        - 提取所有属性定义
        - 识别属性类型和约束
    4. 返回实体列表
}

def_nl @@extractServiceList(pim) {
    1. 在PIM中查找"领域服务"或"服务"章节
    2. 识别所有服务定义
    3. 对每个服务:
        - 提取服务名称
        - 提取服务方法列表
        - 识别方法参数和返回值
        - 理解业务逻辑
    4. 返回服务列表
}

def_nl @@extractResourceList(pim) {
    1. 基于实体列表生成资源列表
    2. 对每个实体:
        - 确定资源名称（通常是实体名的复数形式）
        - 确定资源路径
        - 确定支持的操作（CRUD）
    3. 返回资源列表
}

def_nl @@generateEnumConstants(entity) {
    1. 识别实体中的枚举类型属性
    2. 对每个枚举属性:
        - 创建Enum类定义
        - 定义所有可能的值
        - 添加中文注释说明
    3. 返回枚举定义代码
}

def_nl @@generateTransactionDecorator() {
    1. 创建事务装饰器函数
    2. 实现自动提交和回滚逻辑
    3. 添加错误处理
    4. 返回装饰器代码
}

def_nl @@generateRepositoryInterface(entity) {
    1. 创建抽象基类
    2. 定义标准CRUD方法签名
    3. 添加类型注解
    4. 返回接口代码
}

def_nl @@generateRepositoryImplementation(entity) {
    1. 实现仓储接口
    2. 使用SQLAlchemy进行数据库操作
    3. 实现分页、过滤、排序
    4. 添加事务支持
    5. 返回实现代码
}

def_nl @@generateRouteDefinition(resource) {
    1. 创建APIRouter实例
    2. 设置路由前缀和标签
    3. 配置响应模型
    4. 返回路由定义
}

def_nl @@generateRequestValidation(resource) {
    1. 使用Pydantic模型验证请求体
    2. 验证路径参数
    3. 验证查询参数
    4. 返回验证代码
}

def_nl @@generateResponseFormat(resource) {
    1. 定义统一的响应格式
    2. 包含分页信息
    3. 包含错误信息格式
    4. 返回响应格式代码
}