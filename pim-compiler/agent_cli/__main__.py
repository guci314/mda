#!/usr/bin/env python3
"""
Agent CLI v3 命令行入口 - 支持任务分类和自适应规划
支持直接运行: python -m agent_cli
"""
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 使用最新 v3 增强版架构
from .core_v3_enhanced import AgentCLI_V3_Enhanced
from .core_v2_improved import AgentCLI_V2_Improved
from .core import LLMConfig
from .setup import setup_provider, show_providers, show_prices


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        prog="agent_cli",
        description="Agent CLI v3 - 支持任务分类和自适应规划的智能 LLM Agent"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # setup 命令
    setup_parser = subparsers.add_parser("setup", help="配置 LLM 提供商")
    setup_parser.add_argument("--list", action="store_true", help="列出所有提供商")
    setup_parser.add_argument("--prices", action="store_true", help="显示价格对比")
    
    # test 命令
    test_parser = subparsers.add_parser("test", help="运行连接测试")
    test_parser.add_argument("--provider", help="指定提供商")
    
    # run 命令 - 执行任务
    run_parser = subparsers.add_parser("run", help="执行任务")
    run_parser.add_argument("task", help="要执行的任务描述")
    run_parser.add_argument("-p", "--provider", help="指定 LLM 提供商")
    run_parser.add_argument("-m", "--model", help="指定模型")
    run_parser.add_argument("-v", "--verbose", action="store_true", help="详细输出")
    run_parser.add_argument("--max-actions", type=int, default=10, help="每个步骤最大动作数")
    run_parser.add_argument("--no-dynamic", action="store_true", help="禁用动态计划调整")
    run_parser.add_argument("--use-v2", action="store_true", help="使用 v2 版本而不是 v3")
    run_parser.add_argument("--no-classification", action="store_true", help="禁用任务分类")
    run_parser.add_argument("--no-query-opt", action="store_true", help="禁用查询优化")
    
    # convert 命令 - PIM 到 PSM 转换
    convert_parser = subparsers.add_parser("convert", help="转换 PIM 到 PSM")
    convert_parser.add_argument("input", help="输入 PIM 文件路径")
    convert_parser.add_argument("-o", "--output", help="输出 PSM 文件路径")
    convert_parser.add_argument("-t", "--target", default="fastapi", 
                              choices=["fastapi", "django", "flask"],
                              help="目标平台")
    convert_parser.add_argument("-p", "--provider", help="指定 LLM 提供商")
    
    # providers 命令 - 显示提供商信息
    providers_parser = subparsers.add_parser("providers", help="显示提供商信息")
    providers_parser.add_argument("--prices", action="store_true", help="显示价格")
    
    args = parser.parse_args()
    
    if args.command == "setup":
        if args.list:
            show_providers()
        elif args.prices:
            show_prices()
        else:
            setup_provider()
    
    elif args.command == "test":
        # 测试连接
        try:
            if args.provider:
                config = LLMConfig.from_env(args.provider)
            else:
                config = LLMConfig.from_env()
            
            print(f"测试 {config.provider} 连接...")
            print(f"模型: {config.model}")
            
            from .setup import test_llm_connection
            if test_llm_connection(config):
                print("✅ 测试成功！")
            else:
                print("❌ 测试失败！")
                sys.exit(1)
                
        except Exception as e:
            print(f"❌ 错误: {str(e)}")
            sys.exit(1)
    
    elif args.command == "run":
        # 执行任务
        try:
            # 创建配置
            if args.provider or args.model:
                config = LLMConfig.from_env(args.provider)
                if args.model:
                    config.model = args.model
            else:
                config = LLMConfig.from_env()
            
            # 根据参数选择版本
            if args.use_v2:
                # 使用 v2 版本
                cli = AgentCLI_V2_Improved(
                    llm_config=config,
                    max_actions_per_step=args.max_actions,
                    enable_dynamic_planning=not args.no_dynamic
                )
                version_info = "v2.2 改进版 (增强动态执行架构)"
            else:
                # 使用 v3 版本（默认）
                cli = AgentCLI_V3_Enhanced(
                    llm_config=config,
                    max_actions_per_step=args.max_actions,
                    enable_dynamic_planning=not args.no_dynamic,
                    enable_task_classification=not args.no_classification,
                    enable_adaptive_planning=not args.no_classification,
                    enable_query_optimization=not args.no_query_opt
                )
                version_info = "v3.0 增强版 (智能任务分类+自适应规划)"
            
            print(f"使用 Agent CLI {version_info}")
            print(f"提供商: {config.provider}")
            print(f"模型: {config.model}")
            print(f"每步骤最大动作数: {args.max_actions}")
            print(f"动态计划: {'启用' if not args.no_dynamic else '禁用'}")
            
            if not args.use_v2:
                print(f"任务分类: {'启用' if not args.no_classification else '禁用'}")
                print(f"查询优化: {'启用' if not args.no_query_opt else '禁用'}")
            
            print("")
            
            # 执行任务
            success, message = cli.execute_task(args.task)
            
            if args.verbose and hasattr(cli, 'steps'):
                print(f"\n执行统计:")
                print(f"- 总步骤数: {len(cli.steps)}")
                total_actions = sum(len(step.actions) for step in cli.steps)
                print(f"- 总动作数: {total_actions}")
                
                # 显示每个步骤的动作数
                for i, step in enumerate(cli.steps, 1):
                    print(f"  步骤 {i} ({step.name}): {len(step.actions)} 个动作")
            
            if success:
                print(f"\n✅ {message}")
                sys.exit(0)
            else:
                print(f"\n❌ {message}")
                sys.exit(1)
                
        except Exception as e:
            print(f"❌ 错误: {str(e)}")
            import traceback
            if args.verbose:
                traceback.print_exc()
            sys.exit(1)
    
    elif args.command == "convert":
        # PIM 到 PSM 转换
        input_path = Path(args.input)
        if not input_path.exists():
            print(f"❌ 输入文件不存在: {input_path}")
            sys.exit(1)
        
        # 自动生成输出文件名
        if args.output:
            output_path = args.output
        else:
            output_path = input_path.stem + f"_{args.target}_psm.md"
        
        task = f"将 {input_path} 中的 PIM 转换为 {args.target} 平台的 PSM，输出到 {output_path}"
        
        try:
            # 创建 CLI (默认使用 v3)
            if args.provider:
                config = LLMConfig.from_env(args.provider)
            else:
                config = LLMConfig.from_env()
                
            cli = AgentCLI_V3_Enhanced(
                llm_config=config,
                enable_task_classification=True,
                enable_adaptive_planning=True,
                enable_query_optimization=True
            )
            
            print(f"开始转换: {input_path} -> {output_path}")
            print(f"目标平台: {args.target}")
            print(f"使用提供商: {config.provider}")
            print(f"使用模型: {config.model}")
            print(f"使用架构: Agent CLI v3.0 增强版 (智能任务分类)")
            
            success, message = cli.execute_task(task)
            
            if success:
                print(f"✅ 转换成功: {output_path}")
                
                # 检查输出文件
                if Path(output_path).exists():
                    size = Path(output_path).stat().st_size
                    print(f"文件大小: {size:,} 字节")
            else:
                print(f"❌ 转换失败: {message}")
                sys.exit(1)
                
        except Exception as e:
            print(f"❌ 错误: {str(e)}")
            sys.exit(1)
    
    elif args.command == "providers":
        if args.prices:
            show_prices()
        else:
            show_providers()
    
    else:
        # 没有指定命令，显示帮助
        parser.print_help()


if __name__ == "__main__":
    main()