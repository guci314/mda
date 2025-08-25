# 如何使用NLTM系统

## 概述
NLTM (Natural Language Turing Machine) 是一个知识驱动的执行系统，不需要编写Python代码，只需要知识文件和Agent配置。

## 系统架构

```
用户请求(自然语言)
    ↓
编导Agent(读取director_agent_as_tool.md)
    ↓
生成NLPL程序
    ↓
执行Agent工具(读取executor_agent_as_tool.md)
    ↓
返回结果
```

## 使用方法

### 1. 对于使用LangChain的Agent（如DeepSeek、Gemini）

创建两个Agent作为工具：

```python
# 编导Agent工具
director_tool = {
    "name": "nltm_director",
    "description": "生成NLPL程序",
    "knowledge": "knowledge/nltm/director_agent_as_tool.md"
}

# 执行Agent工具
executor_tool = {
    "name": "nltm_executor", 
    "description": "执行NLPL程序",
    "knowledge": "knowledge/nltm/executor_agent_as_tool.md"
}
```

### 2. 执行流程

当用户提交请求时：

```yaml
第1步 - 调用编导工具:
  输入: 用户请求
  知识: director_agent_as_tool.md
  输出: NLPL程序 + 初始状态

第2步 - 调用执行工具:
  输入: NLPL程序 + 初始状态
  知识: executor_agent_as_tool.md
  输出: 执行结果

第3步 - 返回给用户:
  将执行结果转换为自然语言
```

### 3. 实际案例

#### 用户请求
"帮我分析这组数据 [10, 20, 30, 40, 50] 的统计信息"

#### 编导Agent生成的NLPL
```yaml
程序: 数据统计分析
  目标: 分析数组的统计信息
  
  状态:
    数据: [10, 20, 30, 40, 50]
    统计:
      总和: null
      平均: null
      最大: null
      最小: null
    完成: false
    
  主流程:
    步骤1_计算总和:
      动作: 计算数据总和
      保存到: 状态.统计.总和
      
    步骤2_计算平均:
      动作: 计算数据平均值
      保存到: 状态.统计.平均
      
    步骤3_找最值:
      动作: 找出最大值和最小值
      保存到: 状态.统计.最大, 状态.统计.最小
      
    步骤4_完成:
      设置: 状态.完成 = true
      返回: 状态.统计
```

#### 执行Agent的结果
```json
{
  "success": true,
  "final_state": {
    "数据": [10, 20, 30, 40, 50],
    "统计": {
      "总和": 150,
      "平均": 30,
      "最大": 50,
      "最小": 10
    },
    "完成": true
  }
}
```

#### 返回给用户
"分析完成！数据 [10, 20, 30, 40, 50] 的统计结果：
- 总和：150
- 平均值：30
- 最大值：50
- 最小值：10"

## 知识文件的作用

### director_agent_as_tool.md
- 定义如何理解用户意图
- 提供NLPL生成模板
- 包含错误处理策略

### executor_agent_as_tool.md
- 定义如何解析NLPL
- 规定执行规则
- 处理状态更新

### nlpl_templates.md
- 提供常见任务的NLPL模板
- 可以扩展新的模板

## 优势

1. **纯知识驱动** - 不需要编写代码
2. **易于修改** - 修改知识文件即可改变行为
3. **可解释** - 每个决策都有知识依据
4. **通用性** - 适用于任何支持工具调用的Agent

## 扩展方法

### 添加新的任务类型
在`nlpl_templates.md`中添加新模板：
```yaml
程序: 新任务类型
  目标: [目标描述]
  状态: [状态设计]
  主流程: [执行步骤]
```

### 增强执行能力
在`executor_agent_as_tool.md`中添加新的动作识别：
```yaml
当遇到 "动作: 新功能":
  - 执行新功能逻辑
  - 更新相应状态
```

### 优化生成策略
在`director_agent_as_tool.md`中添加新的模式：
```yaml
新模式:
  触发词: [关键词列表]
  生成: [对应的NLPL模板]
```

## 注意事项

1. **知识文件是核心** - 系统行为完全由知识文件定义
2. **不需要Python类** - Agent直接读取知识文件执行
3. **保持简单** - NLPL应该简洁明了
4. **测试优先** - 新模板要先测试验证
5. **文档重要** - 知识就是文档，文档就是程序

## 总结

NLTM实现了真正的知识驱动计算：
- **程序 = 自然语言(NLPL)**
- **执行器 = LLM + 知识文件**
- **无需传统编程**

这是计算范式的根本转变：从代码驱动到知识驱动。