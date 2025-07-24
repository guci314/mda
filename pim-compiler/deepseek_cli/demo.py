#!/usr/bin/env python3
"""
DeepSeek CLI 快速演示
展示主要功能和使用方法
"""
import os
import sys
import time
from pathlib import Path
from datetime import datetime

# 添加项目路径
sys.path.append(str(Path(__file__).parent.parent))

try:
    from deepseek_cli.core import DeepSeekCLI, DeepSeekLLM
except ImportError:
    print("❌ 错误：找不到 deepseek_cli 模块")
    print("请确保在正确的目录中")
    sys.exit(1)


def print_section(title):
    """打印分节标题"""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}\n")


def demo_basic_usage():
    """演示基本用法"""
    print_section("1. 基本用法演示")
    
    # 创建简单的 PIM
    pim_content = """# 图书管理系统 PIM

## 实体定义

### 图书 (Book)
- ISBN: 字符串，唯一标识
- 标题: 字符串，必填
- 作者: 字符串，必填
- 出版社: 字符串
- 出版日期: 日期
- 价格: 金额
- 库存: 整数

### 借阅记录 (Borrow)
- 记录ID: 唯一标识
- 图书: 引用图书
- 借阅人: 字符串
- 借阅日期: 日期
- 归还日期: 日期，可空
- 状态: 枚举[借出, 已还]

## 业务规则
1. 图书库存不能为负
2. 同一本书同一时间只能借给一个人
3. 借阅期限最长30天
"""
    
    # 保存 PIM
    pim_file = "demo_library_pim.md"
    with open(pim_file, "w", encoding="utf-8") as f:
        f.write(pim_content)
    print(f"✅ 创建演示 PIM: {pim_file}")
    
    # 检查 API Key
    if not os.getenv("DEEPSEEK_API_KEY"):
        print("\n❌ 未设置 DEEPSEEK_API_KEY")
        print("请运行: python setup_deepseek.py")
        return False
    
    print("\n开始转换 PIM 到 PSM...")
    print("-" * 40)
    
    try:
        # 创建 CLI 并执行
        cli = DeepSeekCLI()
        task = f"将 {pim_file} 转换为 FastAPI 平台的 PSM，输出到 demo_library_psm.md"
        
        start_time = time.time()
        success, message = cli.execute_task(task)
        duration = time.time() - start_time
        
        print(f"\n执行结果: {'✅ 成功' if success else '❌ 失败'}")
        print(f"执行时间: {duration:.2f} 秒")
        print(f"消息: {message}")
        
        # 显示执行统计
        summary = cli.get_execution_summary()
        print(f"\n执行统计:")
        print(f"- 总动作数: {summary['total_actions']}")
        print(f"- 成功: {summary['successful_actions']}")
        print(f"- 失败: {summary['failed_actions']}")
        
        return success
        
    except Exception as e:
        print(f"\n❌ 执行失败: {str(e)}")
        return False


def demo_task_planning():
    """演示任务规划功能"""
    print_section("2. 任务规划演示")
    
    if not os.getenv("DEEPSEEK_API_KEY"):
        print("跳过：需要 API Key")
        return
    
    try:
        llm = DeepSeekLLM()
        
        # 演示不同类型的任务规划
        tasks = [
            "创建一个用户认证系统",
            "优化数据库查询性能",
            "将单体应用拆分为微服务"
        ]
        
        for task in tasks:
            print(f"\n任务: {task}")
            print("-" * 40)
            
            plan = llm.plan(task)
            print(f"目标: {plan.goal}")
            print(f"步骤数: {len(plan.steps)}")
            print("执行步骤:")
            for i, step in enumerate(plan.steps[:5]):  # 只显示前5步
                print(f"  {i+1}. {step}")
            if len(plan.steps) > 5:
                print(f"  ... 还有 {len(plan.steps)-5} 个步骤")
            
            time.sleep(1)  # 避免 API 限流
            
    except Exception as e:
        print(f"❌ 规划失败: {str(e)}")


def demo_code_analysis():
    """演示代码分析功能"""
    print_section("3. 代码分析演示")
    
    if not os.getenv("DEEPSEEK_API_KEY"):
        print("跳过：需要 API Key")
        return
    
    # 创建示例代码
    code_content = """
def calculate_discount(price, customer_type):
    # 计算折扣
    if customer_type == "VIP":
        return price * 0.8
    elif customer_type == "Regular":
        return price * 0.95
    else:
        return price

def process_order(items, customer):
    total = 0
    for item in items:
        total += item['price'] * item['quantity']
    
    final_price = calculate_discount(total, customer['type'])
    
    # TODO: 添加税费计算
    # TODO: 验证库存
    
    return {
        'total': total,
        'discount': total - final_price,
        'final_price': final_price
    }
"""
    
    # 保存代码
    code_file = "demo_code.py"
    with open(code_file, "w") as f:
        f.write(code_content)
    print(f"✅ 创建示例代码: {code_file}")
    
    try:
        llm = DeepSeekLLM()
        
        # 分析代码
        print("\n分析代码质量...")
        analysis = llm.analyze_content(
            code_content,
            "分析这段代码的质量，找出潜在问题和改进建议"
        )
        
        print("\n分析结果:")
        if isinstance(analysis, dict) and "raw_response" in analysis:
            print(analysis["raw_response"][:500] + "...")
        else:
            print(json.dumps(analysis, indent=2, ensure_ascii=False)[:500] + "...")
            
    except Exception as e:
        print(f"❌ 分析失败: {str(e)}")


def demo_batch_processing():
    """演示批处理功能"""
    print_section("4. 批处理演示")
    
    # 创建多个 PIM 文件
    pims = {
        "user_system.md": """# 用户系统 PIM
## 实体
### 用户 (User)
- ID: 唯一标识
- 用户名: 字符串，唯一
- 邮箱: 字符串，唯一
""",
        "product_system.md": """# 产品系统 PIM
## 实体
### 产品 (Product)
- ID: 唯一标识
- 名称: 字符串
- 价格: 金额
""",
        "order_system.md": """# 订单系统 PIM
## 实体
### 订单 (Order)
- ID: 唯一标识
- 用户: 引用用户
- 产品列表: 产品数组
- 总金额: 金额
"""
    }
    
    # 保存文件
    for filename, content in pims.items():
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
    
    print(f"✅ 创建 {len(pims)} 个 PIM 文件")
    
    # 模拟批处理（不实际执行避免 API 消耗）
    print("\n批处理计划:")
    for filename in pims.keys():
        print(f"- 转换 {filename} → {filename.replace('.md', '_psm.md')}")
    
    print("\n实际批处理代码示例:")
    print("""
# 批处理转换
for pim_file in ['user_system.md', 'product_system.md', 'order_system.md']:
    cli = DeepSeekCLI()
    psm_file = pim_file.replace('.md', '_psm.md')
    success, _ = cli.execute_task(f"将 {pim_file} 转换为 FastAPI PSM，输出到 {psm_file}")
    print(f"{pim_file}: {'✅' if success else '❌'}")
""")


def demo_error_handling():
    """演示错误处理"""
    print_section("5. 错误处理演示")
    
    print("常见错误处理示例:\n")
    
    # 1. API Key 错误
    print("1. API Key 未设置:")
    print("""
try:
    cli = DeepSeekCLI()
except ValueError as e:
    print(f"❌ {e}")
    print("请运行: python setup_deepseek.py")
""")
    
    # 2. 文件不存在
    print("\n2. 文件不存在:")
    print("""
cli = DeepSeekCLI()
success, message = cli.execute_task("读取 not_exists.md")
if not success:
    print(f"❌ {message}")
""")
    
    # 3. 网络错误
    print("\n3. 网络错误处理:")
    print("""
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# 配置重试策略
session = requests.Session()
retry = Retry(total=3, backoff_factor=1)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)
""")


def show_summary():
    """显示总结"""
    print_section("演示总结")
    
    print("DeepSeek CLI 主要优势:")
    print("✅ 无需代理，中国直接访问")
    print("✅ 价格极低，约为 GPT-4 的 1/200")
    print("✅ 功能完整，支持任务规划、代码生成、分析等")
    print("✅ 易于集成，Python API 简单易用")
    
    print("\n快速开始:")
    print("1. 获取 API Key: https://platform.deepseek.com")
    print("2. 配置: python setup_deepseek.py")
    print("3. 使用: 参考 DEEPSEEK_CLI_README.md")
    
    print("\n相关文件:")
    print("- gemini_cli_deepseek.py  # 核心实现")
    print("- setup_deepseek.py       # 配置工具")
    print("- test_deepseek_cli.py    # 测试脚本")
    print("- DEEPSEEK_CLI_README.md  # 详细文档")


def cleanup_demo_files():
    """清理演示文件"""
    demo_files = [
        "demo_library_pim.md",
        "demo_library_psm.md",
        "demo_code.py",
        "user_system.md",
        "product_system.md",
        "order_system.md"
    ]
    
    for file in demo_files:
        if Path(file).exists():
            Path(file).unlink()
    
    print("\n✅ 演示文件已清理")


def main():
    """主函数"""
    print("DeepSeek CLI 功能演示")
    print("=" * 60)
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 运行演示
    demos = [
        ("基本用法", demo_basic_usage),
        ("任务规划", demo_task_planning),
        ("代码分析", demo_code_analysis),
        ("批处理", demo_batch_processing),
        ("错误处理", demo_error_handling)
    ]
    
    for name, demo_func in demos:
        try:
            if name == "基本用法":
                # 只运行基本演示以避免 API 消耗
                result = demo_func()
                if result is False and "API Key" in str(result):
                    print("\n⚠️ 需要配置 API Key 才能运行完整演示")
                    print("其他演示将以说明模式运行")
            else:
                # 其他演示只展示说明
                demo_func()
        except KeyboardInterrupt:
            print("\n\n用户中断")
            break
        except Exception as e:
            print(f"\n❌ {name}演示失败: {str(e)}")
    
    # 显示总结
    show_summary()
    
    # 清理文件
    cleanup = input("\n清理演示文件？[Y/n]: ").strip().lower()
    if cleanup != 'n':
        cleanup_demo_files()
    
    print("\n演示完成！")


if __name__ == "__main__":
    main()