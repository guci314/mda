#!/bin/bash

echo "=== Quick Gemini CLI Check ==="
echo

# 确保容器在运行
if ! docker ps | grep -q pim-engine; then
    echo "Starting container..."
    docker compose -f docker-compose.llm.yml up -d --build
    sleep 10
fi

echo "Checking Gemini CLI installation in Docker container..."
echo

# 检查安装情况
docker exec pim-engine bash -c '
    echo "1. Checking npm global packages:"
    npm list -g --depth=0 2>/dev/null | grep -i generative || echo "No generative-ai packages found"
    
    echo -e "\n2. Looking for CLI executables:"
    # Check common locations
    for cmd in gemini generative-ai-cli genai google-genai; do
        if which $cmd 2>/dev/null; then
            echo "Found: $cmd at $(which $cmd)"
            echo "Testing $cmd --help:"
            $cmd --help 2>&1 | head -5
        fi
    done
    
    echo -e "\n3. Checking /usr/local/bin:"
    ls -la /usr/local/bin/ | grep -v "^total" | grep -E "(gemini|genai|generative|google)" || echo "No matching files"
    
    echo -e "\n4. Checking node_modules/.bin:"
    ls -la /usr/local/lib/node_modules/@google/generative-ai-cli/bin/ 2>/dev/null || echo "CLI bin directory not found"
    
    echo -e "\n5. Package.json of installed package:"
    cat /usr/local/lib/node_modules/@google/generative-ai-cli/package.json 2>/dev/null | grep -E "(bin|name|version)" | head -10
'

echo -e "\n6. Testing with API key:"
docker exec pim-engine bash -c '
    export GOOGLE_AI_STUDIO_KEY="AIzaSyAK6A0j6OkkDaUd6nB2mgFuzjnWowKBaE0"
    
    # Try to find and run the CLI
    if which gemini 2>/dev/null; then
        echo "Testing: gemini --version"
        gemini --version 2>&1 || echo "Version command failed"
    elif which generative-ai-cli 2>/dev/null; then
        echo "Testing: generative-ai-cli --version"
        generative-ai-cli --version 2>&1 || echo "Version command failed"
    else
        echo "No CLI command found"
    fi
'