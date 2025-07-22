# MDA 项目设置指南

## 环境配置

### 1. 设置 Gemini API Key

本项目使用 Gemini CLI 进行智能模型转换，需要配置 API key。

#### 方法一：使用项目 .env 文件（推荐）

1. 复制环境变量模板：
   ```bash
   cp .env.example .env
   ```

2. 编辑 `.env` 文件，替换 API key：
   ```bash
   # 编辑 .env 文件
   nano .env
   
   # 将 your_actual_api_key_here 替换为您的实际 API key
   GEMINI_API_KEY=your_actual_api_key_here
   ```

3. `.env` 文件已在 `.gitignore` 中，不会被提交到版本控制

#### 方法二：设置环境变量

```bash
export GEMINI_API_KEY=your_actual_api_key_here
```

### 2. 代理配置（可选）

如果需要使用代理，在 `.env` 文件中配置：

```env
HTTP_PROXY=http://127.0.0.1:7890
HTTPS_PROXY=http://127.0.0.1:7890
```

### 3. 安装依赖

```bash
cd pim-engine
pip install -r requirements.txt
```

## 使用说明

### 运行 MDA 转换

```bash
# 转换 PIM 模型为可执行代码
python mda.py models/图书管理系统.md --platform fastapi
```

### 运行测试

```bash
# 运行所有测试（需要 API key）
python -m pytest tests/ -v

# 只运行结构测试（不需要 API key）
python -m pytest tests/converters/test_converters_structure.py -v
```

## 获取 Gemini API Key

1. 访问 [Google AI Studio](https://makersuite.google.com/app/apikey)
2. 创建或选择一个项目
3. 生成 API key
4. 将 API key 保存到 `.env` 文件

## 故障排除

### 错误：GEMINI_API_KEY environment variable not found

确保：
1. `.env` 文件存在于项目根目录
2. `.env` 文件中包含有效的 `GEMINI_API_KEY=xxx` 行
3. API key 没有空格或引号

### 错误：Gemini CLI not found

确保已安装 Gemini CLI：
```bash
npm install -g @anthropic/gemini
```

或检查 Gemini CLI 路径：
```bash
which gemini
```