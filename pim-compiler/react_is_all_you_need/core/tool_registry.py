#!/usr/bin/env python3
"""
轻量级External Tool注册表 - 不需要Spring Cloud
只需要一个JSON文件 + 简单的HTTP服务
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import hashlib

class ToolRegistry:
    """极简的工具注册表 - 用文件系统实现"""

    def __init__(self, registry_dir: str = "~/.agent/tool_registry"):
        self.registry_dir = Path(registry_dir).expanduser()
        self.registry_dir.mkdir(parents=True, exist_ok=True)
        self.registry_file = self.registry_dir / "registry.json"
        self.load_registry()

    def load_registry(self):
        """加载注册表"""
        if self.registry_file.exists():
            with open(self.registry_file, 'r') as f:
                self.registry = json.load(f)
        else:
            self.registry = {
                "tools": {},
                "agents": {},
                "updated_at": datetime.now().isoformat()
            }

    def save_registry(self):
        """保存注册表"""
        self.registry["updated_at"] = datetime.now().isoformat()
        with open(self.registry_file, 'w') as f:
            json.dump(self.registry, f, indent=2, ensure_ascii=False)

    def register_tool(self, tool_name: str, tool_path: str, agent_name: str,
                      schema: Optional[Dict] = None) -> str:
        """注册External Tool"""
        tool_id = self._generate_id(f"{agent_name}/{tool_name}")

        self.registry["tools"][tool_id] = {
            "name": tool_name,
            "path": tool_path,
            "agent": agent_name,
            "schema": schema or {},
            "created_at": datetime.now().isoformat(),
            "version": self._get_file_hash(tool_path)
        }

        self.save_registry()
        return tool_id

    def register_agent(self, agent_name: str, endpoint: str,
                      capabilities: List[str]) -> str:
        """注册Agent服务"""
        agent_id = self._generate_id(agent_name)

        self.registry["agents"][agent_id] = {
            "name": agent_name,
            "endpoint": endpoint,  # 可以是文件路径或HTTP端点
            "capabilities": capabilities,
            "created_at": datetime.now().isoformat(),
            "status": "active"
        }

        self.save_registry()
        return agent_id

    def discover_tools(self, capability: Optional[str] = None) -> List[Dict]:
        """发现可用工具"""
        tools = []
        for tool_id, tool_info in self.registry["tools"].items():
            if capability is None or capability in tool_info.get("schema", {}).get("capabilities", []):
                tools.append({
                    "id": tool_id,
                    **tool_info
                })
        return tools

    def get_tool(self, tool_id: str) -> Optional[Dict]:
        """获取工具信息"""
        return self.registry["tools"].get(tool_id)

    def _generate_id(self, name: str) -> str:
        """生成简单ID"""
        return name.replace("/", "_").replace(" ", "_").lower()

    def _get_file_hash(self, file_path: str) -> str:
        """获取文件哈希（用于版本控制）"""
        if not os.path.exists(file_path):
            return "not_found"

        with open(file_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()[:8]


class SimpleToolBroker:
    """极简的工具代理 - 不需要消息队列"""

    def __init__(self, registry: ToolRegistry):
        self.registry = registry
        self._tool_cache = {}  # 缓存已加载的工具

    def call_tool(self, tool_id: str, params: Dict) -> any:
        """调用工具"""
        tool_info = self.registry.get_tool(tool_id)
        if not tool_info:
            return {"error": f"Tool {tool_id} not found"}

        # 动态加载工具
        tool_path = tool_info["path"]

        # 检查缓存
        cache_key = f"{tool_path}:{tool_info['version']}"
        if cache_key not in self._tool_cache:
            # 加载Python模块
            import importlib.util
            spec = importlib.util.spec_from_file_location(tool_id, tool_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            self._tool_cache[cache_key] = module

        module = self._tool_cache[cache_key]

        # 执行
        if hasattr(module, 'execute'):
            return module.execute(**params)
        else:
            return {"error": "Tool has no execute function"}


# 使用Redis的替代方案 - 用文件锁实现分布式
class FileBasedRegistry(ToolRegistry):
    """基于文件系统的分布式注册表"""

    def __init__(self, registry_dir: str = "~/.agent/shared_registry"):
        super().__init__(registry_dir)
        self.lock_file = self.registry_dir / ".lock"

    def _acquire_lock(self, timeout: int = 5):
        """获取文件锁（简单实现）"""
        import time
        start = time.time()
        while time.time() - start < timeout:
            try:
                # 原子性创建锁文件
                fd = os.open(str(self.lock_file),
                           os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.close(fd)
                return True
            except FileExistsError:
                time.sleep(0.1)
        return False

    def _release_lock(self):
        """释放锁"""
        try:
            os.unlink(self.lock_file)
        except:
            pass

    def save_registry(self):
        """带锁的保存"""
        if self._acquire_lock():
            try:
                super().save_registry()
            finally:
                self._release_lock()
        else:
            raise Exception("Cannot acquire lock for registry")


# HTTP API（可选，用Flask实现最简单的）
def create_registry_api(registry: ToolRegistry):
    """创建极简的HTTP API"""
    from flask import Flask, jsonify, request

    app = Flask(__name__)

    @app.route('/tools', methods=['GET'])
    def list_tools():
        capability = request.args.get('capability')
        tools = registry.discover_tools(capability)
        return jsonify(tools)

    @app.route('/tools/<tool_id>', methods=['GET'])
    def get_tool(tool_id):
        tool = registry.get_tool(tool_id)
        if tool:
            return jsonify(tool)
        return jsonify({"error": "Not found"}), 404

    @app.route('/tools', methods=['POST'])
    def register_tool():
        data = request.json
        tool_id = registry.register_tool(
            data['name'],
            data['path'],
            data['agent'],
            data.get('schema')
        )
        return jsonify({"id": tool_id})

    @app.route('/call/<tool_id>', methods=['POST'])
    def call_tool(tool_id):
        broker = SimpleToolBroker(registry)
        result = broker.call_tool(tool_id, request.json)
        return jsonify(result)

    return app


if __name__ == "__main__":
    # 示例用法
    registry = ToolRegistry()

    # Agent注册自己创建的工具
    tool_id = registry.register_tool(
        tool_name="order_processor",
        tool_path="/tmp/external_tools/order_processor.py",
        agent_name="order_agent",
        schema={
            "input": {"order_id": "string"},
            "output": {"status": "string"},
            "capabilities": ["order", "processing"]
        }
    )

    print(f"Registered tool: {tool_id}")

    # 发现工具
    tools = registry.discover_tools("order")
    print(f"Found tools: {tools}")

    # 调用工具
    broker = SimpleToolBroker(registry)
    result = broker.call_tool(tool_id, {"order_id": "12345"})
    print(f"Tool result: {result}")

    # 可选：启动HTTP服务
    # app = create_registry_api(registry)
    # app.run(host='0.0.0.0', port=5000)