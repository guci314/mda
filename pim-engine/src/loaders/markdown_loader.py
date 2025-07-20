"""Markdown format loader for PIM models"""

import re
from typing import Dict, Any, List, Optional, Tuple
import time

from core.models import (
    ModelLoadResult, PIMModel, Entity, Service, Method,
    Attribute, AttributeType, Flow, Rule
)


class MarkdownLoader:
    """Load PIM models from Markdown format"""
    
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
            
            # Parse model
            model = await self._parse_markdown(content)
            
            load_time_ms = (time.time() - start_time) * 1000
            
            return ModelLoadResult(
                success=True,
                model=model,
                load_time_ms=load_time_ms
            )
            
        except Exception as e:
            return ModelLoadResult(
                success=False,
                errors=[f"Failed to load markdown: {str(e)}"]
            )
    
    async def _parse_markdown(self, content: str) -> PIMModel:
        """Parse markdown content into PIM model"""
        # Extract domain from title
        domain = self._extract_domain(content)
        
        # Extract entities
        entities = self._extract_entities(content)
        
        # Extract services
        services = self._extract_services(content)
        
        # Extract flows
        flows = self._extract_flows(content)
        
        # Extract rules
        rules = self._extract_rules(content)
        
        # Mark debuggable methods
        for service in services:
            for method in service.methods:
                flow_name = f"{service.name}.{method.name}"
                if flow_name in flows:
                    method.is_debuggable = True
                    method.flow = flow_name
        
        return PIMModel(
            domain=domain,
            entities=entities,
            services=services,
            flows=flows,
            rules=rules
        )
    
    def _extract_domain(self, content: str) -> str:
        """Extract domain name from markdown title"""
        match = re.search(r'^#\s+(.+?)(?:\s+领域模型|\s+\(PIM\))?$', content, re.MULTILINE)
        if match:
            return match.group(1).strip()
        return "Unknown"
    
    def _extract_entities(self, content: str) -> List[Entity]:
        """Extract entities from markdown"""
        entities = []
        
        # Find entity sections
        entity_pattern = r'###\s+(.+?)\s*\((\w+)\)\s*\n(.*?)(?=###|##\s|$)'
        
        for match in re.finditer(entity_pattern, content, re.DOTALL):
            entity_name_cn = match.group(1).strip()
            entity_name_en = match.group(2).strip()
            entity_content = match.group(3).strip()
            
            # Extract attributes
            attributes = self._parse_attributes(entity_content)
            
            # Extract constraints
            constraints = self._parse_constraints(entity_content)
            
            entities.append(Entity(
                name=entity_name_en,
                description=entity_name_cn,
                attributes=attributes,
                constraints=constraints
            ))
        
        return entities
    
    def _extract_services(self, content: str) -> List[Service]:
        """Extract services from markdown"""
        services = []
        
        # Find service sections
        service_pattern = r'###\s+(.+?服务)\s*\((\w+)\)\s*\n(.*?)(?=###|##\s|$)'
        
        for match in re.finditer(service_pattern, content, re.DOTALL):
            service_name_cn = match.group(1).strip()
            service_name_en = match.group(2).strip()
            service_content = match.group(3).strip()
            
            # Extract methods
            methods = self._parse_methods(service_content)
            
            services.append(Service(
                name=service_name_en,
                description=service_name_cn,
                methods=methods
            ))
        
        return services
    
    def _extract_flows(self, content: str) -> Dict[str, Flow]:
        """Extract flows from markdown"""
        flows = {}
        
        # Find flow sections with mermaid diagrams
        flow_pattern = r'###\s+(\w+Service)\.(\w+)\s+流程\s*\n(.*?)```mermaid\s*\n(.*?)\n```'
        
        for match in re.finditer(flow_pattern, content, re.DOTALL):
            service_name = match.group(1)
            method_name = match.group(2)
            flow_description = match.group(3).strip()
            mermaid_diagram = match.group(4).strip()
            
            flow_name = f"{service_name}.{method_name}"
            
            # Parse mermaid diagram to extract steps
            steps = self._parse_mermaid_steps(mermaid_diagram)
            
            flows[flow_name] = Flow(
                name=flow_name,
                description=flow_description,
                steps=steps,
                diagram=mermaid_diagram
            )
        
        return flows
    
    def _extract_rules(self, content: str) -> Dict[str, Rule]:
        """Extract business rules from markdown"""
        rules = {}
        
        # Find rules section
        rules_section = re.search(r'##\s+业务规则\s*\n(.*?)(?=##|$)', content, re.DOTALL)
        if rules_section:
            rules_content = rules_section.group(1)
            
            # Parse individual rules
            rule_pattern = r'\d+\.\s*\*\*(.+?)\*\*[：:]\s*\n\s*-\s*(.+)'
            
            for match in re.finditer(rule_pattern, rules_content):
                rule_name = match.group(1).strip()
                rule_desc = match.group(2).strip()
                
                rules[rule_name] = Rule(
                    name=rule_name,
                    description=rule_desc,
                    condition="",
                    action=""
                )
        
        return rules
    
    def _parse_attributes(self, content: str) -> List[Attribute]:
        """Parse attributes from entity content"""
        attributes = []
        
        # Find attributes section
        attr_section = re.search(r'\*\*属性\*\*[：:]\s*\n(.*?)(?=\*\*|$)', content, re.DOTALL)
        if attr_section:
            attr_content = attr_section.group(1)
            
            # Parse each attribute line
            attr_pattern = r'-\s*(.+?)[：:]\s*(.+)'
            
            for match in re.finditer(attr_pattern, attr_content):
                attr_name = match.group(1).strip()
                attr_desc = match.group(2).strip()
                
                # Infer type from description
                attr_type = self._infer_attribute_type(attr_name, attr_desc)
                
                # Convert Chinese name to English
                attr_name_en = self._convert_to_english_name(attr_name)
                
                attributes.append(Attribute(
                    name=attr_name_en,
                    type=attr_type,
                    description=attr_desc
                ))
        
        return attributes
    
    def _parse_methods(self, content: str) -> List[Method]:
        """Parse methods from service content"""
        methods = []
        
        # Find methods section
        method_section = re.search(r'\*\*方法\*\*[：:]\s*\n(.*?)(?=\*\*|$)', content, re.DOTALL)
        if method_section:
            method_content = method_section.group(1)
            
            # Parse each method line
            method_pattern = r'-\s*`(.+?)\((.+?)\)`\s*(?:⚡\s*可调试\s*)?-\s*(.+)'
            
            for match in re.finditer(method_pattern, method_content):
                method_name = match.group(1).strip()
                method_params = match.group(2).strip()
                method_desc = match.group(3).strip()
                
                # Convert to English names
                method_name_en = self._convert_to_english_name(method_name)
                
                methods.append(Method(
                    name=method_name_en,
                    description=method_desc,
                    parameters={"input": method_params}
                ))
        
        return methods
    
    def _parse_constraints(self, content: str) -> List[str]:
        """Parse constraints from content"""
        constraints = []
        
        # Find constraints in business rules
        constraint_pattern = r'-\s*(.+必须.+)'
        
        for match in re.finditer(constraint_pattern, content):
            constraints.append(match.group(1).strip())
        
        return constraints
    
    def _parse_mermaid_steps(self, diagram: str) -> List[Dict[str, Any]]:
        """Parse steps from mermaid flowchart"""
        steps = []
        
        # Extract nodes
        node_pattern = r'(\w+)\[(.*?)\]'
        nodes = {}
        
        for match in re.finditer(node_pattern, diagram):
            node_id = match.group(1)
            node_label = match.group(2)
            nodes[node_id] = {
                "id": node_id,
                "label": node_label,
                "type": "process"
            }
        
        # Extract decision nodes
        decision_pattern = r'(\w+)\{(.*?)\}'
        for match in re.finditer(decision_pattern, diagram):
            node_id = match.group(1)
            node_label = match.group(2)
            nodes[node_id] = {
                "id": node_id,
                "label": node_label,
                "type": "decision"
            }
        
        # Convert to steps list
        for node in nodes.values():
            steps.append(node)
        
        return steps
    
    def _infer_attribute_type(self, name: str, description: str) -> AttributeType:
        """Infer attribute type from name and description"""
        # Check for common patterns
        if any(word in name for word in ['时间', 'time', 'date', '日期']):
            return AttributeType.DATETIME
        elif any(word in name for word in ['数量', 'count', 'number', '数', '量']):
            return AttributeType.INTEGER
        elif any(word in name for word in ['金额', 'price', 'amount', '价']):
            return AttributeType.FLOAT
        elif any(word in name for word in ['状态', 'status', 'state']):
            return AttributeType.ENUM
        elif any(word in name for word in ['是否', 'is', 'has']):
            return AttributeType.BOOLEAN
        else:
            return AttributeType.STRING
    
    def _convert_to_english_name(self, chinese_name: str) -> str:
        """Convert Chinese name to English (simple mapping)"""
        # Common mappings
        mappings = {
            '标识符': 'id',
            '姓名': 'name',
            '名称': 'name',
            '邮箱': 'email',
            '电话': 'phone',
            '状态': 'status',
            '创建时间': 'created_at',
            '更新时间': 'updated_at',
            '创建用户': 'createUser',
            '查询用户': 'queryUser',
            '更新用户': 'updateUser',
            '删除用户': 'deleteUser',
            '注册用户': 'registerUser'
        }
        
        return mappings.get(chinese_name, chinese_name)