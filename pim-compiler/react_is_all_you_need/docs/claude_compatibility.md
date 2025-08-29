# Claude API Compatibility for React Agent Minimal

## Problem
The React Agent Minimal framework uses OpenAI's tool calling format, which is incompatible with Claude's API. This causes the error:
```
unexpected `tool_use_id` found in `tool_result` blocks
```

## Solution
Created `ReactAgentClaude` class that extends `ReactAgentMinimal` with Claude-specific message format conversion.

## Key Differences

### OpenAI Format
```python
# Tool call in assistant message
{
    "role": "assistant",
    "tool_calls": [{
        "id": "call_123",
        "type": "function",
        "function": {
            "name": "tool_name",
            "arguments": "{...}"
        }
    }]
}

# Tool result in separate message
{
    "role": "tool",
    "tool_call_id": "call_123",
    "content": "result"
}
```

### Claude Format
```python
# Tool use in assistant message content
{
    "role": "assistant",
    "content": [{
        "type": "tool_use",
        "id": "toolu_123",
        "name": "tool_name",
        "input": {...}
    }]
}

# Tool result in user message content
{
    "role": "user",
    "content": [{
        "type": "tool_result",
        "tool_use_id": "toolu_123",
        "content": "result"
    }]
}
```

## Usage

### Quick Start
```python
from core.react_agent_claude import create_claude_agent

# Create Claude-compatible agent
agent = create_claude_agent(
    work_dir="my_project",
    model="claude-3-5-sonnet-20241022",
    knowledge_files=["knowledge/debug_knowledge.md"],
    window_size=30,
    max_rounds=100
)

# Run task
result = agent.run("Debug the FastAPI application")
```

### Manual Configuration
```python
from core.react_agent_claude import ReactAgentClaude

agent = ReactAgentClaude(
    work_dir="my_project",
    model="claude-3-5-sonnet-20241022",
    base_url="https://api.anthropic.com/v1",
    api_key=os.getenv("ANTHROPIC_API_KEY"),
    knowledge_files=["knowledge/debug_knowledge.md"]
)
```

## Supported Claude Models
- `claude-3-5-sonnet-20241022` (Claude Sonnet 4)
- `claude-3-opus-20240229`
- `claude-3-haiku-20240307`
- Any model with "claude", "sonnet", "opus", or "haiku" in the name

## Auto-Detection
The system automatically detects Claude models based on:
1. Model name containing Claude keywords
2. Base URL containing "anthropic"

## Features
- Automatic message format conversion
- Transparent API compatibility
- Preserves all React Agent Minimal functionality
- No changes needed to existing tools or knowledge files

## Environment Setup
```bash
# Set API key
export ANTHROPIC_API_KEY=your_api_key

# Optional: Set proxy if needed
export HTTP_PROXY=http://127.0.0.1:7890
export HTTPS_PROXY=http://127.0.0.1:7890
```

## Performance Comparison

| Model | Speed | Accuracy | Context Window |
|-------|--------|----------|----------------|
| Claude Sonnet 4 | Fast | High | 200k tokens |
| Gemini 2.5 Flash | Fastest | Good | 1M tokens |
| DeepSeek Chat | Moderate | Good | 128k tokens |

## Troubleshooting

### API Key Not Found
```bash
export ANTHROPIC_API_KEY=your_api_key
```

### Rate Limiting
The system automatically retries with exponential backoff.

### Tool Format Errors
Ensure you're using `ReactAgentClaude` instead of `ReactAgentMinimal` for Claude models.

## Implementation Details
The compatibility layer:
1. Detects Claude model usage
2. Converts messages before API calls
3. Converts responses back to standard format
4. Handles tool definitions in Claude format

This ensures seamless integration with existing React Agent Minimal tools and workflows.