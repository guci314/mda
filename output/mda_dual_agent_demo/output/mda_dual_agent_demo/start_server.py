#!/usr/bin/env python3
"""
启动FastAPI服务器
"""
import uvicorn
import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("启动图书借阅系统API服务器...")
    print("API文档地址: http://localhost:8000/docs")
    print("ReDoc文档地址: http://localhost:8000/redoc")
    print("按 Ctrl+C 停止服务器")
    
    try:
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n服务器已停止")
    except Exception as e:
        print(f"启动服务器时出错: {e}")
        sys.exit(1)