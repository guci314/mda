#!/bin/bash

echo "=== Setting up PIM Engine for Local Development ==="
echo

# 1. 检查 Python 版本
echo "1. Checking Python version..."
python3 --version

# 2. 创建虚拟环境（如果不存在）
if [ ! -d "venv" ]; then
    echo "2. Creating virtual environment..."
    python3 -m venv venv
else
    echo "2. Virtual environment already exists"
fi

# 3. 激活虚拟环境
echo "3. Activating virtual environment..."
source venv/bin/activate

# 4. 升级 pip
echo "4. Upgrading pip..."
pip install --upgrade pip

# 5. 安装依赖
echo "5. Installing dependencies..."
pip install -r requirements.txt

# 6. 安装额外的 LLM 依赖
echo "6. Installing LLM dependencies..."
pip install anthropic aiohttp httpx psycopg2-binary

# 7. 检查 Gemini CLI
echo -e "\n7. Checking Gemini CLI..."
if ! which gemini > /dev/null 2>&1; then
    echo "Gemini CLI not found. Installing..."
    npm install -g @google/gemini-cli
else
    echo "Gemini CLI already installed:"
    gemini --version
fi

echo -e "\n✅ Setup complete!"
echo "To start the engine, run:"
echo "  source venv/bin/activate"
echo "  ./start_local.sh"