#!/bin/bash

echo "=== Testing Gemini CLI in Running Container ==="
echo

# 1. 检查 Gemini CLI
echo "1. Gemini CLI Status:"
docker exec pim-engine bash -c "gemini --version 2>&1 || echo 'Version command not supported'"

# 2. 设置 API Key
echo -e "\n2. Setting up API Key..."
API_KEY="AIzaSyAK6A0j6OkkDaUd6nB2mgFuzjnWowKBaE0"

# 3. 测试简单提示
echo -e "\n3. Testing simple prompt:"
docker exec pim-engine bash -c "
export GOOGLE_AI_STUDIO_KEY='$API_KEY'
export HTTP_PROXY='http://host.docker.internal:7890'
export HTTPS_PROXY='http://host.docker.internal:7890'

echo 'Say Hello World' | gemini --api-key '$API_KEY' 2>&1 | head -20
"

# 4. 测试代码生成
echo -e "\n4. Testing code generation:"
docker exec pim-engine bash -c "
export GOOGLE_AI_STUDIO_KEY='$API_KEY'
export HTTP_PROXY='http://host.docker.internal:7890'
export HTTPS_PROXY='http://host.docker.internal:7890'

gemini --api-key '$API_KEY' -p 'Write a Python function that adds two numbers. Only output the code, no explanation.' 2>&1 | head -30
"

# 5. 重新加载模型
echo -e "\n5. Reloading todo_management model:"
curl -X POST http://localhost:8001/api/v1/models/todo_management/reload

# 6. 检查 LLM 提供商
echo -e "\n\n6. Checking LLM providers:"
curl -s http://localhost:8001/api/v1/codegen/llm/providers | python3 -m json.tool

# 7. 测试 AI 代码生成 API
echo -e "\n7. Testing AI code generation via API:"
curl -X POST http://localhost:8001/api/v1/codegen/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model_name": "todo_management",
    "platform": "fastapi",
    "use_llm": true,
    "llm_provider": "gemini"
  }' | python3 -m json.tool | head -50

echo -e "\nTest complete!"