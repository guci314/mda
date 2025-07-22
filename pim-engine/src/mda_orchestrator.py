"""MDA Orchestrator - 完整的模型驱动架构流程编排"""

import asyncio
import shutil
import subprocess
from pathlib import Path
from typing import Optional
import logging
import sys

# 添加 src 目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

from converters.pim_to_psm_gemini import PIMtoPSMGeminiConverter
from converters.psm_to_code_gemini import PSMtoCodeGeminiGenerator

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MDAOrchestrator:
    """MDA 流程编排器"""
    
    def __init__(self, deployment_base: str = "/opt/mda/services"):
        self.pim_to_psm = PIMtoPSMGeminiConverter()
        self.psm_to_code = PSMtoCodeGeminiGenerator()
        self.deployment_base = Path(deployment_base)
    
    async def process_model(self, 
                          pim_file: Path, 
                          platform: str = "fastapi",
                          deploy: bool = True) -> Path:
        """
        完整的 MDA 处理流程
        
        Args:
            pim_file: PIM 模型文件路径
            platform: 目标平台 (fastapi, spring 等)
            deploy: 是否自动部署
            
        Returns:
            生成的代码目录路径
        """
        
        model_name = pim_file.stem
        logger.info(f"开始处理模型: {model_name}")
        
        try:
            # 步骤 1: PIM → PSM
            logger.info("[1/4] 转换 PIM → PSM")
            psm_data = await self.pim_to_psm.convert(pim_file, platform)
            psm_file = pim_file.parent / f"{model_name}_psm_{platform}.yaml"
            logger.info(f"✓ PSM 已生成: {psm_file}")
            
            # 步骤 2: PSM → Code
            logger.info("[2/4] 生成代码 PSM → Code")
            output_dir = pim_file.parent / f"{model_name}_{platform}_generated"
            generated_files = await self.psm_to_code.generate(psm_file, output_dir)
            logger.info(f"✓ 代码已生成: {len(generated_files)} 个文件")
            
            # 步骤 3: 测试生成的代码
            logger.info("[3/4] 测试生成的代码")
            await self._test_generated_code(output_dir)
            logger.info("✓ 代码测试通过")
            
            # 步骤 4: 部署（可选）
            if deploy:
                logger.info("[4/4] 部署服务")
                service_url = await self._deploy_service(model_name, output_dir)
                logger.info(f"✓ 服务已部署: {service_url}")
            else:
                logger.info("[4/4] 跳过部署")
            
            logger.info(f"✅ 模型 {model_name} 处理完成！")
            logger.info(f"   生成的代码位于: {output_dir}")
            
            return output_dir
            
        except Exception as e:
            logger.error(f"处理失败: {e}")
            raise
    
    async def _test_generated_code(self, code_dir: Path):
        """测试生成的代码"""
        # 1. 语法检查
        logger.info("  - 检查 Python 语法...")
        for py_file in code_dir.glob("*.py"):
            result = subprocess.run(
                ["python", "-m", "py_compile", str(py_file)],
                capture_output=True
            )
            if result.returncode != 0:
                raise ValueError(f"语法错误 in {py_file}: {result.stderr.decode()}")
        
        # 2. 导入检查
        logger.info("  - 检查导入...")
        test_script = f"""
import sys
sys.path.insert(0, '{code_dir}')
try:
    import main
    import models
    import schemas
    import services
    import api
    print("All imports successful")
except Exception as e:
    print(f"Import error: {{e}}")
    sys.exit(1)
"""
        result = subprocess.run(
            ["python", "-c", test_script],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            raise ValueError(f"导入错误: {result.stdout}")
    
    async def _deploy_service(self, model_name: str, code_dir: Path) -> str:
        """部署服务（简化版）"""
        # 在开发环境中，只是复制到部署目录
        deploy_dir = self.deployment_base / model_name
        
        # 创建部署目录
        deploy_dir.mkdir(parents=True, exist_ok=True)
        
        # 复制代码
        for item in code_dir.iterdir():
            if item.is_file():
                shutil.copy2(item, deploy_dir)
        
        # 创建启动脚本
        start_script = deploy_dir / "start.sh"
        start_script.write_text(f"""#!/bin/bash
cd {deploy_dir}
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
""")
        start_script.chmod(0o755)
        
        # 返回服务 URL（假设的）
        return f"http://localhost:8000"
    
    async def batch_process(self, pim_files: list[Path], platform: str = "fastapi"):
        """批量处理多个 PIM 模型"""
        logger.info(f"批量处理 {len(pim_files)} 个模型")
        
        results = []
        for pim_file in pim_files:
            try:
                output_dir = await self.process_model(pim_file, platform, deploy=False)
                results.append((pim_file, "成功", output_dir))
            except Exception as e:
                results.append((pim_file, "失败", str(e)))
                logger.error(f"处理 {pim_file} 失败: {e}")
        
        # 打印结果汇总
        logger.info("\n处理结果汇总:")
        for pim_file, status, detail in results:
            logger.info(f"  - {pim_file.name}: {status}")
            if status == "成功":
                logger.info(f"    输出: {detail}")
            else:
                logger.info(f"    错误: {detail}")


# CLI 接口
async def main():
    """命令行接口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="MDA 模型驱动架构处理器")
    parser.add_argument("pim_file", type=Path, help="PIM 模型文件路径")
    parser.add_argument("--platform", default="fastapi", 
                       choices=["fastapi", "spring"],
                       help="目标平台")
    parser.add_argument("--no-deploy", action="store_true",
                       help="只生成代码，不部署")
    parser.add_argument("--output-dir", type=Path,
                       help="输出目录（默认在 PIM 文件同目录）")
    
    args = parser.parse_args()
    
    # 检查文件存在
    if not args.pim_file.exists():
        logger.error(f"文件不存在: {args.pim_file}")
        sys.exit(1)
    
    # 创建编排器
    orchestrator = MDAOrchestrator()
    
    try:
        # 处理模型
        output_dir = await orchestrator.process_model(
            args.pim_file,
            platform=args.platform,
            deploy=not args.no_deploy
        )
        
        print(f"\n✅ 成功！生成的代码位于: {output_dir}")
        print(f"\n下一步:")
        print(f"  cd {output_dir}")
        print(f"  python -m venv venv")
        print(f"  source venv/bin/activate  # Windows: venv\\Scripts\\activate")
        print(f"  pip install -r requirements.txt")
        print(f"  python main.py")
        
    except Exception as e:
        logger.error(f"处理失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())