#!/bin/bash

# 运行带软件工程知识的代码生成实验

echo "Starting code generation experiments with software engineering knowledge..."

# 创建输出目录
mkdir -p generated_code_with_knowledge

# 启动实验
echo "Launching experiments in background..."
nohup python code_gen_agent_with_knowledge.py > knowledge_experiment.out 2>&1 &
PID=$!

echo "Experiments started with PID: $PID"
echo "Monitor progress with:"
echo "  tail -f code_gen_*_knowledge_*.log"
echo "  ps -p $PID"

# 保存 PID
echo $PID > knowledge_experiment.pid