# PIM UI - Web Interface for PIM Engine

PIM UI 是 PIM Engine 的独立 Web 界面，通过 REST API 与 PIM Engine 通信。

## 架构设计

### 分离原则
- UI 完全独立于 PIM Engine
- 通过 REST API 进行所有通信
- 可独立部署和扩展
- 支持多个 UI 实例连接同一个 Engine

### 技术栈
- **前端**: 纯 HTML/CSS/JavaScript（无框架依赖）
- **服务器**: Express.js（Node.js）
- **通信**: REST API + WebSocket（计划中）

## 快速开始

### 1. 安装依赖
```bash
npm install
```

### 2. 配置
复制环境变量文件：
```bash
cp .env.example .env
```

编辑 `.env` 文件，设置 PIM Engine 的地址：
```env
PORT=3000
API_BASE_URL=http://localhost:8000
```

### 3. 启动服务
```bash
# 生产模式
npm start

# 开发模式（支持热重载）
npm run dev
```

### 4. 访问界面
打开浏览器访问: http://localhost:3000

## 功能特性

### 模型管理
- 上传 PIM 模型文件（支持 .md, .yaml, .yml）
- 查看已加载的模型
- 加载/卸载模型
- 硬卸载（删除所有相关文件）
- 预览模型内容

### 实例管理
- 创建模型实例
- 管理运行中的实例
- 查看实例状态和端口
- 启动/停止实例

### 仪表板
- 系统状态监控
- 资源使用情况
- 实时性能指标

### 调试工具
- 流程调试器
- 规则测试
- API 测试工具

## 项目结构

```
pim-ui/
├── package.json          # Node.js 项目配置
├── server.js            # Express 服务器
├── .env.example         # 环境变量示例
├── public/              # 静态文件
│   ├── index.html       # 首页
│   ├── models.html      # 模型管理页
│   ├── instances.html   # 实例管理页
│   ├── dashboard.html   # 仪表板
│   ├── debug.html       # 调试工具
│   └── js/             # JavaScript 文件
│       ├── config.js    # 配置管理
│       └── mermaid.min.js # 流程图库
└── README.md           # 本文件
```

## API 配置

UI 通过 `/api/config` 端点获取 API 配置：

```javascript
// 自动从服务器加载配置
fetch('/api/config')
  .then(res => res.json())
  .then(config => {
    API_BASE_URL = config.apiBaseUrl;
  });
```

## 部署

### Docker 部署
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
EXPOSE 3000
CMD ["node", "server.js"]
```

### PM2 部署
```bash
pm2 start server.js --name pim-ui
pm2 save
pm2 startup
```

### Nginx 反向代理
```nginx
location / {
    proxy_pass http://localhost:3000;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection 'upgrade';
    proxy_set_header Host $host;
    proxy_cache_bypass $http_upgrade;
}
```

## 开发指南

### 添加新页面
1. 在 `public/` 下创建新的 HTML 文件
2. 在 `server.js` 中添加路由
3. 更新导航菜单

### 修改 API 调用
所有 API 调用都使用 `API_BASE_URL` 变量：
```javascript
fetch(API_BASE_URL + '/models')
```

### 调试
浏览器控制台会显示：
- API 请求日志
- 配置加载信息
- 错误信息

## 常见问题

### Q: 无法连接到 PIM Engine
A: 检查：
1. PIM Engine 是否正在运行
2. `.env` 中的 `API_BASE_URL` 是否正确
3. CORS 是否已在 PIM Engine 中启用

### Q: 页面显示 "Loading..."
A: 可能是配置未加载，检查：
1. `/api/config` 端点是否正常
2. `config.js` 是否正确引入

### Q: 上传文件失败
A: 确保：
1. 文件格式正确（.md, .yaml, .yml）
2. PIM Engine 有写入权限
3. 文件大小未超限

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License