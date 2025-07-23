"""Rule engine for executing business rules"""

from typing import Dict, Any, Optional, List
import re
import operator
from datetime import datetime

from core.models import Rule
from utils.logger import setup_logger


class RuleEngine:
    """Execute business rules defined in natural language"""
    
    def __init__(self, llm_client=None):
        self.logger = setup_logger(__name__)
        self.llm_client = llm_client
        self.rules: Dict[str, Rule] = {}
        self.compiled_rules: Dict[str, Any] = {}
        
        # Basic operators for simple rule evaluation
        self.operators = {
            '=': operator.eq,
            '==': operator.eq,
            '!=': operator.ne,
            '>': operator.gt,
            '>=': operator.ge,
            '<': operator.lt,
            '<=': operator.le,
            'in': lambda x, y: x in y,
            'not in': lambda x, y: x not in y,
            'contains': lambda x, y: y in x,
            'startswith': lambda x, y: x.startswith(y),
            'endswith': lambda x, y: x.endswith(y)
        }
    
    async def load_rules(self, rules: Dict[str, Rule]):
        """Load rules into the engine"""
        self.rules = rules
        
        # Pre-compile simple rules
        for name, rule in rules.items():
            try:
                compiled = self._compile_simple_rule(rule)
                if compiled:
                    self.compiled_rules[name] = compiled
            except Exception as e:
                self.logger.warning(f"Could not compile rule '{name}': {e}")
        
        self.logger.info(f"Loaded {len(rules)} rules, compiled {len(self.compiled_rules)}")
    
    async def execute_rule(
        self,
        rule_name: str,
        context: Dict[str, Any]
    ) -> Any:
        """Execute a named rule"""
        if rule_name not in self.rules:
            raise ValueError(f"Rule '{rule_name}' not found")
        
        rule = self.rules[rule_name]
        
        # Try compiled version first
        if rule_name in self.compiled_rules:
            try:
                return self._execute_compiled_rule(
                    self.compiled_rules[rule_name],
                    context
                )
            except Exception as e:
                self.logger.warning(f"Compiled rule failed, falling back: {e}")
        
        # Fall back to interpretation
        return await self._interpret_rule(rule, context)
    
    async def evaluate_condition(
        self,
        condition: str,
        context: Dict[str, Any]
    ) -> bool:
        """Evaluate a condition string"""
        # Simple pattern matching for common conditions
        
        # Pattern: "field operator value"
        pattern = r'(\w+(?:\.\w+)*)\s*(==|!=|>|>=|<|<=|=)\s*(.+)'
        match = re.match(pattern, condition.strip())
        
        if match:
            field_path = match.group(1)
            operator_str = match.group(2)
            value_str = match.group(3).strip('"\'')
            
            # Get field value from context
            field_value = self._get_nested_value(context, field_path)
            
            # Convert value string to appropriate type
            value = self._parse_value(value_str, field_value)
            
            # Apply operator
            if operator_str in self.operators:
                return self.operators[operator_str](field_value, value)
        
        # Default to false for unparseable conditions
        self.logger.warning(f"Could not parse condition: {condition}")
        return False
    
    def _compile_simple_rule(self, rule: Rule) -> Optional[Dict[str, Any]]:
        """Compile a simple rule for faster execution"""
        # This is a simplified compiler for demonstration
        # In production, you would have more sophisticated parsing
        
        if not rule.description:
            return None
        
        # Pattern: "if X then Y"
        if_then_pattern = r'[如若]果?\s*(.+?)[则就那]\s*(.+)'
        match = re.search(if_then_pattern, rule.description)
        
        if match:
            return {
                'type': 'if_then',
                'condition': match.group(1).strip(),
                'action': match.group(2).strip()
            }
        
        # Pattern: "X must be Y"
        must_pattern = r'(.+?)必须\s*(.+)'
        match = re.search(must_pattern, rule.description)
        
        if match:
            return {
                'type': 'must',
                'subject': match.group(1).strip(),
                'requirement': match.group(2).strip()
            }
        
        return None
    
    def _execute_compiled_rule(
        self,
        compiled_rule: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Any:
        """Execute a pre-compiled rule"""
        rule_type = compiled_rule['type']
        
        if rule_type == 'if_then':
            # Evaluate condition
            condition_met = self._evaluate_simple_condition(
                compiled_rule['condition'],
                context
            )
            
            if condition_met:
                return self._execute_action(compiled_rule['action'], context)
            
            return None
        
        elif rule_type == 'must':
            # Validation rule
            subject = compiled_rule['subject']
            requirement = compiled_rule['requirement']
            
            # Simple validation logic
            if '唯一' in requirement:
                return {'type': 'unique_check', 'field': subject}
            elif '不为空' in requirement or '必填' in requirement:
                return {'type': 'required_check', 'field': subject}
            elif '格式' in requirement:
                return {'type': 'format_check', 'field': subject}
        
        return None
    
    async def _interpret_rule(
        self,
        rule: Rule,
        context: Dict[str, Any]
    ) -> Any:
        """Interpret a rule using LLM or pattern matching"""
        # If LLM is available, use it for complex rules
        if self.llm_client:
            return await self._llm_interpret_rule(rule, context)
        
        # Otherwise, use simple pattern matching
        return self._pattern_interpret_rule(rule, context)
    
    def _pattern_interpret_rule(
        self,
        rule: Rule,
        context: Dict[str, Any]
    ) -> Any:
        """Interpret rule using pattern matching"""
        description = rule.description.lower() if rule.description else ""
        
        # Common business rule patterns
        if '折扣' in description or 'discount' in description:
            # Extract discount rules
            if '金牌' in description or 'gold' in description:
                return 0.9  # 10% discount
            elif '银牌' in description or 'silver' in description:
                return 0.95  # 5% discount
        
        elif '验证' in description or 'validate' in description:
            # Validation rules
            if '邮箱' in description or 'email' in description:
                return {'validate': 'email'}
            elif '电话' in description or 'phone' in description:
                return {'validate': 'phone'}
        
        elif '限制' in description or 'limit' in description:
            # Rate limiting rules
            numbers = re.findall(r'\d+', description)
            if numbers:
                return {'limit': int(numbers[0])}
        
        # Default: return the rule description for logging
        return {'rule': rule.description}
    
    async def _llm_interpret_rule(
        self,
        rule: Rule,
        context: Dict[str, Any]
    ) -> Any:
        """Use LLM to interpret complex rules"""
        # This would call the LLM API to interpret the rule
        # For now, return a placeholder
        return {'llm_interpretation': rule.description, 'context': context}
    
    def _evaluate_simple_condition(
        self,
        condition: str,
        context: Dict[str, Any]
    ) -> bool:
        """Evaluate a simple condition"""
        # Handle Chinese conditions
        condition_lower = condition.lower()
        
        # User level checks
        if '会员等级' in condition or 'vip' in condition:
            user = context.get('user', {})
            level = user.get('level', '').lower()
            
            if '金牌' in condition or 'gold' in condition:
                return level == 'gold' or level == '金牌'
            elif '银牌' in condition or 'silver' in condition:
                return level == 'silver' or level == '银牌'
        
        # Amount checks
        if '金额' in condition or 'amount' in condition:
            amount = context.get('amount', 0)
            
            # Extract comparison
            if '大于' in condition or '>' in condition:
                numbers = re.findall(r'\d+', condition)
                if numbers:
                    return amount > float(numbers[0])
            elif '小于' in condition or '<' in condition:
                numbers = re.findall(r'\d+', condition)
                if numbers:
                    return amount < float(numbers[0])
        
        return False
    
    def _execute_action(self, action: str, context: Dict[str, Any]) -> Any:
        """Execute an action"""
        action_lower = action.lower()
        
        # Discount actions
        if '折' in action or 'discount' in action:
            # Extract discount percentage
            numbers = re.findall(r'\d+', action)
            if numbers:
                discount = float(numbers[0])
                if discount > 1:  # Percentage form (e.g., 90 for 90%)
                    return discount / 100
                else:  # Decimal form (e.g., 0.9)
                    return discount
        
        # Status change actions
        elif '状态' in action or 'status' in action:
            if '活跃' in action or 'active' in action:
                return {'set_status': 'active'}
            elif '停用' in action or 'inactive' in action:
                return {'set_status': 'inactive'}
        
        # Default action
        return {'action': action}
    
    def _get_nested_value(self, obj: Dict[str, Any], path: str) -> Any:
        """Get nested value from object using dot notation"""
        parts = path.split('.')
        current = obj
        
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None
        
        return current
    
    def _parse_value(self, value_str: str, reference_value: Any) -> Any:
        """Parse value string to appropriate type"""
        # If reference value is available, use its type
        if reference_value is not None:
            value_type = type(reference_value)
            
            try:
                if value_type == int:
                    return int(value_str)
                elif value_type == float:
                    return float(value_str)
                elif value_type == bool:
                    return value_str.lower() in ['true', '1', 'yes', '是', '真']
            except ValueError:
                pass
        
        # Try to infer type
        if value_str.lower() in ['true', 'false', '真', '假', '是', '否']:
            return value_str.lower() in ['true', '真', '是']
        
        try:
            # Try integer
            return int(value_str)
        except ValueError:
            try:
                # Try float
                return float(value_str)
            except ValueError:
                # Return as string
                return value_str