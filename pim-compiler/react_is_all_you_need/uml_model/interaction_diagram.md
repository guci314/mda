# Core Module Interaction Diagrams

## Overview
These interaction diagrams show the dynamic behavior of the React Agent system, illustrating how components interact during task execution, memory management, and tool usage.

## 1. Task Execution Flow

```mermaid
sequenceDiagram
    participant User
    participant ReactAgent
    participant Memory
    participant LLM
    participant Tool
    participant FileSystem

    User->>ReactAgent: run(task)
    ReactAgent->>ReactAgent: _load_knowledge()
    ReactAgent->>Memory: get_context_messages()
    Memory-->>ReactAgent: context_messages
    
    loop Until task complete or max_rounds
        ReactAgent->>LLM: _call_llm(messages, tools)
        LLM-->>ReactAgent: response with tool_calls
        
        alt Tool Call Required
            ReactAgent->>Tool: _execute_tool(tool_name, args)
            Tool->>FileSystem: perform_operation()
            FileSystem-->>Tool: result
            Tool-->>ReactAgent: tool_result
            ReactAgent->>Memory: add_message("tool", result)
        else Direct Response
            ReactAgent->>Memory: add_message("assistant", content)
        end
        
        ReactAgent->>ReactAgent: check_completion()
    end
    
    ReactAgent->>Memory: save_checkpoint()
    ReactAgent-->>User: final_result
```

## 2. Memory Compression Flow (Natural Decay)

```mermaid
sequenceDiagram
    participant Agent
    participant MemoryWithNaturalDecay as Memory
    participant CompressedMemory
    participant FileSystem

    Agent->>Memory: add_message(role, content)
    Memory->>Memory: messages.append(message)
    Memory->>Memory: should_compact()
    
    alt Pressure Threshold Exceeded
        Memory->>Memory: compact()
        Memory->>Memory: _extract_key_points(messages)
        Memory->>Memory: _extract_task_results(messages)
        Memory->>Memory: _generate_summary(messages)
        Memory->>CompressedMemory: create(summary, key_points, task_results)
        CompressedMemory-->>Memory: compressed_unit
        Memory->>Memory: compressed_history.append(compressed_unit)
        Memory->>Memory: clear_window(keep_context=true)
        
        alt Persistence Enabled
            Memory->>FileSystem: save_compressed_history()
            FileSystem-->>Memory: saved
        end
    end
    
    Memory-->>Agent: ready_for_next
```

## 3. Cognitive Memory Integration Flow

```mermaid
sequenceDiagram
    participant Agent
    participant CognitiveMemory as CMI
    participant SimpleMemoryManager as SMM
    participant NLPLMemorySystem as NLPL
    participant FileSystem

    Agent->>CMI: add_interaction(role, content, metadata)
    
    par Parallel Memory Updates
        CMI->>SMM: add_interaction(role, content, metadata)
        SMM->>SMM: update_short_term_memory()
        SMM->>SMM: check_transfer_to_long_term()
    and
        CMI->>NLPL: add_event(event_type, content, metadata)
        NLPL->>NLPL: calculate_importance()
        NLPL->>NLPL: update_events()
    end
    
    Agent->>CMI: get_context()
    CMI->>SMM: get_context_messages()
    SMM-->>CMI: structured_messages
    CMI->>NLPL: get_relevant_memories(query)
    NLPL->>NLPL: _compute_relevance(events, query)
    NLPL-->>CMI: relevant_events
    CMI->>CMI: merge_contexts(structured, events)
    CMI-->>Agent: combined_context
    
    Agent->>CMI: save_all()
    par Parallel Saves
        CMI->>SMM: save_checkpoint()
        SMM->>FileSystem: write_memory_files()
    and
        CMI->>NLPL: save()
        NLPL->>FileSystem: write_event_files()
    end
```

## 4. Tool Execution Flow

```mermaid
sequenceDiagram
    participant ReactAgent
    participant LLM
    participant ToolExecutor
    participant FileInput
    participant FileSystem
    participant ErrorHandler

    ReactAgent->>LLM: request_with_tools(task, available_tools)
    LLM-->>ReactAgent: tool_call(name="write_file", args)
    
    ReactAgent->>ReactAgent: _execute_tool("write_file", args)
    ReactAgent->>FileInput: validate(args)
    
    alt Validation Success
        FileInput-->>ReactAgent: validated_input
        ReactAgent->>ToolExecutor: execute_write_file(file_path, content)
        ToolExecutor->>FileSystem: write(path, content)
        
        alt Write Success
            FileSystem-->>ToolExecutor: success
            ToolExecutor-->>ReactAgent: "File written successfully"
        else Write Failure
            FileSystem-->>ToolExecutor: error
            ToolExecutor->>ErrorHandler: handle_error(error)
            ErrorHandler-->>ReactAgent: error_message
        end
    else Validation Failure
        FileInput-->>ReactAgent: validation_error
        ReactAgent->>ErrorHandler: handle_validation_error(error)
        ErrorHandler-->>ReactAgent: error_message
    end
    
    ReactAgent->>LLM: tool_result(result_or_error)
```

## 5. Agent as Tool (LangChain Integration)

```mermaid
sequenceDiagram
    participant LangChain
    participant GenericAgentTool
    participant AgentToolWrapper
    participant ReactAgent
    participant TeeOutput
    participant LogFile

    LangChain->>GenericAgentTool: _run(task_description, context)
    GenericAgentTool->>AgentToolWrapper: execute(task)
    
    AgentToolWrapper->>TeeOutput: redirect_output()
    TeeOutput->>LogFile: create_log()
    
    AgentToolWrapper->>ReactAgent: run(task)
    
    loop Task Execution
        ReactAgent->>ReactAgent: process_task()
        ReactAgent->>TeeOutput: write(output)
        TeeOutput->>TeeOutput: split_output()
        par Output Handling
            TeeOutput->>LogFile: write(output)
        and
            TeeOutput->>AgentToolWrapper: capture(output)
        end
    end
    
    ReactAgent-->>AgentToolWrapper: result
    AgentToolWrapper->>TeeOutput: restore_output()
    AgentToolWrapper-->>GenericAgentTool: formatted_result
    GenericAgentTool-->>LangChain: tool_response
```

## 6. API Service Detection and Configuration

```mermaid
sequenceDiagram
    participant User
    participant ReactAgent
    participant ConfigDetector
    participant Environment
    participant APIClient

    User->>ReactAgent: __init__(model, api_key, base_url)
    
    ReactAgent->>ConfigDetector: _detect_service()
    
    alt API Key Provided
        ConfigDetector->>ConfigDetector: check_api_key_type()
    else No API Key
        ConfigDetector->>Environment: get_env_vars()
        Environment-->>ConfigDetector: available_keys
        ConfigDetector->>ConfigDetector: select_first_available()
    end
    
    alt Base URL Provided
        ConfigDetector-->>ReactAgent: use_provided_url
    else Auto Detect
        ConfigDetector->>ConfigDetector: _detect_base_url_for_key()
        alt DeepSeek Key
            ConfigDetector-->>ReactAgent: "https://api.deepseek.com/v1"
        else Moonshot Key
            ConfigDetector-->>ReactAgent: "https://api.moonshot.cn/v1"
        else OpenRouter Key
            ConfigDetector-->>ReactAgent: "https://openrouter.ai/api/v1"
        else Gemini Key
            ConfigDetector-->>ReactAgent: "https://generativelanguage.googleapis.com/v1beta/openai/"
        end
    end
    
    ReactAgent->>ConfigDetector: _detect_context_size(model)
    ConfigDetector-->>ReactAgent: context_size
    
    ReactAgent->>APIClient: initialize(base_url, api_key, model)
    APIClient-->>ReactAgent: client_ready
```

## 7. Minimal vs Full Agent Initialization

```mermaid
sequenceDiagram
    participant User
    participant ReactAgentMinimal
    participant ReactAgent
    participant MemoryWithNaturalDecay
    participant MemoryManagerAdapter
    participant CognitiveMemoryIntegration

    alt Minimal Agent
        User->>ReactAgentMinimal: __init__(pressure_threshold=50)
        ReactAgentMinimal->>MemoryWithNaturalDecay: __init__(pressure_threshold)
        MemoryWithNaturalDecay-->>ReactAgentMinimal: memory_ready
        ReactAgentMinimal->>ReactAgentMinimal: _define_tools()
        ReactAgentMinimal-->>User: agent_ready (600 lines)
    else Full Agent
        User->>ReactAgent: __init__(window_size=50)
        ReactAgent->>MemoryManagerAdapter: __init__(max_context_tokens)
        MemoryManagerAdapter->>MemoryManagerAdapter: initialize_three_tier_memory()
        MemoryManagerAdapter-->>ReactAgent: memory_ready
        
        opt Cognitive Memory Enabled
            ReactAgent->>CognitiveMemoryIntegration: __init__(work_dir)
            CognitiveMemoryIntegration->>CognitiveMemoryIntegration: setup_dual_memory()
            CognitiveMemoryIntegration-->>ReactAgent: cognitive_ready
        end
        
        ReactAgent->>ReactAgent: _define_tools()
        ReactAgent->>ReactAgent: _load_knowledge()
        ReactAgent-->>User: agent_ready (1450 lines)
    end
```

## 8. Message Hook System

```mermaid
sequenceDiagram
    participant ReactAgent
    participant MessageHook1
    participant MessageHook2
    participant Memory
    participant LLM

    ReactAgent->>ReactAgent: add_message_hook(hook1)
    ReactAgent->>ReactAgent: add_message_hook(hook2)
    
    Note over ReactAgent: During execution
    
    ReactAgent->>ReactAgent: _process_hooks("pre_llm", message)
    ReactAgent->>MessageHook1: process(message)
    MessageHook1-->>ReactAgent: modified_message
    ReactAgent->>MessageHook2: process(modified_message)
    MessageHook2-->>ReactAgent: final_message
    
    ReactAgent->>LLM: call_with_message(final_message)
    LLM-->>ReactAgent: response
    
    ReactAgent->>ReactAgent: _process_hooks("post_llm", response)
    ReactAgent->>MessageHook1: process(response)
    MessageHook1-->>ReactAgent: modified_response
    ReactAgent->>MessageHook2: process(modified_response)
    MessageHook2-->>ReactAgent: final_response
    
    ReactAgent->>Memory: add_message(final_response)
```

## Key Interaction Patterns

### 1. **Compression-Based Memory Management**
- Natural pressure-based triggering
- Automatic compression when threshold exceeded
- Layered history preservation

### 2. **Parallel Memory Updates**
- Cognitive Memory Integration updates both structured and event-based memories simultaneously
- Ensures consistency across memory systems

### 3. **Tool Validation Pipeline**
- Pydantic validation before execution
- Error handling at multiple levels
- Graceful degradation on failures

### 4. **Output Redirection for Logging**
- TeeOutput splits output to both console and log files
- Preserves complete execution history
- Enables debugging and analysis

### 5. **Service Auto-Configuration**
- Intelligent detection of API service based on keys and URLs
- Automatic context size configuration
- Fallback mechanisms for reliability

### 6. **Hook-Based Message Processing**
- Pre and post processing hooks
- Chainable modifications
- Non-intrusive monitoring and modification

## State Transitions

### Memory State Transitions

```mermaid
stateDiagram-v2
    [*] --> Empty: Initialize
    Empty --> Accumulating: Add Message
    Accumulating --> Accumulating: Add Message (< threshold)
    Accumulating --> Compressing: Pressure Threshold Reached
    Compressing --> Compressed: Generate Summary
    Compressed --> Accumulating: Clear Window
    Accumulating --> Saving: Save Checkpoint
    Saving --> Accumulating: Continue
    Accumulating --> [*]: Shutdown
```

### Agent Execution States

```mermaid
stateDiagram-v2
    [*] --> Idle: Initialize
    Idle --> Planning: Receive Task
    Planning --> Executing: Select Tool
    Executing --> WaitingForTool: Tool Call
    WaitingForTool --> Processing: Tool Result
    Processing --> Planning: Need More Actions
    Processing --> Completing: Task Done
    Completing --> Idle: Reset
    Planning --> Failed: Max Rounds Exceeded
    Failed --> Idle: Reset
    Idle --> [*]: Shutdown
```

## Performance Characteristics

### Memory Efficiency
- **Natural Decay**: O(1) compression trigger, O(n) compression operation
- **Three-tier Memory**: O(n) transfer operations, O(n²) relevance scoring
- **NLPL Events**: O(n·m) relevance computation (n events, m query terms)

### API Call Optimization
- Batched tool definitions in single request
- Context window management to prevent truncation
- Automatic retry with exponential backoff

### Persistence Strategy
- Lazy writing (only on checkpoint or compression)
- Incremental saves for large histories
- JSON serialization for portability