# 网络配置与故障排除指南

## API超时问题解决方案

### 1. 已实施的改进
- ✅ **增加超时时间**: 从30秒增加到60秒
- ✅ **自动重试机制**: 失败后自动重试3次
- ✅ **延迟重试**: 每次重试前等待2秒

### 2. 网络代理配置（如需要）

如果您在中国大陆，可能需要配置代理：

```python
import httpx

# 配置代理客户端
http_client = httpx.Client(
    proxy='socks5://127.0.0.1:7890',  # 或 'http://127.0.0.1:7890'
    timeout=60,
    verify=False
)

# 创建Agent时传入
agent = ReactAgentMinimal(
    work_dir="my_project",
    pressure_threshold=50,
    model="deepseek-chat",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    http_client=http_client  # 传入代理客户端
)
```

### 3. 使用备选API服务

如果DeepSeek连接不稳定，可以尝试其他服务：

#### OpenRouter（推荐）
```python
agent = ReactAgentMinimal(
    work_dir="my_project",
    pressure_threshold=50,
    model="qwen/qwen3-coder",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)
```

#### Moonshot (Kimi)
```python
agent = ReactAgentMinimal(
    work_dir="my_project",
    pressure_threshold=50,
    model="kimi-k2-turbo-preview",
    api_key=os.getenv("MOONSHOT_API_KEY"),
    base_url="https://api.moonshot.cn/v1"
)
```

### 4. 测试网络连接

```bash
# 测试DeepSeek API连接
curl https://api.deepseek.com/v1/models \
  -H "Authorization: Bearer $DEEPSEEK_API_KEY"

# 测试延迟
ping api.deepseek.com
```

### 5. 环境变量配置

在`.env`文件中配置多个API密钥作为备选：

```env
# 主要服务
DEEPSEEK_API_KEY=your_deepseek_key

# 备选服务
OPENROUTER_API_KEY=your_openrouter_key
MOONSHOT_API_KEY=your_moonshot_key
GEMINI_API_KEY=your_gemini_key

# 代理设置（如需要）
HTTP_PROXY=http://127.0.0.1:7890
HTTPS_PROXY=http://127.0.0.1:7890
```

### 6. 错误类型说明

- **Timeout**: 网络延迟太高，增加超时时间或使用代理
- **Connection Error**: 无法连接到API，检查网络和防火墙
- **401 Unauthorized**: API密钥错误
- **422 Unprocessable Entity**: 请求格式错误（已修复）
- **429 Too Many Requests**: 速率限制，稍后重试

### 7. 高级配置

如果需要更多控制，可以修改ReactAgentMinimal的初始化参数：

```python
class ReactAgentMinimal:
    def __init__(self, 
                 # ... 其他参数
                 timeout: int = 60,          # API超时时间
                 max_retries: int = 3,       # 最大重试次数
                 retry_delay: int = 2):      # 重试延迟（秒）
```

## 推荐配置

对于稳定性最优的配置，建议：

1. **使用OpenRouter** - 全球CDN，稳定性好
2. **配置代理** - 如果在网络受限地区
3. **设置多个API密钥** - 自动故障转移

## 联系支持

如果问题持续，请检查：
- API服务状态页面
- 本地网络连接
- 防火墙设置
- VPN/代理配置