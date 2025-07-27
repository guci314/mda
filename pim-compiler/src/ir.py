# PIM Compiler Intermediate Representation

class IRNode:
    """Base class for all IR nodes"""
    def __init__(self):
        self.metadata = {}

    def accept(self, visitor):
        """Visitor pattern support"""
        raise NotImplementedError

class ModuleIR(IRNode):
    """Top-level module representation"""
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.functions = []

    def accept(self, visitor):
        return visitor.visit_module(self)

class FunctionIR(IRNode):
    """Function representation"""
    def __init__(self, name, params, body):
        super().__init__()
        self.name = name
        self.params = params
        self.body = body

    def accept(self, visitor):
        return visitor.visit_function(self)

# Add more IR node types as needed

class IRTransformer:
    """Base class for IR transformations"""
    def transform(self, node):
        return node.accept(self)

    def visit_module(self, node):
        # Default implementation
        return node

    def visit_function(self, node):
        # Default implementation
        return node
