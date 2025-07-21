"""Markdown format loader for PIM models - 支持自然语言描述"""

import re
from typing import Dict, Any, List, Optional, Tuple
import time

from core.models import (
    ModelLoadResult, PIMModel, Entity, Service, Method,
    Attribute, AttributeType, Flow, Rule
)
from utils.logger import setup_logger


class MarkdownLoader:
    """Load PIM models from natural language Markdown format"""
    
    def __init__(self):
        self.logger = setup_logger(__name__)
    
    async def load(self, file_path: str) -> ModelLoadResult:
        """Load model from Markdown file"""
        start_time = time.time()
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if not content.strip():
                return ModelLoadResult(
                    success=False,
                    errors=["Empty markdown file"]
                )
            
            # Parse model using natural language processing
            model = await self._parse_natural_markdown(content, file_path)
            
            load_time_ms = (time.time() - start_time) * 1000
            
            return ModelLoadResult(
                success=True,
                model=model,
                load_time_ms=load_time_ms
            )
            
        except Exception as e:
            self.logger.error(f"Failed to load markdown: {e}")
            return ModelLoadResult(
                success=False,
                errors=[f"Failed to load markdown: {str(e)}"]
            )
    
    async def _parse_natural_markdown(self, content: str, file_path: str) -> PIMModel:
        """Parse natural language markdown into PIM model"""
        from pathlib import Path
        
        # Extract domain from filename or title
        domain = Path(file_path).stem.replace('_', '-').replace(' ', '-').lower()
        
        # Split content into sections
        sections = self._split_sections(content)
        
        # Initialize model data
        description = ''
        entities = []
        services = []
        flows = {}
        rules = {}
        
        # Process each section
        for section_title, section_content in sections.items():
            if '概述' in section_title or '简介' in section_title:
                description = self._extract_description(section_content)
            elif '实体' in section_title or '对象' in section_title:
                entities = self._parse_entities(section_content)
            elif '流程' in section_title:
                flows, flow_services = self._parse_flows(section_content)
                services.extend(flow_services)
            elif '规则' in section_title:
                rules = self._parse_rules(section_content)
            elif '功能' in section_title:
                func_services = self._parse_functions(section_content, entities)
                services.extend(func_services)
        
        # Generate CRUD services if no services defined
        if not services and entities:
            services = self._generate_crud_services(entities)
        
        # Mark debuggable methods
        for service in services:
            for method in service.methods:
                flow_name = f"{service.name}.{method.name}"
                if flow_name in flows:
                    method.is_debuggable = True
                    method.flow = flow_name
        
        return PIMModel(
            domain=domain,
            version="1.0.0",
            description=description or f"{domain} system",
            entities=entities,
            services=services,
            flows=flows,
            rules=rules
        )
    
    def _split_sections(self, content: str) -> Dict[str, str]:
        """将Markdown内容分割成章节"""
        sections = {}
        current_section = None
        current_content = []
        
        for line in content.split('\n'):
            # 检测二级标题
            if line.startswith('## '):
                if current_section:
                    sections[current_section] = '\n'.join(current_content)
                current_section = line[3:].strip()
                current_content = []
            elif current_section:
                current_content.append(line)
        
        # 保存最后一个章节
        if current_section:
            sections[current_section] = '\n'.join(current_content)
        
        return sections
    
    def _extract_description(self, content: str) -> str:
        """提取系统描述"""
        lines = content.strip().split('\n')
        description_lines = []
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                description_lines.append(line)
                if len(description_lines) >= 2:  # 最多取前两行
                    break
        
        return ' '.join(description_lines)
    
    def _parse_entities(self, content: str) -> List[Entity]:
        """解析实体定义"""
        entities = []
        current_entity = None
        
        for line in content.split('\n'):
            line = line.strip()
            
            # 检测三级标题（实体名）
            if line.startswith('### '):
                if current_entity:
                    entities.append(current_entity)
                
                entity_name = line[4:].strip()
                current_entity = Entity(
                    name=self._to_english_name(entity_name),
                    description=entity_name,
                    attributes=[]
                )
            
            # 解析属性（列表项）
            elif line.startswith('- ') and current_entity:
                attr_info = self._parse_attribute(line[2:])
                if attr_info:
                    current_entity.attributes.append(attr_info)
            
            # 实体描述
            elif current_entity and line and not line.startswith('#') and not line.startswith('-'):
                if not current_entity.description or current_entity.description == current_entity.name:
                    current_entity.description = line
        
        # 添加最后一个实体
        if current_entity:
            entities.append(current_entity)
        
        return entities
    
    def _parse_attribute(self, attr_line: str) -> Optional[Attribute]:
        """解析属性描述"""
        # 提取属性名（加粗部分）
        name_match = re.match(r'\*\*(.+?)\*\*', attr_line)
        if not name_match:
            # 尝试普通格式
            parts = attr_line.split('（')
            if parts:
                name = parts[0].strip()
            else:
                return None
        else:
            name = name_match.group(1)
        
        # 标准化属性
        attr = Attribute(
            name=self._to_english_name(name),
            type=AttributeType.STRING,  # 默认类型
            description=attr_line,
            required=False
        )
        
        # 检测必填
        if '必填' in attr_line or '必须' in attr_line:
            attr.required = True
        
        # 检测唯一
        if '唯一' in attr_line:
            attr.unique = True
        
        # 检测类型和枚举
        if '（' in attr_line and '）' in attr_line:
            content = re.search(r'（(.+?)）', attr_line)
            if content:
                options = content.group(1)
                if '、' in options:
                    # 枚举类型
                    attr.type = AttributeType.ENUM
                    attr.enum_values = [opt.strip() for opt in options.split('、')]
                elif '关联到' in options or '关联' in options:
                    # 引用类型
                    attr.type = AttributeType.REFERENCE
                    ref_match = re.search(r'关联到?(.+)', options)
                    if ref_match:
                        attr.reference_entity = self._to_english_name(ref_match.group(1).strip())
        
        # 检测数值类型
        if '金额' in attr_line or '价格' in attr_line:
            attr.type = AttributeType.DECIMAL
        elif '数量' in attr_line or '数' in attr_line:
            attr.type = AttributeType.INTEGER
        
        # 检测日期类型
        if '日期' in attr_line or '时间' in attr_line:
            attr.type = AttributeType.DATETIME
            if '自动记录' in attr_line:
                attr.auto_now_add = True
        
        # 检测百分比
        if '百分比' in attr_line or '概率' in attr_line:
            attr.type = AttributeType.INTEGER
            attr.min = 0
            attr.max = 100
        
        return attr
    
    def _parse_flows(self, content: str) -> Tuple[Dict[str, Flow], List[Service]]:
        """解析流程定义"""
        flows = {}
        services = []
        current_flow = None
        in_mermaid = False
        mermaid_content = []
        
        for line in content.split('\n'):
            # 检测流程标题
            if line.startswith('### '):
                flow_name = line[4:].strip()
                current_flow = flow_name
                flows[flow_name] = Flow(
                    name=flow_name,
                    description=flow_name,
                    diagram='',
                    steps=[]
                )
                
                # 创建对应的服务方法
                service_name = self._extract_service_from_flow(flow_name)
                method_name = self._extract_method_from_flow(flow_name)
                
                # 查找或创建服务
                service = None
                for s in services:
                    if s.name == service_name:
                        service = s
                        break
                
                if not service:
                    service = Service(
                        name=service_name,
                        description=f'{service_name}相关业务',
                        methods=[]
                    )
                    services.append(service)
                
                # 添加方法
                service.methods.append(Method(
                    name=method_name,
                    description=flow_name,
                    flow=flow_name
                ))
            
            # 检测Mermaid代码块
            elif line.strip() == '```mermaid':
                in_mermaid = True
                mermaid_content = []
            elif line.strip() == '```' and in_mermaid:
                in_mermaid = False
                if current_flow and current_flow in flows:
                    flows[current_flow].diagram = '\n'.join(mermaid_content)
                    # 解析流程步骤
                    flows[current_flow].steps = self._parse_flow_steps(mermaid_content)
            elif in_mermaid:
                mermaid_content.append(line)
        
        return flows, services
    
    def _extract_service_from_flow(self, flow_name: str) -> str:
        """从流程名提取服务名"""
        if '客户' in flow_name:
            return 'CustomerService'
        elif '订单' in flow_name:
            return 'OrderService'
        elif '销售' in flow_name:
            return 'SalesService'
        elif '产品' in flow_name:
            return 'ProductService'
        elif '借' in flow_name or '还' in flow_name:
            return 'BorrowService'
        elif '图书' in flow_name:
            return 'BookService'
        else:
            return 'BusinessService'
    
    def _extract_method_from_flow(self, flow_name: str) -> str:
        """从流程名提取方法名"""
        # 移除'流程'后缀
        method = flow_name.replace('流程', '')
        # 转换为驼峰命名
        return self._to_camel_case(method)
    
    def _parse_flow_steps(self, mermaid_lines: List[str]) -> List[Dict[str, Any]]:
        """解析流程步骤"""
        steps = []
        step_ids = set()
        
        for line in mermaid_lines:
            # 解析节点定义
            node_match = re.search(r'(\w+)\[(.+?)\]', line)
            if node_match:
                step_id = node_match.group(1)
                step_label = node_match.group(2)
                
                if step_id not in step_ids:
                    step_ids.add(step_id)
                    step_type = 'action'
                    
                    if step_id.lower() == 'start' or '开始' in step_label:
                        step_type = 'start'
                    elif step_id.lower() == 'end' or '结束' in step_label:
                        step_type = 'end'
                    elif '{' in line and '}' in line:
                        step_type = 'decision'
                    
                    steps.append({
                        'id': step_id,
                        'type': step_type,
                        'description': step_label
                    })
        
        return steps
    
    def _parse_rules(self, content: str) -> Dict[str, Rule]:
        """解析业务规则"""
        rules = {}
        current_category = None
        
        for line in content.split('\n'):
            line = line.strip()
            
            # 类别标题
            if line.startswith('### '):
                current_category = line[4:].strip()
            
            # 规则项（编号列表）
            elif re.match(r'^\d+\.\s+\*\*(.+?)\*\*[：:](.+)', line):
                match = re.match(r'^\d+\.\s+\*\*(.+?)\*\*[：:](.+)', line)
                if match:
                    rule_name = match.group(1).strip()
                    rule_desc = match.group(2).strip()
                    # 生成规则ID
                    rule_id = self._to_snake_case(rule_name)
                    rules[rule_id] = Rule(
                        name=rule_name,
                        description=rule_desc,
                        condition="",
                        action=""
                    )
        
        return rules
    
    def _parse_functions(self, content: str, entities: List[Entity]) -> List[Service]:
        """解析功能描述生成服务"""
        services = []
        current_service = None
        
        for line in content.split('\n'):
            line = line.strip()
            
            # 功能分类
            if line.startswith('### '):
                service_name = line[4:].strip()
                if '管理' in service_name:
                    current_service = Service(
                        name=self._to_english_name(service_name.replace('功能', '服务')),
                        description=service_name,
                        methods=[]
                    )
                    services.append(current_service)
            
            # 功能项
            elif line.startswith('- ') and current_service:
                func_desc = line[2:].strip()
                method = self._function_to_method(func_desc)
                if method:
                    current_service.methods.append(method)
        
        return services
    
    def _function_to_method(self, func_desc: str) -> Optional[Method]:
        """将功能描述转换为方法定义"""
        # 常见功能模式映射
        patterns = [
            (r'添加新?(.+)', lambda m: Method(name=f'create{self._to_pascal_case(m.group(1))}', description=func_desc)),
            (r'修改(.+)信息', lambda m: Method(name=f'update{self._to_pascal_case(m.group(1))}', description=func_desc)),
            (r'查询(.+)', lambda m: Method(name=f'query{self._to_pascal_case(m.group(1))}', description=func_desc)),
            (r'删除(.+)', lambda m: Method(name=f'delete{self._to_pascal_case(m.group(1))}', description=func_desc)),
            (r'导出(.+)', lambda m: Method(name=f'export{self._to_pascal_case(m.group(1))}', description=func_desc)),
            (r'查看(.+)', lambda m: Method(name=f'view{self._to_pascal_case(m.group(1))}', description=func_desc)),
        ]
        
        for pattern, method_gen in patterns:
            match = re.match(pattern, func_desc)
            if match:
                return method_gen(match)
        
        # 默认方法
        return Method(
            name=self._to_camel_case(func_desc.replace(' ', '')),
            description=func_desc
        )
    
    def _generate_crud_services(self, entities: List[Entity]) -> List[Service]:
        """为实体自动生成CRUD服务"""
        services = []
        
        for entity in entities:
            service = Service(
                name=f"{entity.name}Service",
                description=f"管理{entity.description}的基础服务",
                methods=[
                    Method(
                        name=f"create{entity.name}",
                        description=f"创建新的{entity.description}",
                        parameters={'data': entity.name}
                    ),
                    Method(
                        name=f"get{entity.name}",
                        description=f"根据ID获取{entity.description}",
                        parameters={'id': 'string'}
                    ),
                    Method(
                        name=f"update{entity.name}",
                        description=f"更新{entity.description}信息",
                        parameters={'id': 'string', 'data': entity.name}
                    ),
                    Method(
                        name=f"delete{entity.name}",
                        description=f"删除{entity.description}",
                        parameters={'id': 'string'}
                    ),
                    Method(
                        name=f"list{entity.name}",
                        description=f"查询{entity.description}列表",
                        parameters={'filters': 'json'}
                    )
                ]
            )
            services.append(service)
        
        return services
    
    def _to_english_name(self, chinese_name: str) -> str:
        """将中文名转换为英文名"""
        # 常见映射
        mappings = {
            '客户': 'Customer',
            '订单': 'Order',
            '产品': 'Product',
            '用户': 'User',
            '销售机会': 'SalesOpportunity',
            '跟进记录': 'FollowUpRecord',
            '客户管理': 'CustomerManagement',
            '订单管理': 'OrderManagement',
            '销售管理': 'SalesManagement',
            '客户服务': 'CustomerService',
            '订单服务': 'OrderService',
            '销售服务': 'SalesService',
            # 图书管理系统相关
            '图书': 'Book',
            '借阅者': 'Borrower',
            '借阅记录': 'BorrowRecord',
            '图书管理': 'BookManagement',
            '借阅者管理': 'BorrowerManagement',
            '借还书管理': 'BorrowManagement',
            '图书服务': 'BookService',
            '借阅服务': 'BorrowService'
        }
        
        # 检查直接映射
        if chinese_name in mappings:
            return mappings[chinese_name]
        
        # 检查部分匹配
        for cn, en in mappings.items():
            if cn in chinese_name:
                return en
        
        # 返回拼音或原名
        return self._to_pascal_case(chinese_name)
    
    def _to_camel_case(self, text: str) -> str:
        """转换为驼峰命名（首字母小写）"""
        words = re.findall(r'[A-Za-z]+|\d+|[\u4e00-\u9fa5]+', text)
        if not words:
            return text
        
        # 第一个词小写，其余首字母大写
        result = words[0].lower()
        for word in words[1:]:
            result += word.capitalize()
        
        return result
    
    def _to_pascal_case(self, text: str) -> str:
        """转换为帕斯卡命名（首字母大写）"""
        words = re.findall(r'[A-Za-z]+|\d+|[\u4e00-\u9fa5]+', text)
        return ''.join(word.capitalize() for word in words)
    
    def _to_snake_case(self, text: str) -> str:
        """转换为蛇形命名"""
        # 移除特殊字符
        text = re.sub(r'[^\w\s]', '', text)
        # 替换空格为下划线
        text = re.sub(r'\s+', '_', text)
        # 转换为小写
        return text.lower()