# UML Model Documentation

## Overview

This directory contains the UML models extracted from the `core` module of the React Agent system. The models are expressed using Markdown with embedded Mermaid diagrams for easy visualization and modification.

## Model Structure

### 1. [Class Diagram](./class_diagram.md)
The class diagram provides a static view of the system architecture, showing:
- **Class hierarchies**: Base classes and their implementations
- **Relationships**: Inheritance, composition, and dependencies
- **Attributes and methods**: Key properties and operations of each class
- **Design patterns**: Strategy, Adapter, Factory, and Composition patterns

Key components visualized:
- Agent hierarchy (BaseAgent → ReactAgent, ReactAgentMinimal, etc.)
- Memory systems (Natural Decay, Three-tier, NLPL)
- Tool system and input models
- API integration layers

### 2. [Interaction Diagrams](./interaction_diagram.md)
The interaction diagrams show dynamic behavior through sequence diagrams:
- **Task execution flow**: How agents process tasks
- **Memory compression**: Natural decay compression cycles
- **Tool execution**: Validation and execution pipeline
- **API configuration**: Service detection and setup
- **Hook system**: Message interception and modification

Additional diagrams include:
- State transitions for memory and agent execution
- Performance characteristics and optimization strategies

## How to Use These Models

### For Understanding
1. Start with the class diagram to understand the system structure
2. Review interaction diagrams to see how components work together
3. Use state diagrams to understand component lifecycles

### For Modification (Human-AI Collaborative Breathing)

Following the Compress-Process-Decompress paradigm:

#### Step 1: AI Compression (Current State)
The current UML models represent the compressed form of the codebase:
- 15 Python files → 2 comprehensive UML documents
- ~3000 lines of code → ~100 classes and relationships
- Complex interactions → 8 clear sequence diagrams

#### Step 2: Human Processing (Your Turn)
Modify the UML models to improve the architecture:
```markdown
Examples of modifications:
- Add new classes or relationships
- Refactor existing hierarchies
- Introduce new design patterns
- Optimize interaction flows
- Add new tool types
- Enhance memory strategies
```

#### Step 3: AI Decompression (Future Implementation)
Feed the modified UML back to an AI agent to generate updated code:
```python
# Example usage (future)
agent = ReactAgent(work_dir="./")
result = agent.run("""
Based on the modified UML diagrams in uml_model/:
1. Generate updated Python code implementing the changes
2. Ensure backward compatibility where specified
3. Add appropriate tests for new functionality
4. Update documentation
""")
```

## Model Notation

### Mermaid Class Diagram Syntax
- `<<abstract>>`: Abstract classes
- `+`: Public members
- `#`: Protected members
- `-`: Private members
- `*`: Abstract methods
- `$`: Static methods
- `-->`: Association
- `<|--`: Inheritance
- `..>`: Dependency

### Mermaid Sequence Diagram Syntax
- `participant`: Define actors
- `->>/-->>`: Synchronous/asynchronous calls
- `alt/else`: Conditional flows
- `loop`: Iterative processes
- `par`: Parallel execution
- `opt`: Optional sequences

## Viewing the Diagrams

### Option 1: GitHub/GitLab
The Mermaid diagrams will render automatically when viewing the .md files on GitHub or GitLab.

### Option 2: VS Code
Install the "Markdown Preview Mermaid Support" extension to view diagrams in VS Code.

### Option 3: Online Viewer
Copy the Mermaid code blocks to [Mermaid Live Editor](https://mermaid.live/) for interactive viewing and editing.

### Option 4: Generate Images
Use the Mermaid CLI to generate PNG/SVG files:
```bash
npm install -g @mermaid-js/mermaid-cli
mmdc -i class_diagram.md -o class_diagram.png
```

## Architecture Insights

### Memory Philosophy
The system offers two memory paradigms:
1. **Natural Decay** (Minimal): Compression-based, mimics human forgetting
2. **Cognitive Integration** (Full): Multi-tier with event-based memories

### Tool System
- Strongly typed with Pydantic models
- Comprehensive coverage of development tasks
- Extensible for custom tools

### API Flexibility
- Multi-provider support (OpenRouter, DeepSeek, Moonshot, Gemini)
- Automatic configuration based on environment
- Context size auto-detection

## Future Enhancements

Potential areas for architecture improvement:
1. **Plugin System**: Dynamic tool loading
2. **Distributed Memory**: Multi-agent shared memory
3. **Streaming Support**: Real-time response streaming
4. **Visualization Layer**: Built-in debugging UI
5. **Performance Monitoring**: Metrics and profiling

## Contributing

When modifying the UML models:
1. Maintain consistency between class and interaction diagrams
2. Document significant changes in comments
3. Ensure Mermaid syntax validity
4. Consider backward compatibility impacts
5. Update this README if adding new diagram types

## References

- [Mermaid Documentation](https://mermaid-js.github.io/)
- [UML Best Practices](https://www.uml-diagrams.org/)
- [Human-AI Collaborative Breathing Paper](../docs/human_ai_collaborative_breathing.md)