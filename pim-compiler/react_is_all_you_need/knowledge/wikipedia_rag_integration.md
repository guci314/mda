# Wikipedia RAG集成指南

## 核心理念

> "用CATEGORY_INDEX.md替代向量数据库，实现更优雅的RAG"

传统RAG像是把书撕成碎片，然后通过相似度找碎片。
Wikipedia RAG像是保持书的完整，通过目录找章节。

## 为什么Wikipedia RAG更适合Agent

### 1. Agent需要完整上下文
```python
# 传统RAG的问题
chunk1 = "...Agent的记忆系统包括..."  # 缺少开头
chunk2 = "...三个层次：工作记忆..."   # 缺少前后文
chunk3 = "...长期记忆的实现..."       # 缺少整体架构
# Agent拿到碎片，容易误解

# Wikipedia RAG的优势
page = load("记忆架构.md")  # 完整的架构文档
# Agent拿到完整知识，理解准确
```

### 2. Agent需要知识关系
```python
# 传统RAG：只有相似度
similar_chunks = vector_search("AIA架构")
# 不知道AIA和其他架构的关系

# Wikipedia RAG：明确的知识图谱
graph = {
    "AIA架构": {
        "基于": "冯诺依曼等价性",
        "演进为": "函数导向架构",
        "对比": "传统微服务架构"
    }
}
# Agent理解概念间的关系
```

### 3. Agent需要低成本运行
```yaml
# 传统RAG的依赖
dependencies:
  - vector_database: "$100/月"
  - gpu_for_embedding: "$50/月"
  - embedding_api: "$20/月"

# Wikipedia RAG的依赖
dependencies:
  - filesystem: "免费"
  - markdown_parser: "免费"
  - json_loader: "免费"
```

## 集成到ReactAgentMinimal

### 步骤1：准备知识库

```bash
# 1. 生成Wikipedia知识库
python /tmp/agent_creator/generate_wikipedia.py

# 2. 将生成的文件复制到Agent知识目录
cp -r /tmp/agent_creator/docs_wikipedia /home/guci/aiProjects/mda/pim-compiler/react_is_all_you_need/knowledge/wikipedia/

# 3. 关键文件
knowledge/wikipedia/
├── CATEGORY_INDEX.md        # 分类索引（核心）
├── ALPHABETICAL_INDEX.md    # 字母索引
├── docs_knowledge_graph.json # 知识图谱
└── *.md                     # Wikipedia页面
```

### 步骤2：创建Wikipedia RAG工具

```python
# core/tools/wikipedia_rag_tool.py
from tool_base import Function
from pathlib import Path
import re

class WikipediaRAGTool(Function):
    """Wikipedia RAG工具"""

    def __init__(self, work_dir):
        super().__init__(
            name="wikipedia_rag",
            description="基于分类索引检索结构化知识",
            parameters={
                "query": {
                    "type": "string",
                    "description": "查询问题"
                },
                "category": {
                    "type": "string",
                    "description": "知识分类（可选）"
                }
            }
        )
        self.wiki_dir = Path(work_dir) / "knowledge" / "wikipedia"
        self.category_index = self._load_category_index()

    def _load_category_index(self):
        """加载分类索引"""
        index_file = self.wiki_dir / "CATEGORY_INDEX.md"
        if not index_file.exists():
            return {}

        # 解析Markdown格式的索引
        index = {}
        current_category = None

        with open(index_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('## '):
                    current_category = line[3:].strip()
                    index[current_category] = []
                elif line.startswith('- ') and current_category:
                    # 提取页面链接
                    match = re.search(r'\[([^\]]+)\]\(([^\)]+)\)', line)
                    if match:
                        title, file = match.groups()
                        index[current_category].append({
                            'title': title,
                            'file': file
                        })
        return index

    def execute(self, **kwargs):
        query = kwargs["query"]
        category = kwargs.get("category")

        # 如果指定了分类，直接检索该分类
        if category and category in self.category_index:
            pages = self.category_index[category]
            return self._load_pages(pages[:3])

        # 否则，理解查询意图
        relevant_category = self._understand_query(query)
        if relevant_category in self.category_index:
            pages = self.category_index[relevant_category]
            return self._load_pages(pages[:3])

        return "未找到相关知识"

    def _understand_query(self, query):
        """简单的意图理解"""
        query_lower = query.lower()

        # 根据关键词映射到分类
        if any(word in query_lower for word in ['架构', 'architecture', 'aia']):
            return '架构设计'
        elif any(word in query_lower for word in ['理论', 'theory', '等价']):
            return '核心理论'
        elif any(word in query_lower for word in ['实现', 'implement', '技术']):
            return '技术实现'
        else:
            return '通用知识'

    def _load_pages(self, pages):
        """加载Wikipedia页面"""
        contents = []
        for page in pages:
            file_path = self.wiki_dir / page['file']
            if file_path.exists():
                content = file_path.read_text(encoding='utf-8')
                contents.append(f"## {page['title']}\n\n{content[:1000]}...")
        return "\n\n---\n\n".join(contents)
```

### 步骤3：在Agent中使用

```python
# 使用示例
from core.react_agent_minimal import ReactAgentMinimal
from core.tools.wikipedia_rag_tool import WikipediaRAGTool

# 创建Agent，加载Wikipedia索引作为知识
agent = ReactAgentMinimal(
    name="rag_agent",
    work_dir="/home/guci/aiProjects/mda/pim-compiler/react_is_all_you_need",
    model="gpt-4",
    knowledge_files=[
        "knowledge/wikipedia/CATEGORY_INDEX.md",  # 加载索引
        "knowledge/wikipedia/docs_knowledge_graph.json"  # 加载图谱
    ]
)

# 添加Wikipedia RAG工具
agent.add_tool(WikipediaRAGTool(agent.work_dir))

# 现在Agent可以使用结构化知识了
response = agent.run("""
请解释一下AIA架构的核心理念。
使用wikipedia_rag工具检索相关知识。
""")
```

## 知识文件的使用方式

### 方式1：直接加载索引（推荐）
```python
# Agent只需要知道分类结构
knowledge_files = ["knowledge/wikipedia/CATEGORY_INDEX.md"]

# Agent通过理解索引来导航知识
# 不需要把所有知识都加载到上下文
```

### 方式2：按需加载页面
```python
def load_knowledge_for_task(task_type):
    """根据任务类型加载相关知识"""

    if task_type == "architecture_design":
        return [
            "knowledge/wikipedia/AIA架构.md",
            "knowledge/wikipedia/函数导向架构.md"
        ]
    elif task_type == "theory_research":
        return [
            "knowledge/wikipedia/冯诺依曼等价性.md",
            "knowledge/wikipedia/计算-认知-语言统一理论.md"
        ]
    else:
        return ["knowledge/wikipedia/CATEGORY_INDEX.md"]
```

### 方式3：动态检索
```python
# Agent在执行中动态检索
agent_prompt = """
当遇到不了解的概念时：
1. 使用wikipedia_rag工具检索
2. 基于检索到的知识继续推理
3. 如果需要更多信息，检索相关页面
"""
```

## 效果对比

### 查询："如何实现Agent的记忆系统？"

#### 传统RAG响应：
```
找到5个相关chunks：
1. "...短期记忆使用..."（来自第3章中间）
2. "...compact.md文件..."（来自第5章末尾）
3. "...记忆压缩算法..."（来自附录）
4. "...working_memory变量..."（来自代码片段）
5. "...参考MemoryManager..."（来自另一个文档）

[拼接后上下文混乱，Agent难以理解完整架构]
```

#### Wikipedia RAG响应：
```
找到完整知识页面：

## 记忆架构
完整的Agent记忆系统设计，包括：
1. 三层记忆模型（工作记忆、情景记忆、语义记忆）
2. 实现方式（文件系统映射）
3. 代码示例
4. 相关链接：[内存压缩]、[知识管理]

[Agent获得完整、结构化的知识]
```

## 性能优势

```python
# 性能测试对比
def benchmark():
    # 传统RAG
    start = time.time()
    embeddings = get_embeddings(query)  # 100ms
    chunks = vector_search(embeddings)  # 100ms
    context = merge_chunks(chunks)      # 50ms
    # 总计：250ms

    # Wikipedia RAG
    start = time.time()
    category = understand_category(query)  # 5ms
    pages = load_category_pages(category)  # 5ms
    # 总计：10ms

    # 性能提升：25倍！
```

## 维护优势

### 更新知识

```bash
# 传统RAG：复杂的更新流程
1. 修改源文档
2. 重新分块
3. 重新计算embeddings（GPU密集）
4. 更新向量数据库
5. 验证索引完整性

# Wikipedia RAG：简单直接
1. 编辑对应的.md文件
2. 完成！（Git会记录变更）
```

### 添加新知识

```bash
# 传统RAG
python add_to_vectordb.py new_doc.pdf --chunk-size 500 --overlap 50

# Wikipedia RAG
echo "## 新概念\n\n内容..." > knowledge/wikipedia/新概念.md
echo "- [新概念](新概念.md)" >> knowledge/wikipedia/CATEGORY_INDEX.md
```

## 最佳实践

### 1. 知识组织原则
```markdown
每个Wikipedia页面应该：
- 概念原子化（一个页面一个概念）
- 上下文完整（不依赖外部信息）
- 关系明确（标注相关概念）
- 结构清晰（有目录和章节）
```

### 2. 索引维护原则
```markdown
CATEGORY_INDEX.md应该：
- 分类层次不超过3层
- 每个分类不超过10个项目
- 分类名称清晰明确
- 定期重组优化
```

### 3. Agent集成原则
```python
# Agent应该学会：
1. 理解分类体系
2. 导航知识结构
3. 组合多个页面
4. 记住常用路径
```

## 迁移检查清单

- [ ] 导出现有RAG的所有文档
- [ ] 将chunks合并回完整文档
- [ ] 按概念创建Wikipedia页面
- [ ] 生成CATEGORY_INDEX.md
- [ ] 创建knowledge_graph.json
- [ ] 实现WikipediaRAGTool
- [ ] 更新Agent配置
- [ ] 测试检索质量
- [ ] 对比性能指标
- [ ] 删除向量数据库依赖

## 结论

Wikipedia RAG不是技术倒退，而是回归本质：
- 知识的本质是结构，不是向量
- 理解的本质是关系，不是相似度
- 检索的本质是导航，不是搜索

对Agent来说，Wikipedia RAG提供了：
1. **更高质量的知识**（完整、结构化）
2. **更低的运行成本**（无需GPU和向量库）
3. **更好的可维护性**（直接编辑Markdown）
4. **更强的可解释性**（明确的检索路径）

这正是Agent需要的知识组织方式！