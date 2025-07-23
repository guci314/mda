"""Convert PIM models to LLM prompts"""

from typing import List, Dict, Any, Optional
from core.models import PIMModel, Entity, Service, Method, Flow, Rule, Attribute


class PIMToPromptConverter:
    """Convert PIM models to structured prompts for LLM code generation"""
    
    def convert_model_context(self, model: PIMModel) -> str:
        """Convert entire PIM model to context description"""
        parts = [
            f"# {model.domain} System",
            f"\n{model.description or 'Business system implementation'}",
            "\n## Business Entities\n",
            self.convert_entities(model.entities),
            "\n## Business Services\n",
            self.convert_services(model.services),
        ]
        
        if model.rules:
            parts.extend([
                "\n## Business Rules\n",
                self.convert_rules(list(model.rules.values()))
            ])
            
        return "\n".join(parts)
    
    def convert_entities(self, entities: List[Entity]) -> str:
        """Convert entities to natural language description"""
        descriptions = []
        
        for entity in entities:
            desc = [f"### {entity.name}"]
            if entity.description:
                desc.append(f"{entity.description}")
            
            desc.append("\nAttributes:")
            for attr in entity.attributes:
                attr_desc = f"- {attr.name}: {attr.type.value}"
                if attr.required:
                    attr_desc += " (required)"
                if attr.unique:
                    attr_desc += " (unique)"
                if attr.description:
                    attr_desc += f" - {attr.description}"
                desc.append(attr_desc)
            
            if entity.constraints:
                desc.append("\nConstraints:")
                for constraint in entity.constraints:
                    desc.append(f"- {constraint}")
                    
            descriptions.append("\n".join(desc))
            
        return "\n\n".join(descriptions)
    
    def convert_services(self, services: List[Service]) -> str:
        """Convert services to natural language description"""
        descriptions = []
        
        for service in services:
            desc = [f"### {service.name}"]
            if service.description:
                desc.append(f"{service.description}")
                
            desc.append("\nMethods:")
            for method in service.methods:
                method_desc = f"- {method.name}"
                if method.description:
                    method_desc += f": {method.description}"
                desc.append(method_desc)
                
                if method.parameters:
                    desc.append("  Parameters:")
                    for param_name, param_type in method.parameters.items():
                        desc.append(f"    - {param_name}: {param_type}")
                        
                if method.rules:
                    desc.append("  Business Rules:")
                    for rule in method.rules:
                        desc.append(f"    - {rule}")
                        
            descriptions.append("\n".join(desc))
            
        return "\n\n".join(descriptions)
    
    def convert_flow(self, flow: Flow) -> str:
        """Convert flow diagram to step-by-step description"""
        if not flow:
            return ""
            
        lines = [
            f"## Process Flow: {flow.name}",
            f"{flow.description or 'Business process flow'}",
            "\n### Steps:"
        ]
        
        # Convert Mermaid diagram to textual steps
        if flow.diagram:
            steps = self._parse_mermaid_to_steps(flow.diagram)
            for i, step in enumerate(steps, 1):
                lines.append(f"{i}. {step}")
        
        # Add detailed step information if available
        if hasattr(flow, 'steps') and flow.steps:
            lines.append("\n### Detailed Steps:")
            for step in flow.steps:
                step_desc = f"- {step.get('label', step.get('id', 'Step'))}"
                if step.get('type') == 'decision':
                    step_desc += " (Decision Point)"
                if step.get('action'):
                    step_desc += f": {step['action']}"
                lines.append(step_desc)
                
        return "\n".join(lines)
    
    def convert_rules(self, rules: List[Rule]) -> str:
        """Convert business rules to constraints"""
        if not rules:
            return ""
            
        lines = []
        for rule in rules:
            rule_desc = f"- **{rule.name}**: {rule.description}"
            if hasattr(rule, 'condition') and rule.condition:
                rule_desc += f"\n  Condition: {rule.condition}"
            if hasattr(rule, 'action') and rule.action:
                rule_desc += f"\n  Action: {rule.action}"
            lines.append(rule_desc)
            
        return "\n".join(lines)
    
    def convert_method_to_prompt(
        self, 
        method: Method,
        service: Service,
        model: PIMModel
    ) -> str:
        """Convert a specific method to a detailed implementation prompt"""
        
        # Find the flow for this method
        flow = None
        if method.flow and method.flow in model.flows:
            flow = model.flows[method.flow]
            
        # Find the rules for this method
        method_rules = []
        if method.rules:
            for rule_name in method.rules:
                if rule_name in model.rules:
                    method_rules.append(model.rules[rule_name])
        
        prompt_parts = [
            f"Implement the {method.name} method for {service.name}.",
            f"\nMethod Description: {method.description or 'Business logic implementation'}",
        ]
        
        # Add parameters
        if method.parameters:
            prompt_parts.append("\nMethod Parameters:")
            for param_name, param_type in method.parameters.items():
                prompt_parts.append(f"- {param_name}: {param_type}")
        
        # Add return type
        if method.return_type:
            prompt_parts.append(f"\nReturn Type: {method.return_type}")
        
        # Add flow information
        if flow:
            prompt_parts.append(f"\n{self.convert_flow(flow)}")
        
        # Add applicable rules
        if method_rules:
            prompt_parts.append("\n## Applicable Business Rules:")
            prompt_parts.append(self.convert_rules(method_rules))
        
        # Add implementation requirements
        prompt_parts.extend([
            "\n## Implementation Requirements:",
            "1. Implement all business logic according to the flow",
            "2. Validate all inputs according to business rules",
            "3. Handle all error cases with appropriate HTTP status codes",
            "4. Include logging for important operations",
            "5. Use database transactions where appropriate",
            "6. Follow async/await patterns",
            "7. Add comprehensive docstrings"
        ])
        
        return "\n".join(prompt_parts)
    
    def _parse_mermaid_to_steps(self, diagram: str) -> List[str]:
        """Parse Mermaid flowchart to extract steps"""
        steps = []
        lines = diagram.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            # Skip mermaid keywords and empty lines
            if not line or line.startswith('flowchart') or line.startswith('graph'):
                continue
                
            # Extract step descriptions from Mermaid syntax
            # Handle: A[Description] or A(Description) or A{Description}
            import re
            
            # Pattern for node definitions
            node_pattern = r'(\w+)\[(.*?)\]|\w+\((.*?)\)|\w+\{(.*?)\}'
            matches = re.findall(node_pattern, line)
            
            for match in matches:
                # Get the description from whichever group matched
                desc = next((g for g in match if g and g not in ['Start', 'End']), None)
                if desc:
                    steps.append(desc)
            
            # Pattern for edge labels
            edge_pattern = r'-->\|(.*?)\|'
            edge_matches = re.findall(edge_pattern, line)
            for label in edge_matches:
                if label not in ['Valid', 'Invalid', 'Yes', 'No', 'Success', 'Error']:
                    steps.append(f"Decision: {label}")
                    
        return steps
    
    def create_few_shot_examples(self, target_framework: str = "fastapi") -> List[Dict[str, str]]:
        """Create few-shot examples for better code generation"""
        
        if target_framework == "fastapi":
            return [
                {
                    "title": "User Authentication Method",
                    "input": """
Method: authenticateUser
Parameters: email: string, password: string
Rules: 
- Validate email format
- Check user exists and is active
- Verify password hash
Return: AuthToken or error
                    """,
                    "output": """
async def authenticateUser(self, email: str, password: str) -> AuthTokenResponse:
    \"\"\"Authenticate user and return JWT token\"\"\"
    
    # Validate email format
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        raise HTTPException(
            status_code=400,
            detail="Invalid email format"
        )
    
    # Check user exists
    user = self.db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )
    
    # Check user is active
    if user.status != 'active':
        raise HTTPException(
            status_code=403,
            detail="Account is not active"
        )
    
    # Verify password
    if not bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )
    
    # Generate JWT token
    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    
    access_token = jwt.encode(token_data, settings.SECRET_KEY, algorithm="HS256")
    
    logger.info(f"User authenticated successfully: {email}")
    
    return AuthTokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=86400
    )
                    """
                }
            ]
        
        return []