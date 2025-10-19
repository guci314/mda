#!/usr/bin/env python3
"""
可视化智能体记忆流转
使用graphviz生成图片（需要安装：pip install graphviz）
"""

try:
    from graphviz import Digraph

    # 创建有向图
    dot = Digraph(comment='智能体记忆流转')
    dot.attr(rankdir='TB')

    # 语义记忆子图
    with dot.subgraph(name='cluster_semantic') as s:
        s.attr(label='语义记忆', style='filled', color='lightgreen')
        s.node('K', 'knowledge.md\n长期语义\n我会什么', shape='box', style='filled', fillcolor='#90EE90')
        s.node('EC', 'ExecutionContext\n临时语义\n临时理解', shape='box', style='filled', fillcolor='#FFE4B5')

    # 情景记忆子图
    with dot.subgraph(name='cluster_episodic') as e:
        e.attr(label='情景记忆', style='filled', color='lightblue')
        e.node('LLM', 'LLM上下文窗口\n临时情景\n我在做什么', shape='box', style='filled', fillcolor='#87CEEB')
        e.node('OUT', 'output.log\n短期情景\n原始记录', shape='box', style='filled', fillcolor='#B0C4DE')
        e.node('CM', 'compact.md\n短期混合\n情景+语义', shape='box', style='filled', fillcolor='#DDA0DD')
        e.node('DOCS', 'docs/\n长期情景\n重要决策', shape='box', style='filled', fillcolor='#98FB98')

    # 演绎流程（实线）
    dot.edge('K', 'EC', label='演绎\n应用知识', color='blue')
    dot.edge('EC', 'LLM', label='演绎\n执行任务', color='blue')
    dot.edge('LLM', 'OUT', label='持久化', color='blue')
    dot.edge('OUT', 'CM', label='压缩', color='blue')

    # 归纳流程（虚线）
    dot.edge('LLM', 'CM', label='部分归纳\n/compact', style='dashed', color='green')
    dot.edge('CM', 'K', label='归纳\n@learning', style='dashed', color='green')
    dot.edge('DOCS', 'K', label='归纳\n提炼经验', style='dashed', color='green')

    # 重要决策
    dot.edge('LLM', 'DOCS', label='重要决策\n立即记录', style='bold', color='red')

    # 渲染
    output_file = 'memory_flow'
    dot.render(output_file, format='png', cleanup=True)
    print(f'✅ 图片已生成: {output_file}.png')

except ImportError:
    print('❌ 需要安装graphviz: pip install graphviz')
    print('   或者使用在线工具: https://mermaid.live/')
