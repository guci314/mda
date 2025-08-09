# mda_dual_agent_demo - UML四视图分析

生成时间：2025-08-09T21:24:30.304633

# 项目概述

目的：演示一个“双智能体”驱动的图书馆管理系统，提供图书、读者、借阅、预约等完整 REST 接口，用于验证 AI 协作生成代码的质量与可维护性。

技术栈：Python 3 + FastAPI（异步 Web 框架）、SQLite（单文件数据库）、SQLAlchemy（ORM）、Pydantic（数据校验/序列化）、pytest（自动化测试）。

整体结构：  
• app/ 为核心包，按 Clean Architecture 分层：  
  ‑ models/ 定义 ORM 实体与领域枚举；  
  ‑ repositories/ 封装数据库 CRUD；  
  ‑ services/ 实现业务规则；  
  ‑ routers/ 暴露 REST 端点；  
  ‑ schemas/ 提供请求/响应 DTO；  
  ‑ database.py + dependencies.py 管理连接与依赖注入。  
• tests/ 含 pytest 配置与用例。  
• library.db 为本地 SQLite 数据文件；requirements.txt 列依赖；debug_notes.json 与 coordinator_todo.json 供 AI 调试与任务跟踪。

## 1. Use Case视图

## Use Case视图分析

### 1. 主要Actor
- **Reader（读者）**：系统的主要用户，可借阅、归还、预约图书
- **Librarian（图书管理员）**：管理图书信息、处理借阅和归还
- **System（系统）**：自动处理逾期检查、发送通知
- **External API（外部系统）**：可能用于图书信息同步或支付接口

### 2. 核心用例

| 用例名称 | 简要描述 |
|---------|----------|
| **UC01: 查询图书** | 读者按条件搜索图书信息 |
| **UC02: 借阅图书** | 读者借阅可借状态的图书 |
| **UC03: 归还图书** | 读者归还已借阅的图书 |
| **UC04: 预约图书** | 读者预约已被借出的图书 |
| **UC05: 取消预约** | 读者取消已有的预约 |
| **UC06: 管理图书** | 管理员添加、修改、删除图书信息 |
| **UC07: 管理读者** | 管理员注册、更新读者信息 |
| **UC08: 检查逾期** | 系统自动检查逾期借阅并发送通知 |
| **UC09: 查看借阅历史** | 读者查看个人借阅记录 |
| **UC10: 处理罚款** | 管理员处理读者的逾期罚款 |

### 3. 用例关系分析

- **包含关系**：
  - UC02(借阅图书) → 包含 → 检查读者资格
  - UC02(借阅图书) → 包含 → 检查图书可借状态
  - UC03(归还图书) → 包含 → 更新图书状态
  - UC04(预约图书) → 包含 → 检查预约资格

- **扩展关系**：
  - UC02(借阅图书) ← 扩展 ← 处理预约冲突（当有预约时）
  - UC03(归还图书) ← 扩展 ← 触发预约通知（有预约排队时）
  - UC08(检查逾期) ← 扩展 ← 计算罚款金额

- **泛化关系**：
  - 管理图书(UC06) ← 泛化 ← 添加图书、修改图书、删除图书
  - 管理读者(UC07) ← 泛化 ← 注册读者、更新读者信息、注销读者

### 4. 用例图

```mermaid
%% 用例图 - 图书馆管理系统
%% 控制字符数在2000以内，简化展示核心关系

%% 定义参与者
actor Reader as "读者"
actor Librarian as "图书管理员"
actor System as "系统"
actor "External API" as ExtAPI

%% 定义用例
usecase "查询图书" as UC01
usecase "借阅图书" as UC02
usecase "归还图书" as UC03
usecase "预约图书" as UC04
usecase "取消预约" as UC05
usecase "管理图书" as UC06
usecase "管理读者" as UC07
usecase "检查逾期" as UC08
usecase "查看借阅历史" as UC09
usecase "处理罚款" as UC10

%% 定义子用例（泛化）
usecase "添加图书" as UC06a
usecase "修改图书" as UC06b
usecase "删除图书" as UC06c

usecase "注册读者" as UC07a
usecase "更新读者信息" as UC07b

%% 定义包含用例
usecase "检查读者资格" as Include1
usecase "检查图书状态" as Include2
usecase "更新图书状态" as Include3

%% 定义扩展用例
usecase "处理预约冲突" as Extend1
usecase "触发预约通知" as Extend2
usecase "计算罚款金额" as Extend3

%% 绘制关系
Reader --> UC01
Reader --> UC02
Reader --> UC03
Reader --> UC04
Reader --> UC05
Reader --> UC09

Librarian --> UC06
Librarian --> UC07
Librarian --> UC10

System --> UC08

UC06 <|-- UC06a
UC06 <|-- UC06b
UC06 <|-- UC06c

UC07 <|-- UC07a
UC07 <|-- UC07b

UC02 ..> Include1 : <<include>>
UC02 ..> Include2 : <<include>>
UC03 ..> Include3 : <<include>>

UC02 <-- Extend1 : <<extend>>
UC03 <-- Extend2 : <<extend>>
UC08 <-- Extend3 : <<extend>>

%% 系统边界
rectangle "图书馆管理系统" {
  UC01
  UC02
  UC03
  UC04
  UC05
  UC06
  UC07
  UC08
  UC

## 2. Package视图

Package视图分析失败：cannot schedule new futures after shutdown

## 3. Class视图

Class视图分析失败：cannot schedule new futures after shutdown

## 4. Interaction视图

Interaction视图分析失败：cannot schedule new futures after shutdown

## 5. 综合分析

综合分析分析失败：cannot schedule new futures after shutdown