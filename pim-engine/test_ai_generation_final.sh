#!/bin/bash

echo "=== Final AI Generation Test ==="
echo

# 设置环境变量
export GOOGLE_AI_STUDIO_KEY="AIzaSyAK6A0j6OkkDaUd6nB2mgFuzjnWowKBaE0"

# 1. 检查健康状态
echo "1. Checking API health:"
curl --noproxy localhost -s http://localhost:8001/health | python3 -m json.tool

# 2. 检查 LLM 提供商
echo -e "\n2. Checking LLM providers:"
curl --noproxy localhost -s http://localhost:8001/api/v1/codegen/llm/providers | python3 -m json.tool

# 3. 在容器中测试 Gemini CLI
echo -e "\n3. Testing Gemini CLI directly:"
docker exec pim-engine bash -c "
export GOOGLE_AI_STUDIO_KEY='AIzaSyAK6A0j6OkkDaUd6nB2mgFuzjnWowKBaE0'
export HTTP_PROXY='http://host.docker.internal:7890'
export HTTPS_PROXY='http://host.docker.internal:7890'

# 测试简单提示
gemini -p 'Write a Python function add(a, b) that returns a+b. Only code, no explanation.' 2>&1 | head -50
"

# 4. 重新加载 todo 模型
echo -e "\n4. Reloading todo_management model:"
docker exec pim-engine bash -c "
cd /app
python -c '
from core.engine import engine
try:
    engine.reload_model(\"todo_management\")
    print(\"Model reloaded successfully\")
except Exception as e:
    print(f\"Failed to reload: {e}\")
'
"

# 5. 测试 AI 代码生成 API
echo -e "\n5. Testing AI code generation via API:"
curl --noproxy localhost -X POST http://localhost:8001/api/v1/codegen/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model_name": "user_management",
    "platform": "fastapi",
    "use_llm": true,
    "llm_provider": "gemini"
  }' -s | python3 -m json.tool | head -100

echo -e "\nTest complete!"