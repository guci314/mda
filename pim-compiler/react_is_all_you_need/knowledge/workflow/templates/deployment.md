# 软件部署工作流模板

## 模板元信息
```yaml
template_id: deployment_workflow_v1
version: 1.0.0
type: deployment
author: system
created_at: 2024-01-15
tags: [deployment, ci/cd, production]
description: 标准软件部署流程，支持多环境和审批机制
```

## 参数定义
```yaml
parameters:
  environment:
    type: string
    required: true
    description: 部署环境
    enum: [development, staging, production]
    
  servers:
    type: array
    required: true
    description: 目标服务器列表
    example: ["server1", "server2", "server3"]
    
  version:
    type: string
    required: true
    description: 部署版本号
    example: "v1.2.3"
    
  skip_tests:
    type: boolean
    required: false
    default: false
    description: 是否跳过测试步骤
```

## 工作流步骤

### 1. 代码检查 [action]
**描述**: 执行代码质量检查和安全扫描
**执行内容**:
- 运行代码静态分析工具
- 检查代码规范符合性
- 扫描安全漏洞
- 检查依赖版本

**成功条件**: 
- 无严重代码问题
- 无高危安全漏洞

**跳过条件**: 
- 参数 `skip_tests` 为 true

### 2. 单元测试 [action]
**描述**: 运行所有单元测试
**执行内容**:
- 执行 pytest 或相应测试框架
- 生成测试覆盖率报告
- 验证测试通过率

**成功条件**: 
- 测试通过率 >= 95%
- 关键功能测试 100% 通过

**跳过条件**: 
- 参数 `skip_tests` 为 true

### 3. 构建镜像 [action]
**描述**: 构建 Docker 镜像
**执行内容**:
- 编译源代码
- 打包应用程序
- 构建 Docker 镜像
- 推送镜像到 registry

**成功条件**: 
- 镜像构建成功
- 镜像成功推送到 registry
- 镜像标签: `${version}-${environment}`

### 4. 环境判断 [condition]
**描述**: 根据部署环境决定执行路径
**判断逻辑**:
```
if environment == "production":
    需要审批 → 进入步骤5
    设置 variables.require_approval = true
elif environment == "staging":
    可选审批 → 检查是否有待处理的审批请求
    设置 variables.require_approval = optional
else:
    无需审批 → 跳过步骤5，直接进入步骤6
    设置 variables.require_approval = false
```

### 5. 部署审批 [approval]
**描述**: 等待相关人员审批
**配置**:
- 审批超时: 24小时
- 审批方式: 至少一人批准
- 通知方式: 邮件 + Slack

**审批人员**:
- production: 技术负责人 + 运维负责人
- staging: 技术负责人

**跳过条件**: 
- `variables.require_approval` 为 false

### 6. 服务停止 [parallel]
**描述**: 优雅停止现有服务
**并行任务**: 
对每个 server 执行:
- 从负载均衡器移除
- 等待现有请求完成（最多30秒）
- 停止应用服务

**成功条件**: 
- 所有服务器成功停止服务
- 无活跃连接

### 7. 部署新版本 [parallel]
**描述**: 部署新版本到所有服务器
**并行任务**:
对每个 server 执行:
- 拉取新版本镜像
- 更新配置文件
- 启动新版本服务
- 等待服务就绪

**成功条件**: 
- 所有服务器部署成功
- 服务健康检查通过

### 8. 健康检查 [action]
**描述**: 验证部署后的服务状态
**执行内容**:
- 检查服务端口响应
- 验证 API 健康端点
- 检查关键功能可用性
- 验证性能指标

**成功条件**: 
- 所有健康检查通过
- 响应时间 < 500ms
- 错误率 < 1%

### 9. 负载均衡更新 [action]
**描述**: 将新服务加入负载均衡
**执行内容**:
- 将服务器重新加入负载均衡池
- 更新路由规则
- 验证流量分发

**成功条件**: 
- 所有服务器接收流量正常
- 负载分布均匀

### 10. 通知 [action]
**描述**: 发送部署结果通知
**执行内容**:
- 生成部署报告
- 发送成功/失败通知
- 更新部署记录

**通知内容**:
- 部署版本: ${version}
- 目标环境: ${environment}
- 部署服务器: ${servers}
- 执行时长: ${total_duration}
- 部署状态: ${status}

## 回滚策略

当任何步骤失败时:
1. 如果在步骤6之前失败 → 直接终止，无需回滚
2. 如果在步骤6-7失败 → 恢复旧版本服务
3. 如果在步骤8-9失败 → 切换回旧版本，保持服务可用

## 成功判定条件

工作流成功的标准:
- ✅ 所有必要步骤执行完成
- ✅ 健康检查全部通过
- ✅ 服务正常接收流量
- ✅ 错误率低于阈值
- ✅ 性能指标符合要求

## 使用示例

### 基础使用
```
执行 deployment.md 模板
参数:
- environment: production
- servers: [app-server-1, app-server-2, app-server-3]
- version: v2.1.0
```

### 跳过测试（紧急部署）
```
执行 deployment.md 模板
参数:
- environment: production
- servers: [app-server-1]
- version: v2.1.0-hotfix
- skip_tests: true
```

### 覆盖特定步骤
```
基于 deployment.md 模板
但修改:
- 跳过步骤1（代码检查已在CI完成）
- 步骤8增加数据库迁移验证
```

## 监控指标

执行过程中收集的关键指标:
- `deployment.duration`: 总部署时长
- `deployment.success_rate`: 成功率
- `deployment.rollback_count`: 回滚次数
- `health_check.response_time`: 健康检查响应时间
- `service.error_rate`: 服务错误率