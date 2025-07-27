#!/bin/bash
# 设置虚拟环境并安装依赖

# 确保在正确的目录
cd /home/guci/aiProjects/mda/pim-compiler

echo "激活虚拟环境..."
source venv_test/bin/activate

echo "升级 pip..."
pip install --upgrade pip

echo "安装基础依赖..."
if [ -f requirements.txt ]; then
    pip install -r requirements.txt
else
    echo "requirements.txt 不存在，创建基础依赖文件..."
    cat > requirements.txt << EOF
# Core dependencies
fastapi>=0.68.0,<0.69.0
uvicorn>=0.15.0
sqlalchemy>=1.4.22,<2.0.0
pydantic>=1.8.0,<2.0.0
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
python-multipart>=0.0.5
aiofiles>=0.8.0
httpx>=0.23.0
python-dotenv>=0.19.0

# LLM providers
openai>=1.0.0
google-generativeai>=0.3.0
anthropic>=0.7.0

# LangChain ecosystem
langchain>=0.3.0
langchain-openai>=0.2.0
langchain-community>=0.3.0
langchain-core>=0.3.0

# Multi-agent frameworks
pyautogen>=0.2.0

# Utilities
click>=8.0.0
rich>=13.0.0
tenacity>=8.0.0
EOF
    pip install -r requirements.txt
fi

echo "安装开发依赖..."
if [ -f requirements-dev.txt ]; then
    pip install -r requirements-dev.txt
else
    echo "requirements-dev.txt 不存在，跳过..."
fi

echo ""
echo "验证安装..."
echo "Python 版本: $(python --version)"
echo "pip 版本: $(pip --version)"
echo ""
echo "已安装的关键包:"
pip list | grep -E "fastapi|pydantic|langchain|pyautogen|deepseek"

echo ""
echo "虚拟环境设置完成！"
echo "使用以下命令激活虚拟环境："
echo "  source venv_test/bin/activate"