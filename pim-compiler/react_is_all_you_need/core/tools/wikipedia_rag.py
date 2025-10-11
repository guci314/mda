#!/usr/bin/env python3
"""
Wikipedia RAG：基于结构化知识索引的新型RAG实现
替代传统向量数据库RAG，使用分类索引和知识图谱
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

@dataclass
class WikiPage:
    """Wikipedia页面"""
    title: str
    category: str
    content: str
    related: List[str]
    source_path: str

@dataclass
class KnowledgeEntity:
    """知识实体"""
    name: str
    type: str
    description: str
    relations: List[Tuple[str, str]]  # [(relation_type, target_entity)]

class WikipediaRAG:
    """基于Wikipedia风格知识组织的RAG系统"""

    def __init__(self, wiki_dir: str):
        """
        初始化Wikipedia RAG

        Args:
            wiki_dir: Wikipedia知识库目录
        """
        self.wiki_dir = Path(wiki_dir)
        self.category_index = {}
        self.alphabetical_index = {}
        self.knowledge_graph = {}
        self.pages_cache = {}

        # 加载索引和图谱
        self._load_indices()
        self._load_knowledge_graph()

    def _load_indices(self):
        """加载分类索引和字母索引"""
        # 加载分类索引
        category_file = self.wiki_dir / "CATEGORY_INDEX.md"
        if category_file.exists():
            content = category_file.read_text(encoding='utf-8')
            self._parse_category_index(content)

        # 加载字母索引
        alpha_file = self.wiki_dir / "ALPHABETICAL_INDEX.md"
        if alpha_file.exists():
            content = alpha_file.read_text(encoding='utf-8')
            self._parse_alphabetical_index(content)

    def _parse_category_index(self, content: str):
        """解析分类索引"""
        current_category = None
        for line in content.split('\n'):
            if line.startswith('## '):
                current_category = line[3:].strip()
                self.category_index[current_category] = []
            elif line.startswith('- ') and current_category:
                # 提取页面链接
                match = re.search(r'\[([^\]]+)\]\(([^\)]+)\)', line)
                if match:
                    title = match.group(1)
                    filename = match.group(2)
                    self.category_index[current_category].append({
                        'title': title,
                        'file': filename
                    })

    def _parse_alphabetical_index(self, content: str):
        """解析字母索引"""
        for line in content.split('\n'):
            if line.startswith('- **['):
                match = re.search(r'\[([^\]]+)\]\(([^\)]+)\)', line)
                if match:
                    title = match.group(1)
                    filename = match.group(2)
                    first_letter = title[0].upper()
                    if first_letter not in self.alphabetical_index:
                        self.alphabetical_index[first_letter] = []
                    self.alphabetical_index[first_letter].append({
                        'title': title,
                        'file': filename
                    })

    def _load_knowledge_graph(self):
        """加载知识图谱"""
        graph_file = self.wiki_dir / "docs_knowledge_graph.json"
        if graph_file.exists():
            with open(graph_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

                # 构建实体字典
                for entity in data.get('entities', []):
                    self.knowledge_graph[entity['name']] = KnowledgeEntity(
                        name=entity['name'],
                        type=entity['type'],
                        description=entity.get('description', ''),
                        relations=[]
                    )

                # 添加关系
                for relation in data.get('relations', []):
                    source = relation['source']
                    target = relation['target']
                    rel_type = relation['type']
                    if source in self.knowledge_graph:
                        self.knowledge_graph[source].relations.append((rel_type, target))

    def retrieve_by_category(self, category: str) -> List[WikiPage]:
        """
        按分类检索知识

        Args:
            category: 分类名称

        Returns:
            相关Wikipedia页面列表
        """
        pages = []
        if category in self.category_index:
            for page_info in self.category_index[category]:
                page = self._load_page(page_info['file'])
                if page:
                    pages.append(page)
        return pages

    def retrieve_by_keyword(self, keyword: str) -> List[WikiPage]:
        """
        按关键词检索知识

        Args:
            keyword: 关键词

        Returns:
            相关Wikipedia页面列表
        """
        pages = []
        keyword_lower = keyword.lower()

        # 搜索所有分类
        for category, items in self.category_index.items():
            for page_info in items:
                if keyword_lower in page_info['title'].lower():
                    page = self._load_page(page_info['file'])
                    if page:
                        pages.append(page)

        return pages

    def retrieve_by_relation(self, entity_name: str, max_depth: int = 2) -> List[WikiPage]:
        """
        按知识图谱关系检索

        Args:
            entity_name: 实体名称
            max_depth: 最大遍历深度

        Returns:
            相关Wikipedia页面列表
        """
        pages = []
        visited = set()

        def traverse(entity: str, depth: int):
            if depth > max_depth or entity in visited:
                return
            visited.add(entity)

            # 加载实体对应的页面
            page_file = f"{entity}.md"
            page = self._load_page(page_file)
            if page:
                pages.append(page)

            # 遍历相关实体
            if entity in self.knowledge_graph:
                for rel_type, target in self.knowledge_graph[entity].relations:
                    traverse(target, depth + 1)

        traverse(entity_name, 0)
        return pages

    def _load_page(self, filename: str) -> Optional[WikiPage]:
        """
        加载Wikipedia页面

        Args:
            filename: 文件名

        Returns:
            WikiPage对象或None
        """
        # 检查缓存
        if filename in self.pages_cache:
            return self.pages_cache[filename]

        filepath = self.wiki_dir / filename
        if not filepath.exists():
            return None

        content = filepath.read_text(encoding='utf-8')

        # 解析页面内容
        title = self._extract_title(content)
        category = self._extract_category(content)
        related = self._extract_related(content)

        page = WikiPage(
            title=title,
            category=category,
            content=content,
            related=related,
            source_path=str(filepath)
        )

        # 缓存页面
        self.pages_cache[filename] = page
        return page

    def _extract_title(self, content: str) -> str:
        """从内容中提取标题"""
        lines = content.split('\n')
        for line in lines:
            if line.startswith('# '):
                return line[2:].strip()
        return "Untitled"

    def _extract_category(self, content: str) -> str:
        """从内容中提取分类"""
        # 查找"分类："或"Category:"行
        for line in content.split('\n'):
            if '分类：' in line or 'Category:' in line:
                return line.split('：')[-1].strip() if '：' in line else line.split(':')[-1].strip()
        return "未分类"

    def _extract_related(self, content: str) -> List[str]:
        """从内容中提取相关页面"""
        related = []
        # 查找所有内部链接
        matches = re.findall(r'\[([^\]]+)\]\(([^\)]+\.md)\)', content)
        for title, filename in matches:
            if filename != '#':  # 排除锚点链接
                related.append(title)
        return related

    def answer_question(self, question: str) -> str:
        """
        回答问题（主要接口）

        Args:
            question: 用户问题

        Returns:
            基于Wikipedia知识的答案
        """
        # 1. 理解问题意图
        intent = self._understand_intent(question)

        # 2. 检索相关知识
        pages = []

        # 按意图类型检索
        if intent['type'] == 'concept':
            # 概念查询：直接查找对应页面
            pages = self.retrieve_by_keyword(intent['keyword'])
        elif intent['type'] == 'category':
            # 分类查询：检索整个分类
            pages = self.retrieve_by_category(intent['category'])
        elif intent['type'] == 'relation':
            # 关系查询：使用知识图谱
            pages = self.retrieve_by_relation(intent['entity'])
        else:
            # 通用查询：综合检索
            pages = self.retrieve_by_keyword(intent['keyword'])

        # 3. 构建上下文
        context = self._build_context(pages)

        # 4. 生成答案
        answer = self._generate_answer(question, context, pages)

        return answer

    def _understand_intent(self, question: str) -> Dict:
        """
        理解问题意图

        简化版实现，实际可以用LLM
        """
        question_lower = question.lower()

        # 概念查询
        if any(word in question_lower for word in ['什么是', 'what is', '定义', '概念']):
            # 提取关键概念
            keyword = question.replace('什么是', '').replace('?', '').replace('？', '').strip()
            return {'type': 'concept', 'keyword': keyword}

        # 分类查询
        if any(word in question_lower for word in ['有哪些', '列出', '所有的']):
            # 尝试匹配分类
            for category in self.category_index.keys():
                if category.lower() in question_lower:
                    return {'type': 'category', 'category': category}

        # 关系查询
        if any(word in question_lower for word in ['关系', '如何影响', '联系']):
            # 提取实体
            for entity in self.knowledge_graph.keys():
                if entity.lower() in question_lower:
                    return {'type': 'relation', 'entity': entity}

        # 默认：关键词查询
        # 提取最可能的关键词
        words = question.split()
        keyword = max(words, key=len) if words else question
        return {'type': 'general', 'keyword': keyword}

    def _build_context(self, pages: List[WikiPage]) -> str:
        """
        构建上下文

        Args:
            pages: Wikipedia页面列表

        Returns:
            合并的上下文字符串
        """
        if not pages:
            return "未找到相关知识。"

        context_parts = []
        for page in pages[:3]:  # 最多使用3个页面
            context_parts.append(f"## {page.title}\n\n{page.content[:1000]}...")

        return "\n\n---\n\n".join(context_parts)

    def _generate_answer(self, question: str, context: str, pages: List[WikiPage]) -> str:
        """
        生成答案

        简化版实现，实际应该调用LLM
        """
        if not pages:
            return "抱歉，我无法在知识库中找到相关信息来回答这个问题。"

        # 构建答案
        answer = f"基于知识库，我找到了以下相关信息：\n\n"

        # 添加主要信息
        main_page = pages[0]
        answer += f"**{main_page.title}**\n\n"

        # 提取关键段落（简化版）
        paragraphs = main_page.content.split('\n\n')
        for para in paragraphs[:2]:  # 前两段
            if para and not para.startswith('#'):
                answer += f"{para}\n\n"

        # 添加相关页面
        if len(pages) > 1:
            answer += "\n**相关知识**：\n"
            for page in pages[1:3]:
                answer += f"- [{page.title}]({page.source_path})\n"

        # 添加来源
        answer += f"\n*信息来源：{main_page.source_path}*"

        return answer

def demo():
    """演示Wikipedia RAG的使用"""

    # 初始化
    rag = WikipediaRAG("/tmp/agent_creator/docs_wikipedia")

    # 测试不同类型的查询
    questions = [
        "什么是冯诺依曼等价性？",
        "有哪些架构设计方案？",
        "AIA架构和其他架构的关系是什么？"
    ]

    for q in questions:
        print(f"\n问题：{q}")
        print("-" * 50)
        answer = rag.answer_question(q)
        print(answer)
        print("=" * 50)

if __name__ == "__main__":
    demo()