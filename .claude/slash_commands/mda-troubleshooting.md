# /mda-troubleshooting

MDA项目故障排查指南，快速定位和解决开发中的常见问题。

## 使用方法
输入 `/mda-troubleshooting` 查看完整故障排查指南
输入 `/mda-troubleshooting topic=debug` 查看特定主题

## 主要内容
- 模型层次设计（PIM vs PSM）
- 流程调试器实现
- JSON序列化解决方案  
- Docker环境配置
- WebSocket实时通信
- MDA代码生成策略
- LLM驱动开发优势

## 快速参考

### 常见问题
- Mermaid图表渲染错误 → 移除markdown包装
- datetime JSON序列化 → 使用model_dump(mode='json')
- Docker连接失败 → 检查容器名和健康检查
- WebSocket无响应 → 实现状态回调机制

### 调试技巧
1. 浏览器F12查看控制台日志
2. `docker logs` 查看服务端错误
3. 检查 /debug/flows API响应
4. 验证WebSocket消息格式

详细内容请查看 `.mda/commands/mda-troubleshooting.md`