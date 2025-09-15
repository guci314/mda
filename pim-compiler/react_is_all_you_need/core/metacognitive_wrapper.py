#!/usr/bin/env python3
"""
元认知包装器 - 透明包装模式实现
让包装后的Agent保持与原Agent完全相同的接口
"""

from pathlib import Path
import sys
import json

# 添加项目路径
project_root = Path("/home/guci/aiProjects/mda/pim-compiler/react_is_all_you_need")
sys.path.insert(0, str(project_root))

from core.react_agent_minimal import ReactAgentMinimal
from core.tools.create_agent_tool import CreateAgentTool


class MetacognitiveWrapper:
    """
    元认知包装器 - 对Agent进行透明包装
    包装后的对象与原Agent接口完全一致
    """
    
    def __init__(self, target_agent, builder_model="x-ai/grok-code-fast-1"):
        """
        初始化元认知包装器
        
        Args:
            target_agent: 要包装的目标Agent实例
            builder_model: Builder使用的模型
        """
        self.target_agent = target_agent
        self.builder_model = builder_model
        
        # 创建元认知Builder
        self.builder = self._create_builder()
        
        # 从模板创建实际执行的Agent
        self.execution_agent = self._create_execution_agent()
        
    def _create_builder(self):
        """创建元认知Builder"""
        import os
        builder = ReactAgentMinimal(
            work_dir=self.target_agent.work_dir,
            model=self.builder_model,
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY"),
            knowledge_files=[
                f"{project_root}/knowledge/minimal/system/execution_context_guide.md",
                f"{project_root}/knowledge/minimal/system/system_prompt_minimal.md",
                f"{project_root}/knowledge/agent_builder_knowledge.md"
            ],
            max_rounds=30,
            name="metacognitive_builder"
        )
        
        # 添加创建Agent的工具
        create_tool = CreateAgentTool(
            work_dir=self.target_agent.work_dir,
            parent_agent=builder
        )
        builder.add_function(create_tool)
        
        return builder
    
    def _create_execution_agent(self):
        """从模板创建执行Agent"""
        # 获取目标Agent的模板
        template = self.target_agent.get_template()
        
        # 构造创建任务
        create_task = f"""
根据以下模板创建Agent：
```json
{json.dumps(template, indent=2, ensure_ascii=False)}
```

严格按照模板参数创建Agent，返回创建的Agent名称。
"""
        
        # 让Builder创建Agent
        result = self.builder.execute(task=create_task)
        
        # 从结果中提取Agent名称
        if "名称：" in result:
            agent_name = result.split("名称：")[1].split("\n")[0].strip()
            
            # 从Builder的工具列表中找到创建的Agent
            for tool in self.builder.function_instances:
                if tool.name == agent_name:
                    return tool
        
        # 如果创建失败，返回原Agent
        print("⚠️ 元认知包装失败，使用原Agent")
        return self.target_agent
    
    def execute(self, task=None, **kwargs):
        """
        执行任务 - 透明代理到包装后的Agent
        保持与ReactAgentMinimal完全相同的接口
        
        Args:
            task: 要执行的任务
            **kwargs: 其他参数
        
        Returns:
            执行结果
        """
        # 构造元认知监督任务
        supervised_task = f"""
## 元认知监督任务

### 原始任务
{task}

### 执行要求
1. 使用创建的Agent执行任务
2. 检查output.log分析执行过程
3. 验证结果正确性
4. 如发现问题，修正并重试
5. 返回最终执行结果
"""
        
        # 通过Builder监督执行
        result = self.builder.execute(task=supervised_task)
        return result
    
    def __call__(self, task=None, **kwargs):
        """支持函数调用方式"""
        return self.execute(task=task, **kwargs)
    
    def __getattr__(self, name):
        """
        透明代理所有其他方法到目标Agent
        使包装器完全透明
        """
        return getattr(self.execution_agent, name)


def metacognitive_wrap(agent, builder_model="x-ai/grok-code-fast-1"):
    """
    便捷函数 - 对Agent进行元认知包装
    
    Args:
        agent: 要包装的Agent实例
        builder_model: Builder使用的模型
    
    Returns:
        包装后的Agent（接口完全透明）
    
    Example:
        # 创建原始Agent
        agent = ReactAgentMinimal(...)
        
        # 元认知包装（透明）
        wrapped = metacognitive_wrap(agent)
        
        # 使用方式完全相同！
        result = wrapped.execute(task="处理数据")
    """
    return MetacognitiveWrapper(agent, builder_model)


def demo_transparent_wrapper():
    """演示透明包装器模式"""
    print("🎭 演示透明元认知包装器\n")
    print("="*60)
    
    # 1. 创建原始Agent
    print("\n1️⃣ 创建原始Agent")
    import os
    original_agent = ReactAgentMinimal(
        work_dir="/tmp/test",
        model="deepseek-chat",
        base_url="https://api.deepseek.com/v1",
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        knowledge_files=[
            f"{project_root}/knowledge/minimal/system/execution_context_guide.md",
            f"{project_root}/knowledge/minimal/system/system_prompt_minimal.md"
        ],
        max_rounds=10,
        name="calculator_agent",
        description="计算器Agent"
    )
    print(f"   ✅ 原始Agent: {original_agent.name}")
    
    # 2. 元认知包装（透明）
    print("\n2️⃣ 元认知包装")
    wrapped_agent = metacognitive_wrap(original_agent)
    print("   ✅ 包装完成")
    
    # 3. 使用方式完全相同！
    print("\n3️⃣ 透明调用测试")
    print("   📝 原始调用: original_agent.execute(task='...')")
    print("   📝 包装调用: wrapped_agent.execute(task='...')  # 完全相同！")
    
    # 准备测试数据
    test_csv = """col1,col2,col3
1,2,3
,4,5
6,,7
8,9,"""
    
    with open("/tmp/test/test_data.csv", "w") as f:
        f.write(test_csv)
    
    # 4. 执行任务（接口完全透明）
    print("\n4️⃣ 执行任务")
    result = wrapped_agent.execute(
        task="处理/tmp/test/test_data.csv文件，计算每列的和。注意：文件包含缺失值。"
    )
    
    print("\n5️⃣ 执行结果")
    print("-"*40)
    print(result[:500] if len(result) > 500 else result)
    
    print("\n="*60)
    print("✅ 透明包装器验证完成")
    print("\n关键特性：")
    print("• wrapped = metacognitive_wrap(agent)")
    print("• wrapped.execute(task='...') # 接口完全相同")
    print("• 下游程序员无需修改任何代码")
    print("• 自动获得元认知监督能力")


if __name__ == "__main__":
    # 加载环境变量
    from dotenv import load_dotenv
    env_path = Path("/home/guci/aiProjects/mda/pim-compiler/.env")
    if env_path.exists():
        load_dotenv(env_path)
        print(f"  ✅ 已加载环境变量: {env_path}")
    
    demo_transparent_wrapper()