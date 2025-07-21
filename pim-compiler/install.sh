#!/bin/bash
# PIM Compiler 安装脚本

echo "Installing PIM Compiler..."

# 检查 Python 版本
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.8"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
    echo "Error: Python 3.8 or higher is required. Found: $python_version"
    exit 1
fi

# 创建虚拟环境（如果不存在）
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo "Installing dependencies..."
pip install -q --upgrade pip
pip install -q requests python-dotenv

# 创建符号链接到本地 bin
mkdir -p ~/.local/bin
ln -sf "$(pwd)/pim-compiler" ~/.local/bin/pim-compiler

# 检查 PATH
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo ""
    echo "⚠️  Please add ~/.local/bin to your PATH:"
    echo "   echo 'export PATH=\"\$HOME/.local/bin:\$PATH\"' >> ~/.bashrc"
    echo "   source ~/.bashrc"
fi

echo ""
echo "✅ Installation complete!"
echo ""
echo "Usage:"
echo "  pim-compiler model.md              # Compile a PIM file"
echo "  pim-compiler --help                # Show help"
echo ""
echo "Quick start:"
echo "  1. Create a PIM file (e.g., model.md)"
echo "  2. Run: pim-compiler model.md"
echo "  3. Check the output directory for generated code"