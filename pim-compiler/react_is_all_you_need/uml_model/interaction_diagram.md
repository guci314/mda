# React Agent 极简版 - 交互图

## 概述
这些交互图展示了极简React Agent系统的动态行为，展现了简约如何带来优雅。

## 1. 主执行流程

```mermaid
sequenceDiagram
    participant 用户
    participant Agent代理
    participant 记忆系统
    participant 大语言模型
    participant 工具

    用户->>Agent代理: run(任务)
    Agent代理->>Agent代理: _define_tools()
    Agent代理->>记忆系统: get_context_window()
    记忆系统-->>Agent代理: 最近消息
    
    loop 直到完成或达到最大轮数
        Agent代理->>大语言模型: _call_llm(消息, 工具)
        大语言模型-->>Agent代理: 响应
        
        alt 工具调用
            Agent代理->>工具: _execute_tool(名称, 参数)
            工具-->>Agent代理: 结果
            Agent代理->>记忆系统: add_message("tool", 结果)
        else 直接回答
            Agent代理->>记忆系统: add_message("assistant", 内容)
        end
        
        Agent代理->>Agent代理: 检查是否完成()
    end
    
    Agent代理-->>用户: 最终结果
```

## 2. 自然记忆压缩

```mermaid
sequenceDiagram
    participant Agent代理
    participant 记忆系统
    participant 压缩器

    Agent代理->>记忆系统: add_message(角色, 内容)
    记忆系统->>记忆系统: messages.append(消息)
    记忆系统->>记忆系统: 更新统计()
    
    alt 压力 > 阈值
        记忆系统->>记忆系统: should_compact() → true
        记忆系统->>压缩器: compact()
        
        Note over 压缩器: 提取智能精华
        压缩器->>压缩器: _generate_summary()
        压缩器->>压缩器: _extract_key_points()
        压缩器->>压缩器: _extract_task_results()
        
        压缩器->>记忆系统: CompressedMemory对象
        记忆系统->>记忆系统: compressed_history.append()
        记忆系统->>记忆系统: clear_window(保留上下文=true)
        
        opt 启用持久化
            记忆系统->>记忆系统: _save_history()
        end
    end
    
    记忆系统-->>Agent代理: 就绪
```

## 3. 工具执行管道

```mermaid
sequenceDiagram
    participant Agent代理
    participant 验证器
    participant 执行器
    participant 文件系统

    Agent代理->>Agent代理: 解析LLM的tool_call
    
    Agent代理->>验证器: 使用Pydantic模型验证
    alt 输入有效
        验证器-->>Agent代理: 验证通过的输入
        Agent代理->>执行器: 执行工具函数
        
        alt 文件操作
            执行器->>文件系统: 执行操作
            文件系统-->>执行器: 结果
        else 命令执行
            执行器->>执行器: subprocess.run()
        else 搜索操作
            执行器->>执行器: 模式匹配
        end
        
        执行器-->>Agent代理: 工具结果
    else 输入无效
        验证器-->>Agent代理: 验证错误
        Agent代理->>Agent代理: 返回错误给LLM
    end
```

## 4. API服务自动配置

```mermaid
sequenceDiagram
    participant 用户
    participant Agent代理
    participant 检测器
    participant 环境变量

    用户->>Agent代理: __init__(api_key=None)
    
    Agent代理->>检测器: _detect_base_url_for_key()
    
    alt 未提供API密钥
        检测器->>环境变量: 检查环境变量
        环境变量-->>检测器: 可用密钥
        
        alt DEEPSEEK_API_KEY存在
            检测器-->>Agent代理: "https://api.deepseek.com/v1"
        else MOONSHOT_API_KEY存在
            检测器-->>Agent代理: "https://api.moonshot.cn/v1"
        else OPENROUTER_API_KEY存在
            检测器-->>Agent代理: "https://openrouter.ai/api/v1"
        end
    else 提供了API密钥
        检测器->>检测器: 分析密钥模式
        检测器-->>Agent代理: 匹配的服务URL
    end
    
    Agent代理-->>用户: 配置完成并就绪
```

## 5. 呼吸循环（压缩-处理-解压）

```mermaid
sequenceDiagram
    participant 输入 as 高熵输入
    participant 压缩 as 压缩（吸入）
    participant 处理 as 处理（屏息）
    participant 解压 as 解压（呼出）
    participant 输出 as 低熵输出

    输入->>压缩: 原始任务/对话
    
    Note over 压缩: 提炼本质
    压缩->>处理: 压缩表示
    
    Note over 处理: 在压缩空间思考
    处理->>处理: 推理与规划
    
    处理->>解压: 处理后的思想
    Note over 解压: 扩展为详细响应
    
    解压->>输出: 结构化答案
```

## 6. 状态机

```mermaid
stateDiagram-v2
    [*] --> 空闲: 初始化
    
    空闲 --> 接收: 用户任务
    接收 --> 思考: 处理任务
    
    思考 --> 行动: 需要工具
    思考 --> 响应: 直接回答
    
    行动 --> 观察: 执行工具
    观察 --> 思考: 处理结果
    
    响应 --> 压缩: 检查记忆压力
    压缩 --> 空闲: 任务完成
    
    思考 --> 失败: 超过最大轮数
    失败 --> 空闲: 重置
```

## 7. 记忆生命周期

```mermaid
graph LR
    A[新消息] --> B{记忆压力?}
    B -->|低| C[添加到窗口]
    B -->|高| D[触发压缩]
    
    D --> E[提取摘要]
    D --> F[提取要点]
    D --> G[提取结果]
    
    E --> H[创建CompressedMemory]
    F --> H
    G --> H
    
    H --> I[添加到历史]
    I --> J[清空窗口]
    J --> K[保留上下文]
    K --> C
    
    C --> L{持久化?}
    L -->|是| M[保存到磁盘]
    L -->|否| N[仅内存]
```

## 8. 完整任务流程示例

```mermaid
sequenceDiagram
    participant 用户
    participant Agent代理
    participant 记忆
    participant LLM
    participant 写文件 as write_file
    participant 读文件 as read_file

    用户->>Agent代理: "创建一个Python计算器"
    
    Agent代理->>记忆: add_message("user", 任务)
    Agent代理->>LLM: "创建包含+,-,*,/的计算器"
    
    LLM-->>Agent代理: "我将创建calculator.py"
    Agent代理->>记忆: add_message("assistant", 思考)
    
    LLM-->>Agent代理: tool_call(write_file, {路径: "calculator.py", 内容: "..."})
    Agent代理->>写文件: 执行
    写文件-->>Agent代理: "文件已创建"
    Agent代理->>记忆: add_message("tool", 结果)
    
    Agent代理->>LLM: "文件已创建，现在测试"
    LLM-->>Agent代理: tool_call(read_file, {路径: "calculator.py"})
    Agent代理->>读文件: 执行
    读文件-->>Agent代理: 文件内容
    
    Agent代理->>记忆: 检查压力(5条消息)
    记忆-->>Agent代理: 低于阈值
    
    Agent代理->>LLM: "验证实现"
    LLM-->>Agent代理: "计算器完成，包含4个操作"
    
    Agent代理-->>用户: 返回结果：成功创建calculator.py
```

## 性能特征

### 时间复杂度
| 操作 | 复杂度 | 说明 |
|------|--------|------|
| add_message | O(1) | 追加到列表 |
| should_compact | O(1) | 简单比较 |
| compact | O(n) | 处理n条消息 |
| get_context_window | O(k) | 返回k条最近消息 |

### 空间复杂度
| 组件 | 复杂度 | 说明 |
|------|--------|------|
| 消息窗口 | O(阈值) | 受压力阈值限制 |
| 压缩历史 | O(压缩次数) | 对数增长 |
| 总记忆 | O(log n) | 由于压缩 |

## 关键洞察

### 1. **线性简约**
主流程完全线性：
- 接收任务 → 思考 → 行动 → 观察 → 重复

### 2. **自然压力释放**
记忆压缩在压力累积时自然发生：
- 无复杂调度
- 无外部触发
- 只是自然的压力释放

### 3. **最小状态**
系统维护最小状态：
- 当前消息窗口
- 压缩历史
- 简单统计

### 4. **工具透明性**
工具只是带验证的函数：
- 通过Pydantic进行输入验证
- 简单执行
- 清晰结果

## 与复杂系统的对比

| 方面 | 复杂系统 | 极简系统 |
|------|---------|---------| 
| 记忆层数 | 3-6层 | 1层 |
| 状态管理 | 复杂FSM | 简单循环 |
| 配置参数 | 20+ | 1个 |
| 依赖 | 多 | 少 |
| 认知负载 | 高 | 低 |

## 实践中的哲学

交互模式展示了：

1. **呼吸**：压缩 → 处理 → 解压
2. **自然流动**：如水自然找到其水平
3. **涌现**：简单规则产生复杂行为
4. **极简主义**：每个交互都有目的

> "最好的系统不是功能最多的，而是意外最少的。"