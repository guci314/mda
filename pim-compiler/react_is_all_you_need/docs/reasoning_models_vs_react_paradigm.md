# Reasoning Models vs React Paradigm: A Tale of Two Cognitive Architectures in Large Language Models

## Abstract

This paper explores a fundamental dichotomy in Large Language Model (LLM) architectures: the React (Reasoning-Acting) paradigm prevalent in conversational LLMs versus the Plan-Execute paradigm emerging in reasoning-specialized models. Through empirical observations and theoretical analysis, we demonstrate that training methodologies fundamentally shape model cognitive patterns, which in turn determine optimal workflow representations. Our findings suggest that conversational LLMs naturally align with dynamic, interleaved reasoning-acting patterns, while reasoning models exhibit preference for comprehensive planning followed by execution. This distinction has profound implications for multi-agent system design and workflow automation.

## 1. Introduction

The rapid evolution of Large Language Models has produced two distinct architectural philosophies: conversational models optimized for interactive dialogue (e.g., GPT-4, Claude) and reasoning models trained for deep analytical thinking (e.g., OpenAI o1, DeepSeek-R1). While both architectures share transformer-based foundations, their behavioral patterns diverge significantly when confronted with complex, multi-step tasks.

This divergence became apparent through a practical experiment: implementing a BPMN (Business Process Model and Notation) workflow for multi-agent coordination. The workflow, which required code generation, testing, and review with retry logic, failed catastrophically with conversational LLMs but succeeded naturally with reasoning models. This observation led to a deeper investigation of the underlying cognitive architectures.

## 2. The React Paradigm in Conversational LLMs

### 2.1 Theoretical Foundation

The React framework, introduced by Yao et al. (2022), synergizes reasoning and acting in language models through interleaved generation of thought traces and actions. This pattern mirrors human problem-solving:

```
Thought → Action → Observation → Thought → ...
```

### 2.2 Natural Emergence in Conversational Models

Conversational LLMs exhibit React patterns naturally because:

1. **Autoregressive Nature**: Token-by-token generation encourages incremental decision-making
2. **Interactive Training**: RLHF (Reinforcement Learning from Human Feedback) rewards responsive, adaptive behavior
3. **Limited Context Window**: Encourages breaking problems into manageable chunks
4. **Immediate Feedback Loop**: Tool use and user interaction provide constant environmental signals

### 2.3 Empirical Evidence

In our BPMN experiment, conversational LLMs:
- Created workflow files but failed to update execution status
- Lost track of retry counters and loop conditions
- Struggled with maintaining global state across multiple tool calls
- Defaulted to immediate action rather than comprehensive planning

## 3. The Plan-Execute Paradigm in Reasoning Models

### 3.1 Architectural Distinctions

Reasoning models introduce a fundamental architectural change:

```
Internal Reasoning Phase → Complete Plan Formation → Execution
```

This separation is enforced through:
1. **Dedicated Thinking Tokens**: Hidden reasoning traces before visible output
2. **Reward Shaping**: RL training that rewards only final answer correctness
3. **Extended Computation**: Ability to "think" for extended periods without output

### 3.2 Cognitive Implications

The Plan-Execute paradigm creates models that:
- Build complete mental models before acting
- Maintain consistent state across complex workflows
- Excel at symbolic manipulation and formal reasoning
- Naturally align with declarative specifications (like BPMN)

### 3.3 Empirical Success

DeepSeek-Reasoner successfully executed the same BPMN workflow by:
- Maintaining complete workflow state in working memory
- Tracking all variables and conditions internally
- Following complex branching logic without external state management
- Treating BPMN as a declarative specification to interpret

## 4. Comparative Analysis

### 4.1 Cognitive Architecture Comparison

| Aspect | React (Conversational) | Plan-Execute (Reasoning) |
|--------|----------------------|-------------------------|
| Thinking | Interleaved with action | Front-loaded |
| State Management | External/Environmental | Internal/Mental |
| Error Handling | Reactive adaptation | Preventive planning |
| Workflow Affinity | Natural language, intent-based | Symbolic, formal specifications |
| Strength | Dynamic environments | Static, well-defined problems |
| Weakness | Complex state tracking | Real-time adaptation |

### 4.2 Workflow Pattern Matching

Our experiments reveal a clear pattern:

**Natural Alignments:**
- Conversational LLMs + Intent Declaration Workflows ✓
- Conversational LLMs + Narrative/Script Workflows ✓
- Reasoning Models + BPMN/State Machines ✓
- Reasoning Models + Formal Specifications ✓

**Misalignments:**
- Conversational LLMs + BPMN ✗
- Reasoning Models + Highly Interactive Tasks ✗

## 5. Implications for Multi-Agent Systems

### 5.1 Agent Selection Strategy

Choose agents based on task characteristics:
- **Dynamic, exploratory tasks** → Conversational LLMs with React patterns
- **Well-defined, complex workflows** → Reasoning models with Plan-Execute patterns

### 5.2 Workflow Design Principles

For conversational LLMs:
```markdown
# Intent-Based Workflow
Goal: Create tested, high-quality code
Constraints: Max 3 retry attempts
Expected: Working code with quality score
```

For reasoning models:
```xml
<!-- BPMN Workflow -->
<process id="codeGenProcess">
  <serviceTask id="generate" implementation="code_generator"/>
  <exclusiveGateway id="testResult">
    <outgoing>passed</outgoing>
    <outgoing>failed</outgoing>
  </exclusiveGateway>
  <!-- Complete specification... -->
</process>
```

### 5.3 Hybrid Architectures

Future systems might combine both paradigms:
1. **Reasoning models for planning** → Generate detailed execution plans
2. **Conversational models for execution** → Handle dynamic interactions
3. **Mode switching** → Dynamically choose paradigm based on task phase

## 6. Related Work

- **ReAct (Yao et al., 2022)**: Established the reasoning-acting synergy in LLMs
- **Chain-of-Thought (Wei et al., 2022)**: Demonstrated emergent reasoning in large models
- **Constitutional AI (Anthropic, 2022)**: Showed how training shapes model behavior
- **Process Mining in AI (van der Aalst, 2016)**: Formal workflow representations

## 7. Limitations and Future Work

### 7.1 Current Limitations

1. **Binary Classification**: Models may exhibit mixed behaviors
2. **Task Dependency**: Some tasks might benefit from paradigm switching
3. **Limited Sample Size**: Based on specific model implementations

### 7.2 Future Directions

1. **Paradigm Detection**: Automatic classification of model cognitive patterns
2. **Adaptive Workflows**: Systems that adjust representation based on model type
3. **Training Methodology**: Exploring training techniques for hybrid behaviors
4. **Benchmark Development**: Standardized tests for React vs Plan-Execute capabilities

## 8. Conclusion

The distinction between React and Plan-Execute paradigms in LLMs is not merely academic—it has practical implications for system design. Our key findings:

1. **Training shapes cognition**: RLHF creates React patterns; RL with delayed rewards creates Plan-Execute patterns
2. **Workflow alignment matters**: Matching workflow style to model paradigm dramatically improves success rates
3. **No universal best**: Each paradigm excels in different contexts
4. **Future is hybrid**: Combining paradigms may yield more capable systems

The failure of BPMN with conversational LLMs is not a limitation but a feature—these models are optimized for dynamic, interactive problem-solving, not rigid workflow execution. Recognizing and embracing these fundamental differences enables more effective AI system design.

## References

1. Yao, S., Zhao, J., Yu, D., et al. (2022). ReAct: Synergizing Reasoning and Acting in Language Models. *arXiv preprint arXiv:2210.03629*.

2. Wei, J., Wang, X., Schuurmans, D., et al. (2022). Chain-of-Thought Prompting Elicits Reasoning in Large Language Models. *Advances in Neural Information Processing Systems*.

3. Brown, T., Mann, B., Ryder, N., et al. (2020). Language Models are Few-Shot Learners. *Advances in Neural Information Processing Systems*.

4. van der Aalst, W. (2016). Process Mining: Data Science in Action. *Springer*.

5. Ouyang, L., Wu, J., Jiang, X., et al. (2022). Training language models to follow instructions with human feedback. *Advances in Neural Information Processing Systems*.

## Appendix: Experimental Details

### A.1 BPMN Workflow Specification

```xml
<?xml version="1.0" encoding="UTF-8"?>
<definitions xmlns="http://www.omg.org/spec/BPMN/20100524/MODEL">
  <process id="mathUtilsDevProcess" name="MathUtils Development Process">
    <!-- Workflow includes: code generation, testing with retry logic, 
         and code review upon success -->
  </process>
</definitions>
```

### A.2 Model Configurations

- **Conversational LLMs**: GPT-4, Claude-3, Gemini-1.5
- **Reasoning Models**: DeepSeek-Reasoner, OpenAI o1-preview
- **Task**: Multi-agent coordination for code development
- **Metrics**: Task completion, state consistency, retry handling

### A.3 Natural Language Workflow Examples

**Intent Declaration (React-friendly):**
```
Create a reliable MathUtils class.
Allow up to 3 attempts to fix test failures.
Provide final code quality assessment.
```

**Narrative Workflow (React-friendly):**
```
The code generator creates MathUtils.
The tester validates functionality.
If tests fail, generator fixes issues (max 3x).
Finally, reviewer scores the code.
```

---

*Manuscript prepared for: Workshop on Cognitive Architectures in Large Language Models*

*Corresponding author: [Research Team, PIM Compiler Project]*