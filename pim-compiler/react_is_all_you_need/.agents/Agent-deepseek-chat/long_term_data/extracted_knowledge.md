```markdown
# 长期记忆更新

## 用户信息
- 用户姓名：谷词
- 技术偏好：关注系统触发机制（如 `world_overview` 更新条件）
- 交互特点：倾向于直接询问具体技术实现细节

## 交互模式
- 首次交互时主动说明能力范围（技术任务执行助手）
- 技术问题响应规范：
  1. 提供多场景解决方案（手动/定时/事件驱动等）
  2. 附带可操作的排查方法（代码搜索/配置检查）
  3. 主动延伸帮助（执行具体排查动作）

## 技术知识库
### 系统触发机制
核心触发类型：
1. 手动执行（命令/脚本）
2. 定时任务（cron/systemd）
3. 事件驱动（数据变更/用户操作）
4. 版本控制钩子（Git hooks）
5. CI/CD流程（GitHub Actions/Jenkins）
6. API调用

高效排查流程：
1. 代码级搜索：
   ```bash
   grep -r "TARGET_KEYWORD" .
   ```
2. 定时任务检查：
   ```bash
   crontab -l && systemctl list-timers
   ```
3. CI/CD审查：
   - 检查 `.github/workflows/` 或 `.gitlab-ci.yml`
4. 钩子检查：
   - 查看 `.git/hooks/` 目录

### 特殊案例
`world_overview`更新场景：
- 需要特别关注数据变更事件触发
- 可能关联版本控制钩子（文档类更新）
```