# NLPL文件命名约定

## 文件扩展名

**统一使用`.md`扩展名**

理由：
- 获得所有Markdown工具的支持
- 强化"文档即程序"的理念
- 降低采用门槛

## 文件命名模式

### 可执行程序
```
data_conversion.md       # 数据转换程序
user_registration.md     # 用户注册流程
psm_generation.md       # PSM生成程序
```

### 库文件
```
stdlib/
  data/
    conversion.md       # 数据转换库
    validation.md       # 数据验证库
  web/
    api_testing.md      # API测试库
```

### 知识文档（也是程序）
```
knowledge/
  how_to_process_data.md     # 数据处理知识
  api_design_patterns.md     # API设计模式
  debugging_guide.md         # 调试指南
```

## 文件头部约定

在文件开头使用YAML front matter（可选）标记NLPL元信息：

```markdown
---
type: nlpl-program
version: 1.0
author: NLTM Engine
tags: [data-processing, conversion]
---

# 数据转换程序

## 目标
转换各种数据格式
```

但即使没有front matter，任何Markdown文件都是合法的NLPL程序。

## VSCode配置建议

### settings.json
```json
{
  "files.associations": {
    "*.md": "markdown"
  },
  "[markdown]": {
    "editor.wordWrap": "on",
    "editor.quickSuggestions": true,
    "editor.formatOnSave": true
  }
}
```

### 推荐插件
- Markdown All in One
- Markdown Preview Enhanced
- markdownlint

### 自定义代码片段

创建`.vscode/nlpl.code-snippets`:

```json
{
  "NLPL Program": {
    "prefix": "nlpl",
    "body": [
      "# ${1:程序名称}",
      "",
      "## 目标",
      "${2:程序目标描述}",
      "",
      "## 状态",
      "",
      "### 输入",
      "- **${3:变量}**: ${4:初始值}",
      "",
      "### 输出",
      "- **结果**: null",
      "",
      "## 主流程",
      "",
      "### 步骤1: ${5:步骤名称}",
      "- **动作**: ${6:动作描述}",
      "$0"
    ],
    "description": "创建NLPL程序模板"
  },
  "NLPL Step": {
    "prefix": "step",
    "body": [
      "### 步骤${1:N}: ${2:步骤名称}",
      "- **动作**: ${3:动作描述}",
      "- **工具**: `${4:tool_name}`",
      "- **输入**: ${5:输入}",
      "- **输出**: > ${6:状态.变量}"
    ],
    "description": "添加NLPL步骤"
  }
}
```

## GitHub集成

### .gitattributes
```
*.md linguist-language=Markdown
*.md linguist-documentation=false
```

这样GitHub会正确统计NLPL程序为代码而非文档。

## 项目结构示例

```
my-nlpl-project/
├── README.md                 # 项目说明（也可以是主程序）
├── main.md                   # 主程序入口
├── lib/                      # 项目库
│   ├── auth.md              # 认证流程
│   ├── data.md              # 数据处理
│   └── api.md               # API调用
├── knowledge/                # 知识库（也是程序库）
│   ├── business_rules.md    # 业务规则
│   └── best_practices.md    # 最佳实践
├── tests/                    # 测试程序
│   ├── test_auth.md         # 认证测试
│   └── test_data.md         # 数据测试
└── docs/                     # 纯文档
    └── architecture.md       # 架构说明
```

## 优势总结

使用`.md`扩展名：
1. ✅ 即时获得IDE支持
2. ✅ GitHub/GitLab自动渲染
3. ✅ 所有Markdown工具可用
4. ✅ 强化"文档即程序"理念
5. ✅ 零学习成本
6. ✅ 便于分享和协作

这个选择完美体现了NLPL的设计哲学：**不创造新事物，而是赋予现有事物新含义**。