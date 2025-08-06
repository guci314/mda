# 自然语言分层编译器

基于"条件反射 vs 探索"的二分法，实现自然语言任务的分层编译机制。

## 核心思想

1. **可编译性的本质**：不是"是否存在映射"，而是"决策树是否小到可以实际编译"
2. **分层编译**：同一任务在不同抽象层次有不同的可编译性
3. **渐进式降级**：从高层的条件反射逐步降级到底层的探索

## 架构组件

### 1. IR类型定义 (`ir_types.py`)
- `LayeredIR`: 分层中间表示
- `Layer`: 单个抽象层次
- `ExecutionResult`: 执行结果

### 2. 层次分类器 (`layer_classifier.py`)
- 识别任务类型
- 分解任务为抽象层次
- 估算每层的决策树大小

### 3. 分层编译器 (`hierarchical_compiler.py`)
- 判断每层是否可编译
- 生成Python代码（编译层）
- 保留任务描述（探索层）

### 4. 分层执行器 (`hierarchical_executor.py`)
- 执行编译的Python代码
- 调用ReAct代理处理探索任务
- 优化LLM调用

## 使用示例

```python
from compiler import HierarchicalCompiler, HierarchicalExecutor

# 创建编译器
compiler = HierarchicalCompiler()

# 编译任务
task = "创建一个RESTful API用于管理博客文章"
ir = compiler.compile(task)

# 查看编译结果
print(f"总层数: {len(ir.layers)}")
print(f"编译层数: {len(ir.get_compiled_layers())}")

# 执行
executor = HierarchicalExecutor()
result = executor.execute(ir)
```

## 运行演示

```bash
python demo.py
```

演示程序会展示不同类型任务的编译效果：
- 简单任务：完全编译
- API创建：分层编译
- 性能优化：顶层编译
- 调试任务：主要探索

## 关键洞察

1. **决策树规模决定可编译性**
   - 小决策树（<100）：完全可编译
   - 中等决策树（<100K）：部分可编译
   - 大决策树（>1M）：只能编译顶层
   - 天文数字：完全依赖探索

2. **专家知识是"编译"的结果**
   - 架构师的模式识别
   - 医生的诊断决策
   - 程序员的调试直觉

3. **分层执行的优势**
   - 最大化确定性执行
   - 最小化LLM调用
   - 保持必要的灵活性

## 未来扩展

1. **更智能的代码生成**：集成真实的代码生成器
2. **学习机制**：从执行结果中学习新的编译模式
3. **并行执行**：支持多层并行执行
4. **可视化**：展示编译和执行过程