#!/bin/bash

echo "=== PIM Engine AI Generation Test ==="
echo

# Check if npm packages are installed
if [ ! -d "node_modules" ]; then
    echo "Installing Puppeteer..."
    npm init -y
    npm install puppeteer
fi

# Check if Docker containers are running
echo "Checking Docker containers..."
docker compose -f docker-compose.llm.yml ps

# Check if pim-engine is running
if ! docker compose -f docker-compose.llm.yml ps | grep -q "pim-engine.*Up"; then
    echo "Starting PIM Engine with AI support..."
    ./start-with-gemini-linux.sh
    echo "Waiting for services to start..."
    sleep 15
fi

# Check API availability
echo "Checking API availability..."
curl -s http://localhost:8001/api/v1/codegen/llm/providers | python3 -m json.tool

echo
echo "Running Puppeteer test..."
node test_ai_generation.js

echo
echo "Test complete! Check the following:"
echo "1. ai_generation_result.png - Screenshot of the generation results"
echo "2. Console output above for code quality analysis"
echo "3. Docker logs: docker compose -f docker-compose.llm.yml logs pim-engine"