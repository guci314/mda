## API and Secret Management

### Secrets and API Keys
- API key for PIM compiler is located in `pim-compiler/.env` file
- Always use environment variables for sensitive configuration
- Never commit API keys or secrets directly to version control

### LLM Configurations
#### Kimi (Moonshot AI)
- **Model**: `kimi-k2-0711-preview`
- **Base URL**: `https://api.moonshot.cn/v1`
- **API Key Environment Variable**: `MOONSHOT_API_KEY`
- **Temperature**: 0 (for deterministic outputs)

#### DeepSeek
- **Model**: `deepseek-chat`
- **Base URL**: `https://api.deepseek.com/v1`
- **API Key Environment Variable**: `DEEPSEEK_API_KEY`
- **Temperature**: 0 (for deterministic outputs)

#### Gemini 2.5 Flash ⭐ (推荐 - 速度最快，效果最好)
- **Model**: `gemini-2.5-flash`
- **Base URL**: `https://generativelanguage.googleapis.com/v1beta/openai/`
- **API Key Environment Variable**: `GEMINI_API_KEY`
- **Temperature**: 0 (for deterministic outputs)
- **Performance**: 速度最快，效果最好 (Fastest speed, best performance)
- **Special Requirements**:
  - Requires httpx client with proxy configuration for Chinese network environment
  - Install httpx with SOCKS support: `pip install "httpx[socks]"`
  - Pydantic models must use `Union[str, None]` instead of `Optional[str]` for Gemini compatibility
  
Example configuration:
```python
import httpx

# Create httpx client with proxy
http_client = httpx.Client(
    proxy='socks5://127.0.0.1:7890',  # Or 'http://127.0.0.1:7890'
    timeout=30,
    verify=False
)

# LLM configuration
llm_model="gemini-2.5-flash",
llm_base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
llm_api_key_env="GEMINI_API_KEY",
http_client=http_client,
llm_temperature=0
```