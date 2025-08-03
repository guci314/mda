"""调试器可视化扩展

将 Agent 执行流程导出为可视化格式（如 Mermaid 图）。
"""

from typing import List, Dict, Any
from datetime import datetime
from react_agent_debugger import ExecutionStep, StepType


class DebugVisualizer:
    """将调试历史转换为可视化格式"""
    
    @staticmethod
    def to_mermaid(execution_history: List[ExecutionStep]) -> str:
        """将执行历史转换为 Mermaid 流程图
        
        Args:
            execution_history: 执行步骤列表
            
        Returns:
            Mermaid 格式的流程图代码
        """
        lines = ["graph TD"]
        
        # 添加开始节点
        lines.append("    Start[开始执行]")
        
        # 转换每个步骤
        prev_id = "Start"
        for i, step in enumerate(execution_history):
            step_id = f"Step{i}"
            
            # 根据步骤类型选择节点样式
            if step.step_type == StepType.THINK:
                # 思考步骤用圆角矩形
                label = f"🤔 思考 #{i+1}"
                lines.append(f"    {step_id}[{label}]")
            elif step.step_type == StepType.ACT:
                # 行动步骤用菱形
                label = f"🔧 行动 #{i+1}"
                lines.append(f"    {step_id}{{{label}}}")
            else:  # OBSERVE
                # 观察步骤用圆形
                label = f"👁️ 观察 #{i+1}"
                lines.append(f"    {step_id}(({label}))")
            
            # 添加连接线
            lines.append(f"    {prev_id} --> {step_id}")
            prev_id = step_id
        
        # 添加结束节点
        lines.append(f"    {prev_id} --> End[执行完成]")
        
        # 添加样式
        lines.extend([
            "",
            "    %% 样式定义",
            "    classDef thinkStyle fill:#e1f5fe,stroke:#01579b,stroke-width:2px;",
            "    classDef actStyle fill:#fff3e0,stroke:#e65100,stroke-width:2px;", 
            "    classDef observeStyle fill:#f3e5f5,stroke:#4a148c,stroke-width:2px;",
            ""
        ])
        
        # 应用样式
        for i, step in enumerate(execution_history):
            step_id = f"Step{i}"
            if step.step_type == StepType.THINK:
                lines.append(f"    class {step_id} thinkStyle;")
            elif step.step_type == StepType.ACT:
                lines.append(f"    class {step_id} actStyle;")
            else:
                lines.append(f"    class {step_id} observeStyle;")
        
        return "\n".join(lines)
    
    @staticmethod
    def to_sequence_diagram(execution_history: List[ExecutionStep]) -> str:
        """将执行历史转换为时序图
        
        Args:
            execution_history: 执行步骤列表
            
        Returns:
            Mermaid 格式的时序图代码
        """
        lines = ["sequenceDiagram"]
        lines.append("    participant User")
        lines.append("    participant Agent") 
        lines.append("    participant Tools")
        
        for i, step in enumerate(execution_history):
            if step.step_type == StepType.THINK:
                lines.append(f"    Agent->>Agent: 思考 #{i+1}")
            elif step.step_type == StepType.ACT:
                lines.append(f"    Agent->>Tools: 调用工具 #{i+1}")
            else:  # OBSERVE
                lines.append(f"    Tools->>Agent: 返回结果 #{i+1}")
        
        return "\n".join(lines)
    
    @staticmethod
    def generate_report(execution_history: List[ExecutionStep], 
                       output_file: str = "debug_report.md") -> str:
        """生成调试报告
        
        Args:
            execution_history: 执行步骤列表
            output_file: 输出文件名
            
        Returns:
            报告内容
        """
        # 统计信息
        step_counts = {}
        for step in execution_history:
            step_type = step.step_type.value
            step_counts[step_type] = step_counts.get(step_type, 0) + 1
        
        # 计算执行时间
        if execution_history:
            start_time = execution_history[0].timestamp
            end_time = execution_history[-1].timestamp
            duration = (end_time - start_time).total_seconds()
        else:
            duration = 0
        
        # 生成报告
        report = f"""# Agent 执行调试报告

生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 执行统计

- 总步骤数：{len(execution_history)}
- 执行时长：{duration:.2f} 秒
- 步骤分布：
  - THINK（思考）：{step_counts.get('THINK', 0)} 次
  - ACT（行动）：{step_counts.get('ACT', 0)} 次
  - OBSERVE（观察）：{step_counts.get('OBSERVE', 0)} 次

## 执行流程图

```mermaid
{DebugVisualizer.to_mermaid(execution_history)}
```

## 时序图

```mermaid
{DebugVisualizer.to_sequence_diagram(execution_history)}
```

## 详细执行历史

| 序号 | 时间 | 步骤类型 | 深度 | 详情 |
|------|------|----------|------|------|
"""
        
        for i, step in enumerate(execution_history):
            time_str = step.timestamp.strftime('%H:%M:%S.%f')[:-3]
            details = str(step.data.get('content_preview', ''))[:50]
            if len(details) == 50:
                details += "..."
            report += f"| {i+1} | {time_str} | {step.step_type.value} | {step.depth} | {details} |\n"
        
        # 保存报告
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        return report


# 示例：如何在调试后生成可视化
if __name__ == "__main__":
    print("调试可视化器示例")
    print("在调试会话结束后，可以使用以下代码生成可视化报告：")
    print()
    print("```python")
    print("from debug_visualizer import DebugVisualizer")
    print()
    print("# 假设 debugger 是你的调试器实例")
    print("# 生成报告")
    print("report = DebugVisualizer.generate_report(")
    print("    debugger.execution_history,")
    print("    'my_debug_report.md'")
    print(")")
    print("print('报告已生成：my_debug_report.md')")
    print("```")