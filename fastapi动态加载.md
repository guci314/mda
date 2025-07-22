# FastAPI 动态加载和卸载方案

## 概述

本方案解决 PIM Engine 中动态加载和卸载模型的需求，确保卸载后在 OpenAPI (Swagger) 和 ReDoc 界面中看不到已卸载的 API。

## 核心挑战

1. FastAPI 原生不支持运行时删除路由
2. OpenAPI Schema 会缓存，需要强制刷新
3. 需要完全清理路由，包括从文档中移除

## 解决方案

### 方案一：直接操作路由表（推荐）

```python
from fastapi import FastAPI, APIRouter
from typing import Dict, Set, Optional
import asyncio

class DynamicRouteManager:
    """动态路由管理器"""
    
    def __init__(self, app: FastAPI):
        self.app = app
        self.loaded_models: Dict[str, APIRouter] = {}
        self.route_paths: Dict[str, Set[str]] = {}  # 记录每个模型的所有路由路径
    
    def load_model(self, model_name: str, router: APIRouter) -> bool:
        """加载模型路由"""
        if model_name in self.loaded_models:
            return False
        
        # 记录该模型的所有路由路径
        paths = set()
        for route in router.routes:
            if hasattr(route, 'path'):
                paths.add(route.path)
        
        # 添加路由
        self.app.include_router(router, prefix=f"/api/{model_name}")
        
        # 保存信息
        self.loaded_models[model_name] = router
        self.route_paths[model_name] = paths
        
        # 清除 OpenAPI 缓存
        self._clear_openapi_cache()
        
        return True
    
    def unload_model(self, model_name: str) -> bool:
        """卸载模型路由"""
        if model_name not in self.loaded_models:
            return False
        
        # 获取要删除的路由路径
        paths_to_remove = {f"/api/{model_name}{path}" for path in self.route_paths[model_name]}
        
        # 从 app.routes 中删除相关路由
        new_routes = []
        for route in self.app.routes:
            if hasattr(route, 'path') and route.path not in paths_to_remove:
                new_routes.append(route)
            elif not hasattr(route, 'path'):
                # 保留非路径路由（如 Mount）
                new_routes.append(route)
        
        self.app.routes = new_routes
        
        # 清理记录
        del self.loaded_models[model_name]
        del self.route_paths[model_name]
        
        # 清除 OpenAPI 缓存
        self._clear_openapi_cache()
        
        return True
    
    def _clear_openapi_cache(self):
        """清除 OpenAPI Schema 缓存"""
        self.app.openapi_schema = None
```

### 方案二：使用子应用挂载（Mount）

```python
from fastapi import FastAPI
from typing import Dict

class SubAppManager:
    """子应用管理器"""
    
    def __init__(self, app: FastAPI):
        self.app = app
        self.sub_apps: Dict[str, FastAPI] = {}
        self.mount_paths: Dict[str, str] = {}
    
    def load_model(self, model_name: str, create_sub_app_func) -> bool:
        """加载模型为子应用"""
        if model_name in self.sub_apps:
            return False
        
        # 创建子应用
        sub_app = create_sub_app_func()
        mount_path = f"/api/{model_name}"
        
        # 挂载子应用
        self.app.mount(mount_path, sub_app)
        
        # 保存信息
        self.sub_apps[model_name] = sub_app
        self.mount_paths[model_name] = mount_path
        
        return True
    
    def unload_model(self, model_name: str) -> bool:
        """卸载模型子应用"""
        if model_name not in self.sub_apps:
            return False
        
        mount_path = self.mount_paths[model_name]
        
        # 从路由中移除挂载点
        new_routes = []
        for route in self.app.routes:
            if hasattr(route, 'path') and route.path != mount_path:
                new_routes.append(route)
            elif hasattr(route, 'app') and route.app != self.sub_apps[model_name]:
                new_routes.append(route)
        
        self.app.routes = new_routes
        
        # 清理记录
        del self.sub_apps[model_name]
        del self.mount_paths[model_name]
        
        # 清除缓存
        self.app.openapi_schema = None
        
        return True
```

### 方案三：完整的 PIM Engine 集成方案

```python
from fastapi import FastAPI, APIRouter, HTTPException
from typing import Dict, List, Optional
from pathlib import Path
import importlib.util
import sys

class PIMRouteManager:
    """PIM 路由管理器"""
    
    def __init__(self, app: FastAPI):
        self.app = app
        self.loaded_pims: Dict[str, Dict] = {}  # {pim_name: {router, routes, module}}
        
    def load_pim(self, pim_name: str, pim_file: Path) -> Dict:
        """从 PIM 文件加载并生成路由"""
        if pim_name in self.loaded_pims:
            raise ValueError(f"PIM {pim_name} already loaded")
        
        # 创建路由器
        router = APIRouter(
            prefix=f"/{pim_name}",
            tags=[pim_name]
        )
        
        # 根据 PIM 定义生成路由
        routes = self._generate_routes_from_pim(pim_file, router)
        
        # 注册路由到主应用
        self.app.include_router(router)
        
        # 记录加载信息
        self.loaded_pims[pim_name] = {
            "router": router,
            "routes": routes,
            "file": pim_file
        }
        
        # 清除 OpenAPI 缓存
        self._refresh_openapi()
        
        return {
            "pim_name": pim_name,
            "routes_count": len(routes),
            "endpoints": [r["path"] for r in routes]
        }
    
    def unload_pim(self, pim_name: str) -> bool:
        """卸载 PIM 及其所有路由"""
        if pim_name not in self.loaded_pims:
            return False
        
        pim_info = self.loaded_pims[pim_name]
        router = pim_info["router"]
        
        # 获取该 PIM 的所有路由路径
        pim_paths = set()
        for route in router.routes:
            if hasattr(route, 'path'):
                # 完整路径 = router prefix + route path
                full_path = f"/{pim_name}{route.path}"
                pim_paths.add(full_path)
        
        # 从主应用中移除这些路由
        original_routes = list(self.app.routes)
        self.app.routes = []
        
        for route in original_routes:
            # 检查是否是要删除的路由
            if hasattr(route, 'path'):
                if route.path not in pim_paths:
                    self.app.routes.append(route)
            else:
                # 保留非路径类型的路由
                self.app.routes.append(route)
        
        # 清理记录
        del self.loaded_pims[pim_name]
        
        # 刷新 OpenAPI
        self._refresh_openapi()
        
        return True
    
    def list_loaded_pims(self) -> List[Dict]:
        """列出所有已加载的 PIM"""
        return [
            {
                "name": name,
                "file": str(info["file"]),
                "routes_count": len(info["routes"])
            }
            for name, info in self.loaded_pims.items()
        ]
    
    def _generate_routes_from_pim(self, pim_file: Path, router: APIRouter) -> List[Dict]:
        """根据 PIM 定义生成路由"""
        # 这里应该解析 PIM 文件并生成相应的路由
        # 示例实现
        routes = []
        
        # 假设 PIM 定义了 CRUD 操作
        # 实际实现应该解析 PIM 文件内容
        
        # 创建
        @router.post("/")
        async def create_item(data: dict):
            return {"message": "Created", "data": data}
        
        routes.append({"path": "/", "method": "POST"})
        
        # 读取列表
        @router.get("/")
        async def list_items():
            return {"items": []}
        
        routes.append({"path": "/", "method": "GET"})
        
        # 读取单个
        @router.get("/{item_id}")
        async def get_item(item_id: str):
            return {"id": item_id}
        
        routes.append({"path": "/{item_id}", "method": "GET"})
        
        # 更新
        @router.put("/{item_id}")
        async def update_item(item_id: str, data: dict):
            return {"id": item_id, "data": data}
        
        routes.append({"path": "/{item_id}", "method": "PUT"})
        
        # 删除
        @router.delete("/{item_id}")
        async def delete_item(item_id: str):
            return {"message": "Deleted", "id": item_id}
        
        routes.append({"path": "/{item_id}", "method": "DELETE"})
        
        return routes
    
    def _refresh_openapi(self):
        """刷新 OpenAPI Schema"""
        # 清除缓存的 schema
        self.app.openapi_schema = None
        
        # 可选：手动触发重新生成
        # self.app.openapi()

# 使用示例
app = FastAPI(title="PIM Engine")
pim_manager = PIMRouteManager(app)

# 管理端点
@app.post("/admin/pim/load")
async def load_pim(pim_name: str, pim_file: str):
    """加载 PIM 模型"""
    try:
        result = pim_manager.load_pim(pim_name, Path(pim_file))
        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/admin/pim/{pim_name}")
async def unload_pim(pim_name: str):
    """卸载 PIM 模型"""
    if pim_manager.unload_pim(pim_name):
        return {"status": "success", "message": f"PIM {pim_name} unloaded"}
    else:
        raise HTTPException(status_code=404, detail=f"PIM {pim_name} not found")

@app.get("/admin/pim")
async def list_pims():
    """列出所有已加载的 PIM"""
    return {"pims": pim_manager.list_loaded_pims()}
```

## 关键技术点

### 1. 路由删除
- 直接操作 `app.routes` 列表
- 需要记录每个模型的所有路由路径
- 删除时精确匹配路径

### 2. OpenAPI Schema 刷新
```python
# 清除缓存
app.openapi_schema = None

# 下次访问 /docs 或 /redoc 时会重新生成
```

### 3. 路由隔离
- 使用统一的前缀（如 `/api/{model_name}`）
- 便于批量管理和删除

### 4. 状态管理
- 维护已加载模型的记录
- 跟踪每个模型的路由信息

## 注意事项

1. **线程安全**：在生产环境中，路由操作应该加锁
```python
import threading

class ThreadSafePIMManager:
    def __init__(self, app: FastAPI):
        self.app = app
        self.lock = threading.Lock()
        self.loaded_pims = {}
    
    def load_pim(self, pim_name: str, pim_file: Path):
        with self.lock:
            # 执行加载操作
            pass
    
    def unload_pim(self, pim_name: str):
        with self.lock:
            # 执行卸载操作
            pass
```

2. **内存管理**：卸载时确保清理所有引用，避免内存泄漏

3. **依赖处理**：如果 PIM 之间有依赖关系，需要检查依赖

4. **持久化**：考虑将加载状态持久化，以便重启后恢复

## 测试验证

```python
# 测试脚本
import requests

# 1. 加载 PIM
response = requests.post("http://localhost:8000/admin/pim/load", 
    json={"pim_name": "user_management", "pim_file": "models/user.yaml"})
print("Load:", response.json())

# 2. 检查 API 文档
# 访问 http://localhost:8000/docs - 应该能看到 user_management 的 API

# 3. 测试 API
response = requests.get("http://localhost:8000/user_management/")
print("API Test:", response.json())

# 4. 卸载 PIM
response = requests.delete("http://localhost:8000/admin/pim/user_management")
print("Unload:", response.json())

# 5. 再次检查 API 文档
# 访问 http://localhost:8000/docs - user_management 的 API 应该消失

# 6. 测试 API（应该返回 404）
response = requests.get("http://localhost:8000/user_management/")
print("API Test after unload:", response.status_code)  # 应该是 404
```

## 总结

本方案提供了三种实现动态路由加载/卸载的方法：

1. **直接操作路由表**：最灵活，推荐用于 PIM Engine
2. **子应用挂载**：隔离性好，但灵活性稍差
3. **完整集成方案**：专门为 PIM Engine 设计

关键是要：
- 精确管理路由路径
- 正确清理 OpenAPI 缓存
- 确保线程安全
- 提供管理接口

这样可以实现 PIM 的热加载和卸载，且在 Swagger/ReDoc 中能正确反映当前状态。