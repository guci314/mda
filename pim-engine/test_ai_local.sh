#!/bin/bash

echo "=== Testing AI Code Generation Locally ==="
echo

# 1. 先确保模型已加载
echo "1. Checking loaded models:"
curl --noproxy localhost -s http://localhost:8000/api/v1/models | python3 -m json.tool

# 2. 测试简单的 Gemini CLI 调用
echo -e "\n2. Testing Gemini CLI directly:"
GEMINI_API_KEY="AIzaSyAK6A0j6OkkDaUd6nB2mgFuzjnWowKBaE0" \
HTTP_PROXY="http://127.0.0.1:7890" \
HTTPS_PROXY="http://127.0.0.1:7890" \
gemini -p "Write a Python function that adds two numbers. Only code, no explanation." 2>&1 | head -30

# 3. 测试 AI 代码生成 API
echo -e "\n3. Testing AI code generation via API:"
echo "Generating code for user_management model..."
curl --noproxy localhost -X POST http://localhost:8000/api/v1/codegen/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model_name": "user_management",
    "platform": "fastapi",
    "use_llm": true,
    "llm_provider": "gemini",
    "options": {
      "use_llm_for_all": true
    }
  }' -s | python3 -m json.tool > ai_generation_result.json

# 检查结果
if [ -s ai_generation_result.json ]; then
    echo "✅ Generation complete! Result saved to ai_generation_result.json"
    
    # 显示生成的文件列表
    echo -e "\nGenerated files:"
    python3 -c "
import json
with open('ai_generation_result.json') as f:
    data = json.load(f)
    if 'files' in data:
        for file in data['files']:
            print(f\"  - {file['path']}\")
        print(f\"\\nTotal files: {len(data['files'])}\")
        
        # 检查是否有真实实现
        has_impl = any('TODO' not in f.get('content', '') for f in data['files'])
        print(f\"Has real implementation: {'✅ Yes' if has_impl else '❌ No'}\")
    else:
        print('Error:', data.get('detail', 'Unknown error'))
"
else
    echo "❌ Generation failed"
fi

# 4. 对比模板生成
echo -e "\n4. Comparing with template generation:"
curl --noproxy localhost -X POST http://localhost:8000/api/v1/codegen/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model_name": "user_management",
    "platform": "fastapi",
    "use_llm": false
  }' -s | python3 -m json.tool > template_generation_result.json

echo "Template generation saved to template_generation_result.json"

# 显示对比
echo -e "\nComparison:"
echo "AI Generation:"
grep -c "TODO" ai_generation_result.json || echo "  No TODOs found ✅"
echo "Template Generation:"
grep -c "TODO" template_generation_result.json && echo "  Contains TODOs ❌"

echo -e "\n✅ Test complete!"
echo "Check ai_generation_result.json for full AI-generated code"