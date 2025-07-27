#!/bin/bash
# 安装 ReactAgent 兼容依赖的脚本

echo "Installing compatible dependencies for ReactAgent..."

# 升级 pip
pip install --upgrade pip

# 安装核心依赖
pip install pydantic==2.6.0
pip install langchain==0.3.27
pip install langchain-openai==0.3.28
pip install langchain-community==0.3.27
pip install langchain-core==0.3.27

# 安装其他必需依赖
pip install tiktoken
pip install python-dotenv
pip install sqlalchemy
pip install fastapi
pip install uvicorn
pip install httpx
pip install pytest
pip install pytest-asyncio

echo "Dependencies installed successfully!"
echo "Python version: $(python --version)"
echo "Pip packages:"
pip list | grep -E "pydantic|langchain|tiktoken"