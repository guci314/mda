"""PIM Compiler CLI main entry point"""

import sys
import argparse
import logging
from pathlib import Path
from typing import List
import yaml
import json

from compiler.core.compiler_config import CompilerConfig
from compiler.transformers.deepseek_compiler import DeepSeekCompiler


def setup_logging(verbose: bool = False, debug: bool = False):
    """设置日志"""
    level = logging.WARNING
    if debug:
        level = logging.DEBUG
    elif verbose:
        level = logging.INFO
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def create_parser() -> argparse.ArgumentParser:
    """创建命令行解析器"""
    parser = argparse.ArgumentParser(
        prog='pimc',
        description='PIM Compiler - 将平台无关模型(PIM)编译为平台特定模型(PSM)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  pimc compile user_management.pim
  pimc compile models/*.pim --platform spring
  pimc generate user_management.pim --platform fastapi --code-output ./generated
  pimc validate user_management.pim
  pimc list-platforms
        """
    )
    
    parser.add_argument('--version', action='version', version='%(prog)s 1.0.0')
    
    # 全局选项
    parser.add_argument('-v', '--verbose', action='store_true', help='显示详细信息')
    parser.add_argument('-d', '--debug', action='store_true', help='显示调试信息')
    parser.add_argument('--config', type=Path, help='配置文件路径')
    
    # 子命令
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # compile 命令
    compile_parser = subparsers.add_parser('compile', help='编译PIM文件到PSM')
    compile_parser.add_argument('files', nargs='+', type=Path, help='要编译的PIM文件')
    compile_parser.add_argument('-o', '--output', type=Path, help='输出目录（默认: $PIM_HOME/classpath/models）')
    compile_parser.add_argument('-p', '--platform', default='fastapi', 
                              choices=['fastapi', 'spring', 'django', 'flask'],
                              help='目标平台（默认: fastapi）')
    compile_parser.add_argument('--no-cache', action='store_true', help='禁用缓存')
    compile_parser.add_argument('--no-validation', action='store_true', help='跳过验证')
    compile_parser.add_argument('--save-ir', action='store_true', help='保存中间表示')
    compile_parser.add_argument('--generate-code', action='store_true', help='生成代码（不仅仅是PSM）')
    compile_parser.add_argument('--no-lint', action='store_true', help='跳过lint检查')
    compile_parser.add_argument('--no-tests', action='store_true', help='不生成单元测试')
    compile_parser.add_argument('--no-run-tests', action='store_true', help='不运行生成的测试')
    
    # generate 命令
    generate_parser = subparsers.add_parser('generate', help='从PIM生成代码')
    generate_parser.add_argument('files', nargs='+', type=Path, help='要处理的PIM文件')
    generate_parser.add_argument('-p', '--platform', default='fastapi',
                               choices=['fastapi', 'spring', 'django', 'flask'],
                               help='目标平台（默认: fastapi）')
    generate_parser.add_argument('--code-output', type=Path, required=True, help='代码输出目录')
    generate_parser.add_argument('--psm-output', type=Path, help='PSM输出目录')
    
    # validate 命令
    validate_parser = subparsers.add_parser('validate', help='验证PIM文件')
    validate_parser.add_argument('files', nargs='+', type=Path, help='要验证的PIM文件')
    
    # list-platforms 命令
    list_parser = subparsers.add_parser('list-platforms', help='列出支持的平台')
    
    # clean 命令
    clean_parser = subparsers.add_parser('clean', help='清理缓存')
    clean_parser.add_argument('--all', action='store_true', help='清理所有缓存')
    
    return parser


def compile_files(files: List[Path], config: CompilerConfig) -> int:
    """编译文件"""
    compiler = DeepSeekCompiler(config)
    
    success_count = 0
    failed_files = []
    
    for file_path in files:
        if not file_path.exists():
            logging.error(f"文件不存在: {file_path}")
            failed_files.append(str(file_path))
            continue
        
        print(f"编译: {file_path}")
        result = compiler.compile(file_path)
        
        if result.success:
            print(f"  ✓ 成功 -> {result.psm_file}")
            success_count += 1
        else:
            print(f"  ✗ 失败")
            for error in result.errors:
                print(f"    - {error}")
            failed_files.append(str(file_path))
    
    # 打印摘要
    print(f"\n编译完成: {success_count}/{len(files)} 成功")
    if failed_files:
        print(f"失败文件:")
        for f in failed_files:
            print(f"  - {f}")
        return 1
    
    return 0


def generate_code(files: List[Path], config: CompilerConfig) -> int:
    """生成代码"""
    # 确保生成代码选项已启用
    config.generate_code = True
    
    compiler = DeepSeekCompiler(config)
    
    for file_path in files:
        if not file_path.exists():
            logging.error(f"文件不存在: {file_path}")
            continue
        
        print(f"处理: {file_path}")
        result = compiler.compile(file_path)
        
        if result.success:
            print(f"  ✓ PSM: {result.psm_file}")
            code_files = result.metadata.get("code_files", [])
            if code_files:
                print(f"  ✓ 代码文件:")
                for cf in code_files:
                    print(f"    - {cf}")
            else:
                print(f"  ! 未生成代码文件")
        else:
            print(f"  ✗ 失败")
            for error in result.errors:
                print(f"    - {error}")
    
    return 0


def validate_files(files: List[Path]) -> int:
    """验证文件"""
    from ..models.pim_model import PIMModel
    
    all_valid = True
    
    for file_path in files:
        if not file_path.exists():
            print(f"✗ {file_path}: 文件不存在")
            all_valid = False
            continue
        
        print(f"验证: {file_path}")
        
        try:
            # TODO: 实现完整的PIM加载逻辑
            # 这里简化处理
            if file_path.suffix in ['.yaml', '.yml']:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    # 简单检查必要字段
                    required = ['domain', 'version', 'entities', 'services']
                    missing = [f for f in required if f not in data]
                    if missing:
                        print(f"  ✗ 缺少必要字段: {', '.join(missing)}")
                        all_valid = False
                    else:
                        print(f"  ✓ 格式正确")
            else:
                print(f"  ! 暂不支持验证 {file_path.suffix} 格式")
                
        except Exception as e:
            print(f"  ✗ 验证失败: {e}")
            all_valid = False
    
    return 0 if all_valid else 1


def list_platforms():
    """列出支持的平台"""
    platforms = {
        "fastapi": {
            "name": "FastAPI",
            "description": "Python异步Web框架",
            "features": ["异步支持", "自动API文档", "类型验证", "高性能"]
        },
        "spring": {
            "name": "Spring Boot",
            "description": "Java企业级框架",
            "features": ["Spring生态", "JPA", "安全框架", "微服务"]
        },
        "django": {
            "name": "Django",
            "description": "Python全栈Web框架",
            "features": ["ORM", "Admin界面", "认证系统", "模板引擎"]
        },
        "flask": {
            "name": "Flask",
            "description": "Python轻量级Web框架",
            "features": ["简单灵活", "扩展丰富", "RESTful", "微服务"]
        }
    }
    
    print("支持的目标平台:\n")
    for key, info in platforms.items():
        print(f"{key:10} - {info['name']}")
        print(f"{'':10}   {info['description']}")
        print(f"{'':10}   特性: {', '.join(info['features'])}")
        print()


def clean_cache(all_cache: bool = False):
    """清理缓存"""
    cache_dir = Path(".pim_cache")
    
    if not cache_dir.exists():
        print("没有找到缓存目录")
        return
    
    if all_cache:
        # 清理所有缓存
        import shutil
        shutil.rmtree(cache_dir)
        print("已清理所有缓存")
    else:
        # 只清理编译缓存
        compiler_cache = cache_dir / "compiler_cache.json"
        if compiler_cache.exists():
            compiler_cache.unlink()
            print("已清理编译缓存")
        else:
            print("没有找到编译缓存")


def load_config(args) -> CompilerConfig:
    """加载配置"""
    if args.config and args.config.exists():
        # 从文件加载配置
        with open(args.config, 'r') as f:
            if args.config.suffix == '.yaml':
                config_data = yaml.safe_load(f)
            else:
                config_data = json.load(f)
        config = CompilerConfig.from_dict(config_data)
    else:
        # 从环境变量加载配置
        config = CompilerConfig.from_env()
    
    # 应用命令行参数
    if hasattr(args, 'platform'):
        config.target_platform = args.platform
    if hasattr(args, 'output'):
        if args.output:
            config.output_dir = args.output
    if hasattr(args, 'no_cache') and args.no_cache:
        config.enable_cache = False
    if hasattr(args, 'no_validation') and args.no_validation:
        config.enable_validation = False
    if hasattr(args, 'save_ir') and args.save_ir:
        config.save_intermediate = True
    if hasattr(args, 'code_output'):
        if args.code_output:
            config.output_dir = args.code_output
            config.generate_code = True
    
    # 处理新的命令行选项
    if hasattr(args, 'generate_code') and args.generate_code:
        config.generate_code = True
    if hasattr(args, 'no_lint') and args.no_lint:
        config.enable_lint = False
    if hasattr(args, 'no_tests') and args.no_tests:
        config.enable_unit_tests = False
    if hasattr(args, 'no_run_tests') and args.no_run_tests:
        config.run_tests = False
    
    # 设置调试选项
    config.verbose = args.verbose
    config.debug = args.debug
    
    return config


def main(argv=None):
    """主函数"""
    parser = create_parser()
    args = parser.parse_args(argv)
    
    # 设置日志
    setup_logging(args.verbose, args.debug)
    
    # 执行命令
    if args.command == 'compile':
        config = load_config(args)
        
        # 验证配置
        errors = config.validate()
        if errors:
            print("配置错误:")
            for error in errors:
                print(f"  - {error}")
            return 1
        
        return compile_files(args.files, config)
    
    elif args.command == 'generate':
        config = load_config(args)
        config.generate_code = True
        
        # 设置代码输出目录
        if args.code_output:
            # 代码生成到指定目录
            # PSM仍然输出到classpath
            pass
        
        errors = config.validate()
        if errors:
            print("配置错误:")
            for error in errors:
                print(f"  - {error}")
            return 1
        
        return generate_code(args.files, config)
    
    elif args.command == 'validate':
        return validate_files(args.files)
    
    elif args.command == 'list-platforms':
        list_platforms()
        return 0
    
    elif args.command == 'clean':
        clean_cache(args.all)
        return 0
    
    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main())