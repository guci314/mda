# 知识库

## 元知识
- **文档转换方法**：从抽象模型到具体实现的系统化转换流程
  - 先完整读取源文档理解领域模型
  - 按目标平台特性重新组织内容结构
  - 保持领域概念一致性的同时添加技术实现细节
- **模型驱动开发验证**：通过文档生成验证转换正确性
  - 检查文件是否成功生成
  - 验证内容是否包含目标平台特定元素

## 原理与设计
- **MDA架构模式**：模型驱动架构的PIM到PSM转换
  - PIM（平台无关模型）：专注业务逻辑和领域概念
  - PSM（平台特定模型）：结合具体技术栈的实现模型
- **PSM文档结构设计**：
  - Domain Models：领域实体的技术实现映射
  - Service Layer：业务逻辑的服务层设计
  - REST API Design：API接口的具体定义
  - Application Configuration：应用配置和部署
  - Testing Specifications：测试策略和规范
- **FastAPI技术栈选择**：作为PSM目标平台的架构决策

## 接口与API
- **read_file工具**：读取文档内容
  - 用法：直接传入文件路径
  - 返回完整文件内容
- **文档命名约定**：
  - PIM文档：`*_pim.md`
  - PSM文档：`*_psm.md`
- **PSM文档标准章节**：
  1. Domain Models
  2. Service Layer  
  3. REST API Design
  4. Application Configuration
  5. Testing Specifications

## 实现细节（需验证）
- **文件操作模式**：
  - 源文件：`library_borrowing_system_pim.md`
  - 目标文件：`library_borrowing_system_psm.md`
- **PIM实体结构**：Book、Reader、BorrowRecord、ReservationRecord等核心实体
- **转换映射规律**：
  - PIM实体属性 → PSM Pydantic模型字段
  - PIM业务服务 → PSM Service Layer方法
  - PIM操作 → PSM REST API端点

## 用户偏好与项目特点
- **任务验证要求**：完成任务后需要明确验证结果
  - 确认文件生成
  - 验证内容包含预期的技术特定元素
- **文档转换偏好**：系统化的模型驱动开发方法
- **技术栈偏好**：FastAPI作为Python Web框架的选择