#!/usr/bin/env python3
"""
DeepSeek CLI 命令行入口
支持直接运行: python -m deepseek_cli
"""
import sys
import argparse
from pathlib import Path

from .core import DeepSeekCLI
from .setup import setup_deepseek
from .demo import main as run_demo


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        prog="deepseek_cli",
        description="DeepSeek CLI - Gemini CLI 的中国友好替代方案"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # setup 命令
    setup_parser = subparsers.add_parser("setup", help="配置 DeepSeek API")
    setup_parser.add_argument("--prices", action="store_true", help="显示价格信息")
    
    # demo 命令
    demo_parser = subparsers.add_parser("demo", help="运行功能演示")
    
    # test 命令
    test_parser = subparsers.add_parser("test", help="运行测试")
    
    # run 命令 - 执行任务
    run_parser = subparsers.add_parser("run", help="执行任务")
    run_parser.add_argument("task", help="要执行的任务描述")
    run_parser.add_argument("-o", "--output", help="输出文件路径")
    run_parser.add_argument("-v", "--verbose", action="store_true", help="详细输出")
    
    # convert 命令 - PIM 到 PSM 转换
    convert_parser = subparsers.add_parser("convert", help="转换 PIM 到 PSM")
    convert_parser.add_argument("input", help="输入 PIM 文件路径")
    convert_parser.add_argument("-o", "--output", help="输出 PSM 文件路径")
    convert_parser.add_argument("-p", "--platform", default="fastapi", 
                              choices=["fastapi", "django", "flask"],
                              help="目标平台")
    
    args = parser.parse_args()
    
    if args.command == "setup":
        if args.prices:
            from .setup import check_deepseek_prices
            check_deepseek_prices()
        else:
            setup_deepseek()
    
    elif args.command == "demo":
        run_demo()
    
    elif args.command == "test":
        from .test_cli import main as run_test
        run_test()
    
    elif args.command == "run":
        # 执行任务
        try:
            cli = DeepSeekCLI()
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
            output_path = input_path.stem + f"_{args.platform}_psm.md"
        
        task = f"将 {input_path} 中的 PIM 转换为 {args.platform} 平台的 PSM，输出到 {output_path}"
        
        try:
            cli = DeepSeekCLI()
            print(f"开始转换: {input_path} -> {output_path}")
            print(f"目标平台: {args.platform}")
            
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
    
    else:
        # 没有指定命令，显示帮助
        parser.print_help()


if __name__ == "__main__":
    main()