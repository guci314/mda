# 在 VSCode 中运行 PIM Engine

## 快速开始

### 1. 打开项目
在 VSCode 中打开 MDA 项目根目录：
```bash
cd /home/guci/aiProjects/mda
code .
```

### 2. 安装依赖（如果需要）
```bash
pip install -r pim-engine/requirements.txt
```

### 3. 配置环境变量
创建或编辑 `pim-engine/.env` 文件：
```env
# 基础配置
DATABASE_URL=sqlite:///./pim_engine.db
LOG_LEVEL=INFO
HOT_RELOAD=true
PORT=8001

# Gemini 配置（可选）
GOOGLE_AI_STUDIO_KEY=your-api-key
LLM_PROVIDER=gemini
PROXY_HOST=127.0.0.1
PROXY_PORT=7890
```

### 4. 运行程序

#### 方法一：使用调试配置（推荐）
1. 按 `F5` 或点击左侧调试图标
2. 在顶部下拉菜单选择运行配置：
   - **PIM Engine**: 基础运行配置
   - **PIM Engine (with Gemini)**: 带 Gemini API 支持
   - **MDA Orchestrator**: 运行代码生成器
   - **Python: Current File**: 运行当前文件

3. 点击绿色运行按钮

#### 方法二：使用终端
```bash
cd pim-engine/src
python main.py
```

#### 方法三：使用任务（Tasks）
按 `Ctrl+Shift+P`，输入 "Run Task"，选择 "Start PIM Engine"

## 调试技巧

### 设置断点
- 在代码行号左侧点击设置断点
- 程序会在断点处暂停

### 查看变量
- 在调试面板查看局部变量
- 悬停在变量上查看值
- 使用调试控制台执行表达式

### 调试配置说明

1. **PIM Engine**
   - 运行主引擎，自动加载 models/ 目录下的模型
   - API 地址：http://localhost:8001

2. **PIM Engine (with Gemini)**
   - 包含 Gemini API 配置
   - 支持代码生成功能

3. **MDA Orchestrator**
   - 运行 PIM 到代码的完整转换流程
   - 默认处理 user_management.yaml

## 常见问题

### 1. 找不到模块
确保运行路径正确：
```bash
cd pim-engine/src
export PYTHONPATH=$PWD
```

### 2. 端口被占用
修改 `.env` 中的 PORT 或在调试配置中修改

### 3. 数据库错误
删除旧的数据库文件：
```bash
rm pim-engine/src/pim_engine.db
```

### 4. Gemini API 错误
- 检查 API key 是否正确
- 检查代理设置
- 确认网络连接

## VSCode 插件推荐

- **Python**: 基础 Python 支持
- **Pylance**: 智能提示和类型检查
- **Python Debugger**: 调试支持
- **Black Formatter**: 代码格式化
- **GitLens**: Git 集成
- **Thunder Client**: API 测试

## 快捷键

- `F5`: 开始调试
- `Shift+F5`: 停止调试
- `F9`: 设置/取消断点
- `F10`: 单步跳过
- `F11`: 单步进入
- `Ctrl+Shift+F5`: 重启调试

## 项目结构

```
mda/
├── .vscode/               # VSCode 配置
│   ├── launch.json       # 调试配置
│   ├── settings.json     # 编辑器设置
│   └── tasks.json        # 任务配置
├── pim-engine/           # PIM 引擎
│   ├── src/              # 源代码
│   │   └── main.py       # 主程序入口
│   ├── models/           # PIM 模型
│   └── requirements.txt  # 依赖列表
└── models/               # 共享模型文件
```