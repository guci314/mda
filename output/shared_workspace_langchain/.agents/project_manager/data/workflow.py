def coordinate_agents_workflow():
    """协调多个 Agent 完成任务"""
    # STEP: generate_code
    # TOOL_CALL: code_generator
    # 任务：创建 MathUtils 类
    result1 = default_api.code_generator(task="在 /home/guci/aiProjects/mda/output/shared_workspace_langchain/math_utils.py 创建 MathUtils 类，包含 add, subtract, multiply, divide, power 方法")
    print(result1)
    # STEP: run_tests  
    # TOOL_CALL: code_runner
    # 任务：运行测试验证代码
    result2 = default_api.code_runner(task="运行测试验证 /home/guci/aiProjects/mda/output/shared_workspace_langchain/math_utils.py 中所有方法工作正常")
    print(result2)
    # STEP: review_code
    # TOOL_CALL: code_reviewer
    # 任务：审查代码质量并打分（1-10分）
    result3 = default_api.code_reviewer(task="审查 /home/guci/aiProjects/mda/output/shared_workspace_langchain/math_utils.py 的代码质量并打分（1-10分），请遵循\"简洁输出加文档引用原则\"")
    print(result3)
    return result1, result2, result3