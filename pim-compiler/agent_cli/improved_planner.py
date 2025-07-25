"""
改进的任务规划器 - 基于程序员视角的里程碑式规划
"""

# 改进的规划提示词
IMPROVED_PLANNER_SYSTEM_PROMPT = """你是一个资深软件工程师，负责将开发任务分解为可执行的里程碑。

## 规划原则

1. **里程碑导向**：每个步骤必须是一个明确的交付物或功能模块
2. **原子性**：每个步骤要么完全成功，要么完全失败，不存在部分完成
3. **可验证性**：每个步骤必须有明确的验收标准
4. **依赖明确**：清晰标注步骤间的依赖关系

## 步骤类型

- **基础设施步骤**：创建项目结构、配置环境、初始化数据库等
- **功能模块步骤**：实现完整的功能单元（如用户认证、数据CRUD等）
- **集成步骤**：组件间的连接和集成（如API路由注册、中间件配置等）
- **验证步骤**：运行测试、验证功能、检查集成

## 步骤粒度标准

✅ 好的步骤：
- "实现完整的用户认证模块（包括模型、服务、API端点）"
- "创建所有数据库模型并验证关系正确"
- "实现并测试所有博客文章的CRUD操作"

❌ 错误的步骤：
- "创建一个模型文件"（粒度太细）
- "编写代码"（太模糊）
- "创建API"（范围不明确）

## 返回格式

{
    "steps": [
        {
            "name": "步骤名称（简洁的里程碑描述）",
            "type": "infrastructure|feature|integration|validation",
            "description": "详细说明要完成的工作",
            "deliverables": [
                "具体的交付物1",
                "具体的交付物2"
            ],
            "acceptance_criteria": [
                "验收标准1",
                "验收标准2"
            ],
            "dependencies": ["依赖的前置步骤名称"]
        }
    ]
}

## 示例

对于"创建博客管理系统"的任务，好的规划是：

1. **初始化项目基础设施**
   - 交付物：项目目录结构、配置文件、依赖管理文件
   - 验收标准：目录结构完整、配置可读取、依赖可安装

2. **实现数据层**
   - 交付物：所有实体模型、数据库连接、迁移脚本
   - 验收标准：模型关系正确、数据库可连接、表结构创建成功

3. **实现业务逻辑层**
   - 交付物：所有服务类、业务规则实现、错误处理
   - 验收标准：服务方法可调用、业务规则正确、错误处理完善

请记住：每个步骤都应该是一个有意义的、可独立交付的功能单元。"""

IMPROVED_PLANNER_HUMAN_PROMPT = """任务：{task}

请将此任务分解为程序员视角的里程碑步骤。每个步骤都应该：
1. 代表一个完整的功能模块或交付物
2. 有明确的完成标准
3. 可以独立验证和测试

注意避免过细的粒度（如单个文件创建）或过粗的粒度（如"实现整个系统"）。"""


def create_smart_plan_validator():
    """创建智能的计划验证器"""
    
    def validate_step_granularity(step: dict) -> tuple[bool, str]:
        """验证步骤粒度是否合适"""
        
        # 检查是否有明确的交付物
        if "deliverables" not in step or not step["deliverables"]:
            return False, "步骤缺少明确的交付物"
            
        # 检查是否有验收标准
        if "acceptance_criteria" not in step or not step["acceptance_criteria"]:
            return False, "步骤缺少验收标准"
            
        # 检查步骤名称是否太细
        too_fine_keywords = ["创建文件", "写入内容", "添加代码", "修改文件"]
        if any(keyword in step["name"] for keyword in too_fine_keywords):
            return False, "步骤粒度过细，应该聚合为更大的功能单元"
            
        # 检查步骤名称是否太粗
        too_coarse_keywords = ["实现系统", "完成所有", "创建整个"]
        if any(keyword in step["name"] for keyword in too_coarse_keywords):
            return False, "步骤粒度过粗，应该分解为具体的功能模块"
            
        return True, "步骤粒度合适"
        
    return validate_step_granularity


class MilestoneBasedPlanner:
    """基于里程碑的任务规划器"""
    
    def __init__(self):
        self.validator = create_smart_plan_validator()
        
    def validate_plan(self, plan: dict) -> tuple[bool, list[str]]:
        """验证整个计划的质量"""
        issues = []
        
        if "steps" not in plan:
            issues.append("计划缺少步骤列表")
            return False, issues
            
        # 验证每个步骤
        for i, step in enumerate(plan["steps"]):
            is_valid, message = self.validator(step)
            if not is_valid:
                issues.append(f"步骤 {i+1} ({step.get('name', '未命名')}): {message}")
                
        # 检查依赖关系
        step_names = {step["name"] for step in plan["steps"]}
        for step in plan["steps"]:
            if "dependencies" in step:
                for dep in step["dependencies"]:
                    if dep not in step_names:
                        issues.append(f"步骤 '{step['name']}' 依赖不存在的步骤 '{dep}'")
                        
        return len(issues) == 0, issues
        
    def suggest_step_aggregation(self, steps: list[dict]) -> list[dict]:
        """建议如何聚合过细的步骤"""
        aggregated = []
        current_module = None
        
        for step in steps:
            # 识别属于同一模块的步骤
            if step.get("type") == "infrastructure":
                if current_module and current_module["type"] == "infrastructure":
                    # 聚合基础设施步骤
                    current_module["deliverables"].extend(step.get("deliverables", []))
                    current_module["description"] += f"; {step['description']}"
                else:
                    current_module = step.copy()
                    aggregated.append(current_module)
            else:
                aggregated.append(step)
                current_module = None
                
        return aggregated


# 步骤模板，帮助生成高质量的步骤
STEP_TEMPLATES = {
    "infrastructure": {
        "name": "初始化{component}基础设施",
        "deliverables": [
            "完整的目录结构",
            "配置文件",
            "依赖声明文件"
        ],
        "acceptance_criteria": [
            "目录结构符合项目规范",
            "配置文件语法正确且包含必要配置项",
            "依赖可以成功安装"
        ]
    },
    "data_layer": {
        "name": "实现{domain}数据层",
        "deliverables": [
            "所有相关的数据模型",
            "数据库迁移脚本",
            "数据访问对象（DAO）或仓储"
        ],
        "acceptance_criteria": [
            "模型定义完整且关系正确",
            "数据库表可以成功创建",
            "基本的CRUD操作可用"
        ]
    },
    "business_logic": {
        "name": "实现{feature}业务逻辑",
        "deliverables": [
            "服务层实现",
            "业务规则验证",
            "异常处理机制"
        ],
        "acceptance_criteria": [
            "核心业务逻辑正确实现",
            "输入验证完善",
            "错误处理恰当"
        ]
    },
    "api_layer": {
        "name": "实现{resource}API端点",
        "deliverables": [
            "RESTful API端点",
            "请求/响应模型",
            "API文档"
        ],
        "acceptance_criteria": [
            "所有CRUD端点可访问",
            "响应格式符合规范",
            "错误响应信息清晰"
        ]
    },
    "integration": {
        "name": "集成{component}到主应用",
        "deliverables": [
            "路由注册",
            "中间件配置",
            "依赖注入设置"
        ],
        "acceptance_criteria": [
            "组件正确注册到应用",
            "路由可正常访问",
            "依赖关系正确解析"
        ]
    }
}