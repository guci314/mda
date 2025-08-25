## API and Secret Management

### Secrets and API Keys
- API key for PIM compiler is located in `pim-compiler/.env` file
- Always use environment variables for sensitive configuration
- Never commit API keys or secrets directly to version control

### LLM Configurations
#### Kimi (Moonshot AI)
- **Models**: 
  - `kimi-k2-0711-preview` (128k context)
  - `kimi-k2-turbo-preview` (128k context)
- **Base URL**: `https://api.moonshot.cn/v1`
- **API Key Environment Variable**: `MOONSHOT_API_KEY`
- **Temperature**: 0 (for deterministic outputs)

#### DeepSeek
- **Model**: `deepseek-chat`
- **Base URL**: `https://api.deepseek.com/v1`
- **API Key Environment Variable**: `DEEPSEEK_API_KEY`
- **Temperature**: 0 (for deterministic outputs)

#### Qwen3 Coder (通义千问 - 代码能力强)
- **Models**: 
  - `qwen/qwen3-coder` (推荐 - 优化用于agent编码任务，支持function calling和tool use)
  - `qwen/qwen-2.5-coder-32b-instruct` (备选 - Qwen2.5版本)
  - `qwen/qwq-32b-preview` (深度推理)
  - `qwen/qwen-2-72b-instruct` (大模型)
- **Base URL**: `https://openrouter.ai/api/v1`
- **API Key Environment Variable**: `OPENROUTER_API_KEY`
- **Temperature**: 0.3 (for code generation)
- **Special Features**:
  - 专门优化用于agent编码任务
  - 支持function calling和tool use
  - 长上下文推理能力（repository级别）
  - 强大的代码生成和调试能力
  - 支持更长的上下文窗口（单次输出8000字符）
  - 通过OpenRouter访问

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
- 我说使用kimi，默认使用kimi-k2-turbo-preview

## 核心理论

### React + 文件系统 = 冯·诺依曼架构

**公式**：React + 文件系统 = 冯·诺依曼架构 = 图灵完备 + 无限存储 = 可计算函数的全集

**要点**：
- React本身是图灵完备的，但受限于有限上下文（像只有寄存器的CPU）
- 文件系统提供无限存储，突破上下文窗口限制
- 组合构成完整计算架构：
  - CPU = React Agent
  - RAM = 上下文窗口
  - 硬盘 = 文件系统
  - 程序 = 知识文件
  - 数据 = 工作文件
- 结果是可计算函数的全集：不仅理论可计算，而且实际可执行
- 知识文件是程序，不是数据
- 元认知通过知识实现，不需要复杂代码
- 系统可以自举：生成和修改自己的知识文件

## 核心代码目录
pim-compiler/react_is_all_you_need
此目录是项目的核心代码目录，其它目录都是废弃的代码