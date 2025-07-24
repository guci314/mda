#!/usr/bin/env python3
"""
Agent CLI 命令行入口
支持直接运行: python -m agent_cli
"""
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

from .core import AgentCLI, LLMConfig
from .setup import setup_provider, show_providers, show_prices


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        prog="agent_cli",
        description="通用 LLM Agent CLI - 支持多种 AI 提供商"
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
                cli = AgentCLI(llm_config=config)
            else:
                cli = AgentCLI()
            
            # 执行任务
            success, message = cli.execute_task(args.task)
            
            if args.verbose:
                summary = cli.get_execution_summary()
                print(f"\n执行统计:")
                print(f"- 总动作数: {summary['total_actions']}")
                print(f"- 成功: {summary['successful_actions']}")
                print(f"- 失败: {summary['failed_actions']}")
            
            if success:
                print(f"✅ {message}")
                sys.exit(0)
            else:
                print(f"❌ {message}")
                sys.exit(1)
                
        except Exception as e:
            print(f"❌ 错误: {str(e)}")
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
            # 创建 CLI
            if args.provider:
                config = LLMConfig.from_env(args.provider)
                cli = AgentCLI(llm_config=config)
            else:
                cli = AgentCLI()
            
            print(f"开始转换: {input_path} -> {output_path}")
            print(f"目标平台: {args.target}")
            print(f"使用提供商: {cli.llm_config.provider}")
            print(f"使用模型: {cli.llm_config.model}")
            
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