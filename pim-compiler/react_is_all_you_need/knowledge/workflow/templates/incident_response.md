# 安全事件响应工作流模板

## 模板元信息
```yaml
template_id: incident_response_v1
version: 1.0.0
type: security_incident
author: system
created_at: 2024-01-15
tags: [security, incident, response, emergency]
description: 安全事件响应标准流程，支持不同严重级别的分级响应
```

## 参数定义
```yaml
parameters:
  incident_id:
    type: string
    required: true
    description: 事件唯一标识
    example: "SEC-2024-001"
    
  incident_type:
    type: string
    required: true
    description: 事件类型
    enum: [unauthorized_access, data_breach, ddos, malware, insider_threat, system_compromise]
    
  severity:
    type: string
    required: true
    description: 严重程度
    enum: [critical, high, medium, low]
    
  affected_systems:
    type: array
    required: true
    description: 受影响系统列表
    example: ["web_server_1", "database_1", "api_gateway"]
    
  detection_source:
    type: string
    required: false
    description: 检测来源
    enum: [siem, ids, waf, manual, user_report]
    default: "siem"
    
  auto_contain:
    type: boolean
    required: false
    default: false
    description: 是否自动隔离（仅用于critical级别）
```

## 工作流步骤

### 1. 事件接收与记录 [action]
**描述**: 接收并记录安全事件
**执行内容**:
- 记录事件基本信息
- 生成事件工单
- 记录初始时间戳
- 分配事件ID

**记录信息**:
- 事件ID: ${incident_id}
- 检测时间: ${detection_time}
- 报告来源: ${detection_source}
- 初始描述: ${description}

**成功条件**: 
- 事件记录创建成功
- 工单系统更新
- 设置 `variables.ticket_id` = 工单号

### 2. 初步评估 [action]
**描述**: 快速评估事件影响范围
**执行内容**:
- 验证告警真实性（排除误报）
- 识别受影响资产
- 评估潜在影响
- 确定事件类型

**评估维度**:
- 数据敏感性: 是否涉及敏感数据
- 业务影响: 对业务运营的影响程度
- 影响范围: 受影响用户/系统数量
- 攻击进度: 攻击者当前阶段

**成功条件**: 
- 完成初步评估
- 更新 `variables.impact_score` = 影响评分
- 更新 `variables.confirmed` = true/false

### 3. 严重性判定 [condition]
**描述**: 根据严重程度决定响应级别
**判断逻辑**:
```
severity_level = severity

if severity == "critical":
    立即响应 → 进入步骤4（紧急响应）
    通知所有相关人员
    设置 variables.response_level = "immediate"
    设置 variables.escalation = true
    
elif severity == "high":
    快速响应 → 进入步骤4（紧急响应）
    通知安全团队
    设置 variables.response_level = "rapid"
    设置 variables.escalation = true
    
elif severity == "medium":
    计划响应 → 进入步骤5（计划响应）
    通知值班人员
    设置 variables.response_level = "planned"
    设置 variables.escalation = false
    
else:  # low
    记录观察 → 进入步骤11（记录存档）
    仅记录不处理
    设置 variables.response_level = "monitor"
    设置 variables.escalation = false
```

### 4. 紧急响应 [parallel]
**描述**: 对高危事件的立即响应措施
**并行任务**:

**系统隔离**:
- 识别受影响系统
- 从网络中隔离
- 保留系统状态
- 阻断攻击路径

**团队通知**:
- 通知安全团队
- 通知系统管理员
- 通知业务负责人
- 如需要，通知管理层

**证据收集**:
- 启动日志收集
- 创建系统快照
- 保存网络流量
- 记录当前状态

**成功条件**: 
- 受影响系统已隔离
- 所有相关人员已通知
- 证据收集已启动
- 记录 `variables.containment_time` = 隔离完成时间

**跳过条件**: 
- `variables.response_level` == "planned" 或 "monitor"

### 5. 计划响应 [action]
**描述**: 对中等严重事件的计划响应
**执行内容**:
- 制定响应计划
- 安排响应资源
- 设置监控告警
- 计划修复时间窗口

**成功条件**: 
- 响应计划制定完成
- 资源分配完成

**跳过条件**: 
- `variables.response_level` == "immediate" 或 "rapid" 或 "monitor"

### 6. 威胁分析 [action]
**描述**: 深入分析攻击手法和影响
**执行内容**:
- 分析攻击向量（入侵途径）
- 识别攻击者TTP（战术、技术、程序）
- 评估横向移动可能性
- 检查数据泄露情况

**分析方法**:
- 日志关联分析
- 恶意代码分析
- 网络流量分析
- 用户行为分析

**输出结果**:
- 攻击时间线
- 受影响资产清单
- 数据泄露评估
- 攻击者画像

**成功条件**: 
- 完成根因分析
- 识别所有受影响系统
- 更新 `variables.root_cause` = 根本原因
- 更新 `variables.attack_vector` = 攻击向量

**跳过条件**: 
- `variables.response_level` == "monitor"

### 7. 修复方案制定 [action]
**描述**: 制定详细的修复方案
**执行内容**:
- 制定修复步骤
- 评估修复影响
- 准备回滚方案
- 估算修复时间

**方案内容**:
- 漏洞修补计划
- 系统加固措施
- 配置更改清单
- 补偿控制措施

**成功条件**: 
- 修复方案文档完成
- 风险评估完成
- 更新 `variables.remediation_plan` = 修复方案

**跳过条件**: 
- `variables.response_level` == "monitor"

### 8. 修复审批 [approval]
**描述**: 获取修复方案的审批
**配置**:
- 审批超时: 根据严重程度（critical: 1小时, high: 4小时, medium: 24小时）
- 审批方式: 根据影响范围决定

**审批人员**:
- critical: CISO + CTO
- high: 安全主管 + 技术主管
- medium: 安全主管

**紧急处理**:
- 如果 `auto_contain` == true 且 severity == "critical"
- 可以先执行后审批

**成功条件**: 
- 获得必要审批
- 记录 `variables.approval_status` = "approved"
- 记录 `variables.approver` = 审批人

**跳过条件**: 
- `variables.response_level` == "monitor"

### 9. 修复执行 [parallel]
**描述**: 执行修复措施
**并行任务**:

**漏洞修补**:
- 应用安全补丁
- 修复配置错误
- 更新安全策略
- 修补应用漏洞

**系统加固**:
- 更新防火墙规则
- 加强访问控制
- 启用额外监控
- 部署检测规则

**数据恢复**:
- 验证数据完整性
- 恢复受损数据
- 重置凭证密钥
- 更新加密密钥

**成功条件**: 
- 所有修复措施执行完成
- 无新的安全告警
- 记录 `variables.remediation_completed` = true

**跳过条件**: 
- `variables.response_level` == "monitor"

### 10. 验证与测试 [action]
**描述**: 验证修复效果
**执行内容**:
- 验证漏洞已修复
- 测试系统功能
- 确认服务正常
- 检查性能影响

**验证方法**:
- 漏洞扫描
- 渗透测试
- 功能测试
- 性能基准测试

**成功条件**: 
- 漏洞验证已修复
- 系统功能正常
- 性能指标正常
- 无新增安全风险

**跳过条件**: 
- `variables.response_level` == "monitor"

### 11. 监控强化 [action]
**描述**: 加强监控以防止再次发生
**执行内容**:
- 部署新的检测规则
- 增加监控指标
- 调整告警阈值
- 更新威胁情报

**监控措施**:
- SIEM规则更新
- IDS/IPS签名更新
- 日志收集优化
- 异常检测增强

**成功条件**: 
- 监控规则部署完成
- 告警测试通过

### 12. 事件总结 [action]
**描述**: 生成事件响应报告
**报告内容**:

**执行摘要**:
- 事件ID: ${incident_id}
- 事件类型: ${incident_type}
- 严重程度: ${severity}
- 影响范围: ${affected_systems}

**时间线**:
- 检测时间: ${detection_time}
- 响应开始: ${response_start}
- 隔离完成: ${containment_time}
- 修复完成: ${remediation_time}
- 总耗时: ${total_duration}

**技术细节**:
- 根本原因: ${root_cause}
- 攻击向量: ${attack_vector}
- 影响评估: ${impact_assessment}
- 修复措施: ${remediation_actions}

**经验教训**:
- 检测能力差距
- 响应流程改进点
- 预防措施建议
- 培训需求

**后续行动**:
- 长期改进计划
- 政策更新建议
- 技术债务清单

**输出文件**: 
- `incident_report_${incident_id}.md`
- `timeline_${incident_id}.json`
- `lessons_learned_${incident_id}.md`

## 升级机制

### 自动升级条件
- 发现新的受影响系统
- 检测到数据泄露
- 攻击者活动升级
- 修复失败

### 升级路径
- low → medium: 发现实际影响
- medium → high: 涉及关键系统
- high → critical: 确认数据泄露或业务中断

## 沟通计划

### 内部沟通
- 技术团队: 实时更新
- 管理层: 每小时简报（critical/high）
- 业务部门: 影响评估和恢复时间

### 外部沟通
- 客户: 如涉及客户数据（legal review后）
- 监管机构: 按合规要求（如72小时内）
- 媒体: 通过公关部门统一发布

## 成功判定条件

事件响应成功的标准:
- ✅ 威胁已完全清除
- ✅ 系统恢复正常运行
- ✅ 无二次感染迹象
- ✅ 监控措施已加强
- ✅ 完整文档已归档

## 使用示例

### 高危事件响应
```
执行 incident_response.md 模板
参数:
- incident_id: "SEC-2024-001"
- incident_type: "unauthorized_access"
- severity: "high"
- affected_systems: ["web_server_1", "database_1"]
- auto_contain: true
```

### 数据泄露事件
```
执行 incident_response.md 模板
参数:
- incident_id: "SEC-2024-002"
- incident_type: "data_breach"
- severity: "critical"
- affected_systems: ["customer_db", "payment_system"]
- detection_source: "user_report"
```

### 低风险监控
```
执行 incident_response.md 模板
参数:
- incident_id: "SEC-2024-003"
- incident_type: "malware"
- severity: "low"
- affected_systems: ["test_server_1"]
```

## 监控指标

执行过程中收集的关键指标:
- `response.detection_time`: 检测时间
- `response.containment_time`: 隔离时间
- `response.resolution_time`: 解决时间
- `response.total_duration`: 总响应时间
- `impact.affected_users`: 受影响用户数
- `impact.data_exposed`: 泄露数据量
- `effectiveness.threat_eliminated`: 威胁清除率
- `effectiveness.false_positive_rate`: 误报率