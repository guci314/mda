#!/bin/bash
echo "=== 网络诊断 ==="
echo

echo "1. 测试DNS解析..."
nslookup api.deepseek.com || echo "DNS解析失败"
echo

echo "2. 测试网络连接..."
timeout 3 curl -v https://api.deepseek.com 2>&1 | head -20
echo

echo "3. 检查代理设置..."
env | grep -i proxy
echo

echo "4. 测试简单HTTP请求..."
timeout 5 curl -X POST "https://api.deepseek.com/v1/chat/completions" \
  -H "Authorization: Bearer $DEEPSEEK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "deepseek-chat", "messages": [{"role": "user", "content": "hi"}], "max_tokens": 5}' \
  2>&1 | head -30

echo
echo "诊断完成！"
