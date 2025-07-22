"""Gemini CLI utility functions"""

import subprocess
import os
import asyncio
import logging
from typing import Optional

logger = logging.getLogger(__name__)


async def call_gemini_cli(prompt: str, model: Optional[str] = None, gemini_cli_path: str = "/home/guci/.nvm/versions/node/v22.17.0/bin/gemini") -> str:
    """
    调用 Gemini CLI
    
    Args:
        prompt: 提示内容
        model: 模型名称，默认从环境变量 GEMINI_MODEL 获取
        gemini_cli_path: Gemini CLI 路径
        
    Returns:
        Gemini 响应内容
        
    Raises:
        FileNotFoundError: 如果 Gemini CLI 不存在
        Exception: 如果 Gemini CLI 执行失败
    """
    # 确保 Gemini CLI 存在
    if not os.path.exists(gemini_cli_path):
        raise FileNotFoundError(f"Gemini CLI not found at: {gemini_cli_path}")
    
    # 设置环境变量（包括代理）
    env = os.environ.copy()
    
    # 设置代理（如果配置了）
    proxy_host = os.getenv("PROXY_HOST", "127.0.0.1")
    proxy_port = os.getenv("PROXY_PORT", "7890")
    if proxy_host and proxy_port:
        proxy_url = f"http://{proxy_host}:{proxy_port}"
        env["HTTP_PROXY"] = proxy_url
        env["HTTPS_PROXY"] = proxy_url
        logger.debug(f"Using proxy: {proxy_url}")
    
    # API key 应该已经从 .env 文件加载到环境变量中
    if "GEMINI_API_KEY" not in env and "GOOGLE_AI_STUDIO_KEY" not in env:
        logger.warning("GEMINI_API_KEY or GOOGLE_AI_STUDIO_KEY not found in environment")
    
    # 如果有 GOOGLE_AI_STUDIO_KEY，将其设置为 GEMINI_API_KEY
    if "GOOGLE_AI_STUDIO_KEY" in env and "GEMINI_API_KEY" not in env:
        env["GEMINI_API_KEY"] = env["GOOGLE_AI_STUDIO_KEY"]
    
    # 构建命令 - 使用 -p 参数传递提示，-m 参数指定模型
    if model is None:
        model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
    
    cmd = [gemini_cli_path, "-m", model, "-p", prompt]
    
    logger.info(f"Calling Gemini CLI with model: {model}")
    logger.debug(f"Command: {' '.join(cmd[:3])}...")  # 只记录命令前几个参数
    
    # 执行命令
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        env=env
    )
    
    stdout, stderr = await process.communicate()
    
    if process.returncode != 0:
        error_msg = stderr.decode('utf-8')
        logger.error(f"Gemini CLI error: {error_msg}")
        raise Exception(f"Gemini CLI failed: {error_msg}")
    
    result = stdout.decode('utf-8')
    logger.debug(f"Gemini CLI response length: {len(result)} characters")
    
    return result


def call_gemini_cli_sync(prompt: str, model: Optional[str] = None, gemini_cli_path: str = "/home/guci/.nvm/versions/node/v22.17.0/bin/gemini") -> str:
    """
    同步版本的 Gemini CLI 调用
    
    Args:
        prompt: 提示内容
        model: 模型名称，默认从环境变量 GEMINI_MODEL 获取
        gemini_cli_path: Gemini CLI 路径
        
    Returns:
        Gemini 响应内容
    """
    # 确保 Gemini CLI 存在
    if not os.path.exists(gemini_cli_path):
        raise FileNotFoundError(f"Gemini CLI not found at: {gemini_cli_path}")
    
    # 设置环境变量（包括代理）
    env = os.environ.copy()
    
    # 设置代理（如果配置了）
    proxy_host = os.getenv("PROXY_HOST", "127.0.0.1")
    proxy_port = os.getenv("PROXY_PORT", "7890")
    if proxy_host and proxy_port:
        proxy_url = f"http://{proxy_host}:{proxy_port}"
        env["HTTP_PROXY"] = proxy_url
        env["HTTPS_PROXY"] = proxy_url
    
    # API key 设置
    if "GOOGLE_AI_STUDIO_KEY" in env and "GEMINI_API_KEY" not in env:
        env["GEMINI_API_KEY"] = env["GOOGLE_AI_STUDIO_KEY"]
    
    # 构建命令
    if model is None:
        model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
    
    cmd = [gemini_cli_path, "-m", model, "-p", prompt]
    
    # 执行命令
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        env=env
    )
    
    if result.returncode != 0:
        raise Exception(f"Gemini CLI failed: {result.stderr}")
    
    return result.stdout

def main():
    
    try:
        output = call_gemini_cli_sync("总结当前项目，请用中文")
        print(output)
    except Exception as e:
        print(f"调用失败: {e}")

if __name__ == "__main__":
    main()
