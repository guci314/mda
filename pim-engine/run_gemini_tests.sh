#!/bin/bash

echo "=== Gemini CLI Docker Test ==="
echo

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if containers are running
echo "Checking Docker containers..."
if ! docker compose -f docker-compose.llm.yml ps | grep -q "pim-engine.*Up"; then
    echo -e "${YELLOW}Starting containers...${NC}"
    docker compose -f docker-compose.llm.yml up -d --build
    echo "Waiting for services to start..."
    sleep 10
fi

# Run tests inside the container
echo -e "\n${GREEN}Running Gemini CLI tests in Docker container...${NC}\n"

# First, let's check what command names are available
echo "1. Checking available commands in container:"
docker exec pim-engine bash -c "
    echo 'Checking for gemini...'
    which gemini 2>/dev/null || echo 'gemini not found'
    
    echo -e '\nChecking for generative-ai-cli...'
    which generative-ai-cli 2>/dev/null || echo 'generative-ai-cli not found'
    
    echo -e '\nChecking for genai...'
    which genai 2>/dev/null || echo 'genai not found'
    
    echo -e '\nAll commands in /usr/local/bin:'
    ls -la /usr/local/bin/ | grep -E '(gemini|genai|generative)' || echo 'No matching commands found'
    
    echo -e '\nNPM global packages:'
    npm list -g --depth=0 | grep -E '(gemini|generative)' || echo 'No matching npm packages'
"

echo -e "\n2. Running pytest tests:"
# Copy test file to container if needed
docker cp tests/test_gemini_cli.py pim-engine:/app/tests/

# Run pytest in container
docker exec pim-engine bash -c "
    cd /app
    # Install pytest if not already installed
    pip install pytest pytest-asyncio 2>/dev/null
    
    # Set environment variables
    export GOOGLE_AI_STUDIO_KEY='${GOOGLE_AI_STUDIO_KEY:-AIzaSyAK6A0j6OkkDaUd6nB2mgFuzjnWowKBaE0}'
    export PROXY_HOST='${PROXY_HOST:-host.docker.internal}'
    export PROXY_PORT='${PROXY_PORT:-7890}'
    
    # Run tests
    python -m pytest tests/test_gemini_cli.py -v -s --tb=short
"

# Check test results
if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}✓ All tests passed!${NC}"
else
    echo -e "\n${RED}✗ Some tests failed${NC}"
    echo -e "\n${YELLOW}Troubleshooting tips:${NC}"
    echo "1. Check if the correct npm package is installed in Dockerfile.llm"
    echo "2. Verify the command name after installation"
    echo "3. Check Docker logs: docker compose -f docker-compose.llm.yml logs pim-engine"
    echo "4. Try rebuilding without cache: docker compose -f docker-compose.llm.yml build --no-cache"
fi

echo -e "\n3. Additional diagnostics:"
docker exec pim-engine bash -c "
    echo 'Node version:' && node --version
    echo 'NPM version:' && npm --version
    echo -e '\nEnvironment variables:'
    env | grep -E '(GEMINI|GOOGLE_AI|PROXY)' | sort
"