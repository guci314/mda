# DeepSeek 长文档生成策略

## 问题背景
DeepSeek API 有以下限制：
- 单次请求最大输出 token 数：通常为 4096-8192 tokens
- 上下文窗口：32K tokens（包括输入和输出）

## 解决策略

### 1. 分段生成（Chunked Generation）
将长文档分成多个部分，逐段生成。

```python
def generate_long_document(sections):
    """分段生成长文档"""
    full_document = ""
    
    for i, section in enumerate(sections):
        prompt = f"""
        请生成文档的第 {i+1} 部分：{section['title']}
        
        要求：
        1. 详细完整地生成这一部分
        2. 与之前的部分保持一致性
        
        之前已生成的部分摘要：
        {get_summary(full_document)}
        """
        
        response = generate_section(prompt)
        full_document += response
        
    return full_document
```

### 2. 继续生成（Continuation）
检测输出是否被截断，然后请求继续。

```python
def generate_with_continuation(prompt, max_continuations=5):
    """带续写功能的生成"""
    full_text = ""
    continuation_count = 0
    
    # 初始生成
    response = llm.generate(prompt)
    full_text = response
    
    # 检查是否需要续写
    while seems_truncated(response) and continuation_count < max_continuations:
        continuation_prompt = f"""
        请继续上面的内容，从这里开始：
        ...{full_text[-200:]}
        
        请直接继续写，不要重复已有内容。
        """
        
        response = llm.generate(continuation_prompt)
        full_text += response
        continuation_count += 1
        
    return full_text
```

### 3. 大纲驱动生成（Outline-Driven）
先生成大纲，然后逐个章节展开。

```python
def generate_with_outline(topic):
    """基于大纲的长文档生成"""
    
    # 第一步：生成大纲
    outline_prompt = f"为 {topic} 生成详细的文档大纲"
    outline = llm.generate(outline_prompt)
    
    # 第二步：解析大纲
    sections = parse_outline(outline)
    
    # 第三步：逐节生成
    document = ""
    for section in sections:
        section_prompt = f"""
        根据大纲生成这一节的内容：
        章节：{section.title}
        子项：{section.items}
        """
        
        section_content = llm.generate(section_prompt)
        document += f"\n\n## {section.title}\n{section_content}"
    
    return document
```

### 4. 函数调用分块写入（Function Call Chunking）
使用函数调用能力，让模型自主决定何时写入文件。

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "append_to_document",
            "description": "追加内容到文档",
            "parameters": {
                "type": "object",
                "properties": {
                    "section_title": {"type": "string"},
                    "content": {"type": "string"},
                    "is_complete": {"type": "boolean"}
                }
            }
        }
    }
]

def generate_with_function_calls():
    """使用函数调用生成长文档"""
    messages = [
        {"role": "system", "content": "生成详细的技术文档，每次写一个章节"},
        {"role": "user", "content": "生成完整的 API 文档"}
    ]
    
    document_sections = []
    max_rounds = 20
    
    for round in range(max_rounds):
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )
        
        if response.choices[0].message.tool_calls:
            for tool_call in response.choices[0].message.tool_calls:
                args = json.loads(tool_call.function.arguments)
                document_sections.append(args)
                
                if args.get("is_complete"):
                    return compile_document(document_sections)
```

### 5. 流式生成（Streaming）
使用流式 API 逐步接收内容。

```python
def stream_long_document(prompt):
    """流式生成长文档"""
    stream = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}],
        stream=True,
        max_tokens=8000  # 设置较大的 max_tokens
    )
    
    full_content = ""
    for chunk in stream:
        if chunk.choices[0].delta.content:
            content = chunk.choices[0].delta.content
            full_content += content
            # 实时处理或保存
            process_chunk(content)
    
    return full_content
```

## 实际应用示例

### 为 PIM Compiler 实现长文档生成

```python
class LongDocumentGenerator:
    def __init__(self, client, model="deepseek-chat"):
        self.client = client
        self.model = model
        
    def generate_long_psm(self, pim_content, platform="fastapi"):
        """生成长 PSM 文档"""
        
        # 1. 生成文档结构
        structure = self._generate_structure(pim_content)
        
        # 2. 分章节生成
        sections = []
        for chapter in structure['chapters']:
            section_content = self._generate_section(
                chapter, 
                pim_content, 
                previous_sections=sections
            )
            sections.append({
                'title': chapter['title'],
                'content': section_content
            })
            
        # 3. 组装完整文档
        return self._assemble_document(sections)
    
    def _generate_structure(self, pim_content):
        """生成文档结构"""
        prompt = f"""
        分析以下 PIM，生成 PSM 文档的章节结构：
        
        {pim_content}
        
        返回 JSON 格式的章节列表。
        """
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)
    
    def _generate_section(self, chapter, pim_content, previous_sections):
        """生成单个章节"""
        context = self._summarize_previous_sections(previous_sections)
        
        prompt = f"""
        基于以下 PIM 生成 PSM 的 {chapter['title']} 章节：
        
        PIM 内容：
        {pim_content}
        
        已生成章节摘要：
        {context}
        
        请详细生成本章节内容。
        """
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=4000
        )
        
        return response.choices[0].message.content
```

## 最佳实践建议

1. **设置合理的 max_tokens**
   ```python
   response = client.chat.completions.create(
       model="deepseek-chat",
       messages=messages,
       max_tokens=8000  # 尽可能大，但不超过模型限制
   )
   ```

2. **使用上下文压缩**
   - 对已生成内容进行摘要
   - 只保留必要的上下文信息

3. **实现断点续传**
   - 保存中间状态
   - 支持从断点继续生成

4. **并行生成**
   - 独立章节可以并行生成
   - 最后合并结果

5. **质量控制**
   - 每个部分生成后进行验证
   - 检查一致性和完整性

## 针对 PIM Compiler 的具体实现

已经在 Function Call Agent 中实现了分章节生成：

```python
chapters = [
    "文档标题和概述",
    "数据模型定义",
    "API 端点设计", 
    "服务层方法定义",
    "业务规则说明"
]

# 逐章生成，使用 append_file 追加内容
```

这种方法可以有效避免单次输出长度限制。