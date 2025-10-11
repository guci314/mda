# 工作流文档知识图谱摘要

## 知识图谱概述

基于cnSchema构建的工作流文档流转协议知识图谱，将文档中的概念、实体和关系转换为结构化知识表示。

## 核心实体

### 1. 工作流文档 (WorkflowDocument)
- **类型**: DigitalDocument
- **描述**: Agent之间协作的状态控制机制文档
- **属性**:
  - hasStatus: 工作流状态
  - hasCurrentOwner: 当前负责人
  - hasPreviousOwner: 上一个负责人
  - hasTask: 包含的任务
  - hasNextAction: 下一步动作
  - hasTerminationCondition: 终止条件

### 2. Agent (参与者)
- **类型**: Person
- **描述**: 工作流参与者
- **示例**: 张三、李四、程序员、测试员

### 3. 工作流状态 (WorkflowStatus)
- **类型**: ActionStatusType
- **状态值**:
  - StatusPending (待处理)
  - StatusInProgress (进行中)
  - StatusCompleted (已完成)
  - StatusTerminated (已终止)

### 4. 任务 (Task)
- **类型**: Action
- **描述**: 工作流中需要完成的具体任务
- **示例**: 计算2+2等于几、测试calculator.py中的add函数

### 5. 工作流动作 (WorkflowAction)
- **类型**: Action
- **动作类型**:
  - AcceptAction (接受任务)
  - CompleteAction (完成任务)
  - TransferAction (转交任务)
  - TerminateAction (终止工作流)

## 关系定义

### 核心关系
1. **hasStatus**: 工作流文档 → 工作流状态
2. **hasCurrentOwner**: 工作流文档 → Agent
3. **hasPreviousOwner**: 工作流文档 → Agent
4. **hasTask**: 工作流文档 → 任务
5. **performsAction**: Agent → 工作流动作
6. **causesStatusChange**: 工作流动作 → 工作流状态

## 状态转换规则

### 状态转换映射
```
pending → in_progress: Agent接受任务 (AcceptAction)
in_progress → completed: Agent完成任务 (CompleteAction)
in_progress → pending: Agent转交给其他Agent (TransferAction)
任何状态 → terminated: 达到终止条件 (TerminateAction)
```

## 实例数据

### 示例工作流1: calc_2plus2_001
- **状态**: pending
- **当前负责人**: 李四
- **上一个负责人**: 张三
- **任务**: 计算2+2等于几
- **下一步动作**: 李四需要计算并回复结果

### 示例工作流2: code_test_001
- **状态**: in_progress
- **当前负责人**: 测试员
- **上一个负责人**: 程序员
- **任务**: 测试calculator.py中的add函数
- **历史动作**: 创建工作流、接受任务、完成编码、转交给测试员

## 知识图谱文件

1. **workflow_knowledge_graph.jsonld** - 模式定义
   - 包含类、属性和关系的定义
   - 基于cnSchema的扩展

2. **workflow_knowledge_graph_instances.jsonld** - 实例数据
   - 包含具体的工作流实例
   - 包含Agent、任务和动作的实例

## 应用价值

1. **语义理解**: 为工作流文档提供结构化语义表示
2. **智能查询**: 支持基于语义的查询和推理
3. **系统集成**: 便于与其他知识图谱系统集成
4. **自动化处理**: 支持工作流的自动化状态管理

## 技术特点

- **标准化**: 基于JSON-LD和RDF标准
- **可扩展**: 支持添加新的工作流类型和属性
- **语义丰富**: 使用cnSchema提供丰富的语义标注
- **机器可读**: 支持自动化处理和推理