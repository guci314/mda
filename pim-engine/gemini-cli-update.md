# Gemini CLI 更新说明

## 安装包更正

根据官方 GitHub 仓库 (https://github.com/google-gemini/gemini-cli)，正确的安装方式是：

```bash
npm install -g @google/generative-ai-cli
```

## 已更新的文件

1. **Dockerfile.llm** - 第15行
   - 从: `npm install -g @google/gemini-cli`
   - 改为: `npm install -g @google/generative-ai-cli`

2. **gemini_provider.py** - 调用方式
   - 从: 使用临时文件传递 prompt
   - 改为: 使用 `-p` 参数直接传递 prompt

## 需要确认的事项

1. **CLI 命令名称**
   安装 `@google/generative-ai-cli` 后，实际的命令可能是：
   - `gemini` (当前代码中使用的)
   - `generative-ai-cli`
   - 或其他名称

2. **API Key 参数**
   需要确认正确的参数格式：
   - `--api-key` (当前使用)
   - `--key`
   - 或通过环境变量 `GOOGLE_AI_API_KEY`

## 测试步骤

重新构建 Docker 镜像并测试：

```bash
# 重新构建镜像
docker compose -f docker-compose.llm.yml build --no-cache

# 启动服务
./start-with-gemini-linux.sh

# 进入容器测试 CLI
docker exec -it pim-engine bash

# 在容器内测试
which gemini  # 或 which generative-ai-cli
gemini --help  # 查看帮助信息
```

## 可能的调整

如果命令名称不是 `gemini`，需要更新 `gemini_provider.py` 第14行：

```python
self.cli_path = "正确的命令名称"
```

## 参考资源

- GitHub: https://github.com/google-gemini/gemini-cli
- NPM: https://www.npmjs.com/package/@google/generative-ai-cli