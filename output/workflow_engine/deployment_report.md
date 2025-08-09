# 部署报告

**Workflow ID:** `deploy-20231027-12345`
**状态:** ✅ completed
**创建时间:** `2023-10-27T10:00:00Z`
**完成时间:** `2023-10-27T10:08:01Z`

---

## 部署详情

- **环境:** `production`
- **Docker 镜像:** `myapp:9ddvzatv438s`
- **部署服务器:** `server-1`, `server-2`, `server-3`

---

## 步骤摘要

| 步骤 ID | 名称 | 状态 | 开始时间 | 完成时间 |
| --- | --- | --- | --- | --- |
| `step_1_code_check` | 代码检查 | ✅ completed | `2023-10-27T10:01:00Z` | `2023-10-27T10:01:02Z` |
| `step_2_build` | 构建 | ✅ completed | `2023-10-27T10:02:00Z` | `2023-10-27T10:02:02Z` |
| `step_3_deploy_decision` | 部署决策 | ✅ completed | `2023-10-27T10:03:00Z` | `2023-10-27T10:03:00Z` |
| `step_4_approval` | 审批流程 | ✅ completed | `2023-10-27T10:03:00Z` | `2023-10-27T10:05:00Z` |
| `step_5_parallel_deploy` | 并行部署 | ✅ completed | `2023-10-27T10:05:00Z` | `2023-10-27T10:06:00Z` |
| `step_6_health_check` | 健康检查 | ✅ completed | `2023-10-27T10:07:00Z` | `2023-10-27T10:07:02Z` |
| `step_7_notify` | 通知 | ✅ completed | `2023-10-27T10:08:00Z` | `2023-10-27T10:08:01Z` |

---

## 审批详情

- **审批人:** `admin@example.com`
- **状态:** `approved`
- **意见:** `LGTM`
- **时间:** `2023-10-27T10:04:59Z`

---

## 执行日志

- `2023-10-27T10:01:02Z` - **step_1_code_check**: Code check completed successfully.
- `2023-10-27T10:02:02Z` - **step_2_build**: Build completed successfully. Image: myapp:9ddvzatv438s
- `2023-10-27T10:03:00Z` - **step_3_deploy_decision**: Condition evaluated to true. Proceeding to approval.
- `2023-10-27T10:05:00Z` - **step_4_approval**: Deployment approved by admin@example.com.
- `2023-10-27T10:06:00Z` - **step_5_parallel_deploy**: All parallel deployment steps completed successfully.
- `2023-10-27T10:07:02Z` - **step_6_health_check**: Health check passed.
- `2023-10-27T10:08:01Z` - **step_7_notify**: Deployment notification sent.
