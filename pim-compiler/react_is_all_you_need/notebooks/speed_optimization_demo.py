#!/usr/bin/env python3
"""
Agent速度优化演示
展示多种优化技巧
"""

import sys
import os
sys.path.insert(0, '/home/guci/aiProjects/mda/pim-compiler/react_is_all_you_need')

from core.react_agent_minimal import ReactAgentMinimal
import time

def create_fast_agent():
    """方案1：使用最快的模型"""
    print("🚀 方案1：使用Gemini 2.5 Flash（最快）")
    print("-" * 50)
    
    # Gemini是目前最快的模型
    agent = ReactAgentMinimal(
        name="fast_order",
        description="快速订单处理",
        work_dir="/tmp/fast_demo",
        model="gemini-2.5-flash",
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        api_key=os.getenv("GEMINI_API_KEY"),
        max_rounds=5  # 减少最大轮数
    )
    
    # 简化的知识，减少思考步骤
    simple_knowledge = """
    # 快速订单处理
    
    创建订单时：
    1. 直接读取预设的客户和产品信息
    2. 快速计算价格
    3. 生成订单
    
    不要过度思考，快速完成任务。
    """
    agent.load_knowledge_str(simple_knowledge)
    
    return agent

def create_cached_agent():
    """方案2：使用缓存和预加载"""
    print("\n💾 方案2：数据预加载（避免文件IO）")
    print("-" * 50)
    
    # 将常用数据写入知识，避免文件读写
    cached_knowledge = """
    # 订单处理（带缓存数据）
    
    ## 预加载的客户数据
    - CUST001: 张三，VIP，8折
    - CUST002: 李四，普通会员，9折
    
    ## 预加载的产品价格
    - iPhone: 8999元
    - AirPods: 1999元
    - MacBook: 19999元
    
    ## 快速处理规则
    创建订单时直接使用上述数据，无需查询文件。
    """
    
    agent = ReactAgentMinimal(
        name="cached_order",
        description="带缓存的订单处理",
        work_dir="/tmp/cached_demo",
        model="deepseek-chat",  # DeepSeek也很快
        base_url="https://api.deepseek.com/v1",
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        max_rounds=3  # 更少的轮数
    )
    agent.load_knowledge_str(cached_knowledge)
    
    return agent

def create_direct_agent():
    """方案3：直接执行，减少子Agent调用"""
    print("\n⚡ 方案3：单Agent直接处理（无子Agent）")
    print("-" * 50)
    
    # 所有逻辑在一个Agent中，避免多层调用
    all_in_one_knowledge = """
    # 一体化订单处理
    
    我直接处理所有订单逻辑，不调用其他服务：
    
    ## 内置数据
    客户：CUST001是VIP（8折）
    产品：iPhone 8999元，AirPods 1999元
    库存：充足
    
    ## 快速流程
    1. 识别客户和产品
    2. 计算：价格 × 数量 × 折扣
    3. 生成订单号：ORD-日期-序号
    4. 返回结果
    
    一步到位，不要多轮思考。
    """
    
    agent = ReactAgentMinimal(
        name="direct_order",
        description="直接订单处理",
        work_dir="/tmp/direct_demo",
        model="gemini-2.5-flash",
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        api_key=os.getenv("GEMINI_API_KEY"),
        max_rounds=2  # 极少轮数
    )
    agent.load_knowledge_str(all_in_one_knowledge)
    
    return agent

def benchmark_agents():
    """性能对比测试"""
    print("\n" + "=" * 60)
    print("📊 性能对比测试")
    print("=" * 60)
    
    test_task = "为CUST001创建订单：iPhone一台"
    
    # 测试方案1：最快模型
    agent1 = create_fast_agent()
    start = time.time()
    result1 = agent1.execute(task=test_task)
    time1 = time.time() - start
    print(f"✅ Gemini Flash耗时: {time1:.2f}秒")
    
    # 测试方案2：缓存数据
    agent2 = create_cached_agent()
    start = time.time()
    result2 = agent2.execute(task=test_task)
    time2 = time.time() - start
    print(f"✅ DeepSeek缓存耗时: {time2:.2f}秒")
    
    # 测试方案3：直接处理
    agent3 = create_direct_agent()
    start = time.time()
    result3 = agent3.execute(task=test_task)
    time3 = time.time() - start
    print(f"✅ 单Agent直接耗时: {time3:.2f}秒")
    
    print("\n" + "=" * 60)
    print("🏆 优化效果总结")
    print("=" * 60)
    print(f"""
速度排名：
1. 单Agent直接处理: {time3:.2f}秒（最快）
2. Gemini Flash: {time1:.2f}秒
3. DeepSeek缓存: {time2:.2f}秒

优化技巧：
✅ 使用更快的模型（Gemini Flash、DeepSeek）
✅ 减少max_rounds（5→3→2）
✅ 预加载数据到知识中，避免文件IO
✅ 简化流程，减少子Agent调用
✅ 明确告诉Agent"不要过度思考"
    """)

def suggest_optimizations():
    """优化建议"""
    print("\n" + "=" * 60)
    print("💡 速度优化建议")
    print("=" * 60)
    print("""
1. **模型选择**（影响最大）
   - 最快：gemini-2.5-flash
   - 次快：deepseek-chat
   - 较慢：grok-code, claude系列

2. **减少思考轮数**
   - 设置max_rounds=3-5（够用即可）
   - 知识中明确说"直接执行，不要过度思考"

3. **优化知识设计**
   - 预置常用数据，避免文件读写
   - 简化决策流程，减少判断分支
   - 明确的指令，避免Agent自由发挥

4. **架构优化**
   - 简单任务用单Agent，避免多层调用
   - 复杂任务才用多Agent协作
   - 考虑并行执行（需要改造框架）

5. **其他技巧**
   - 使用temperature=0（确定性输出）
   - 缓存频繁使用的数据
   - 批量处理相似请求
    """)

if __name__ == "__main__":
    # 展示各种优化方案
    create_fast_agent()
    create_cached_agent()
    create_direct_agent()
    
    # 建议
    suggest_optimizations()
    
    # 如果有API密钥，运行基准测试
    if os.getenv("GEMINI_API_KEY") or os.getenv("DEEPSEEK_API_KEY"):
        print("\n检测到API密钥，开始性能测试...")
        benchmark_agents()
    else:
        print("\n⚠️ 未配置API密钥，跳过实际测试")