# 记忆系统迁移指南

## 目标

将现有的静态记忆系统迁移到动态记忆系统，实现知识的分层管理和动态验证。

## 迁移步骤

### Phase 1: 现有记忆标注（立即可行）

#### 1.1 为现有知识添加分类标签

在不改变现有系统的情况下，先为 `extracted_knowledge.md` 中的内容添加分类标记：

```markdown
## 更新后的长期记忆

### 用户档案（更新）[PRINCIPLE]
- **姓名**：谷词
- **语言**：中文
<!-- metadata: confidence=1.0, source="用户确认" -->

### 项目知识库：React Is All You Need

#### world_overview.md 触发机制（经验验证）[IMPL]
| 触发时机 | 触发条件 | 代码位置 | 执行顺序 |
|----------|----------|----------|----------|
| Agent初始化时 | world_overview.md不存在 | react_agent.py:502 | 第1步 |
<!-- metadata: confidence=0.85, verification="grep _check_world_overview", last_verified="2024-12-14" -->

#### React Agent 设计理念 [PRINCIPLE]
- 采用延迟初始化策略提升性能
- 三级记忆系统适应不同场景
<!-- metadata: confidence=0.95, source="架构文档" -->

#### 查找功能实现的方法 [META]
1. 使用 grep 搜索关键函数名
2. 通过 Read 工具查看具体实现
3. 追踪调用链理解完整流程
<!-- metadata: confidence=1.0, source="最佳实践" -->
```

#### 1.2 实现简单的分类读取器

```python
class LayeredKnowledgeReader:
    """在现有系统基础上的分层读取器"""
    
    def __init__(self, knowledge_file: Path):
        self.knowledge_file = knowledge_file
        self._parse_knowledge()
    
    def _parse_knowledge(self):
        content = self.knowledge_file.read_text()
        # 使用正则提取不同类型的知识
        self.meta_knowledge = self._extract_by_tag(content, "[META]")
        self.principles = self._extract_by_tag(content, "[PRINCIPLE]")
        self.interfaces = self._extract_by_tag(content, "[INTERFACE]")
        self.implementations = self._extract_by_tag(content, "[IMPL]")
    
    def get_stable_knowledge(self):
        """获取稳定的知识（META + PRINCIPLE）"""
        return self.meta_knowledge + self.principles
    
    def get_volatile_knowledge(self):
        """获取需要验证的知识（IMPL）"""
        return self.implementations
```

### Phase 2: 添加验证机制（最小改动）

#### 2.1 在使用前验证实现层知识

修改 Agent 回答问题的逻辑，添加简单的验证：

```python
def answer_with_verification(self, question: str):
    # 原有逻辑
    knowledge = self.search_knowledge(question)
    
    # 新增：验证实现层知识
    if "[IMPL]" in knowledge and "代码位置" in knowledge:
        # 提取文件和行号
        match = re.search(r'(\w+\.py):(\d+)', knowledge)
        if match:
            file, line = match.groups()
            # 简单验证：检查文件是否存在
            if not Path(file).exists():
                return f"注意：{file} 可能已被移动或重命名，建议重新搜索。"
    
    return knowledge
```

#### 2.2 添加置信度衰减

在定期任务中降低实现层知识的置信度：

```python
def decay_confidence(self):
    """每周执行一次，降低实现层知识的置信度"""
    content = self.knowledge_file.read_text()
    
    # 查找所有 confidence 值
    def reduce_confidence(match):
        conf = float(match.group(1))
        new_conf = conf * 0.95  # 每周降低 5%
        return f"confidence={new_conf:.2f}"
    
    # 只对 [IMPL] 部分的 confidence 进行衰减
    # ... 实现细节
```

### Phase 3: 分层存储（结构改进）

#### 3.1 新的目录结构

```
long_term_data/
├── meta_knowledge.md       # [META] 如何学习
├── principles.md          # [PRINCIPLE] 核心理念  
├── interfaces.md          # [INTERFACE] API定义
├── implementations/       # [IMPL] 实现细节
│   ├── current.md
│   └── verification_log.json
└── knowledge_index.yaml   # 知识索引
```

#### 3.2 迁移脚本

```python
def migrate_to_layered_storage(old_file: Path, new_dir: Path):
    """将单一文件迁移到分层结构"""
    reader = LayeredKnowledgeReader(old_file)
    
    # 创建目录结构
    new_dir.mkdir(exist_ok=True)
    (new_dir / "implementations").mkdir(exist_ok=True)
    
    # 分别保存
    (new_dir / "meta_knowledge.md").write_text(
        format_knowledge(reader.meta_knowledge)
    )
    (new_dir / "principles.md").write_text(
        format_knowledge(reader.principles)
    )
    # ... 其他层级
    
    # 创建索引
    create_index(new_dir)
```

### Phase 4: 智能更新（最终目标）

#### 4.1 文件监控

```python
class KnowledgeWatcher:
    """监控代码变更，主动更新相关知识"""
    
    def __init__(self, watch_patterns: List[str]):
        self.patterns = watch_patterns
        self.file_hashes = {}
    
    def check_changes(self):
        """检查文件是否变更"""
        changed_files = []
        for pattern in self.patterns:
            for file in glob.glob(pattern):
                current_hash = self.get_file_hash(file)
                if file in self.file_hashes:
                    if self.file_hashes[file] != current_hash:
                        changed_files.append(file)
                self.file_hashes[file] = current_hash
        return changed_files
    
    def invalidate_related_knowledge(self, changed_files):
        """使相关知识失效"""
        # 降低相关实现层知识的置信度
        # 触发重新验证
```

#### 4.2 主动学习

```python
class ProactiveLearner:
    """主动学习新知识"""
    
    def learn_from_user_correction(self, wrong_answer, correction):
        """从用户纠正中学习"""
        # 1. 分析错误原因
        # 2. 更新相关知识的置信度
        # 3. 添加新的验证方法
        # 4. 可能的话，更新元知识
    
    def periodic_self_check(self):
        """定期自检"""
        # 1. 验证高频使用的知识
        # 2. 清理低置信度且长期未用的知识
        # 3. 整理和优化知识结构
```

## 迁移时间表

- **Week 1**: 完成 Phase 1（标注和分类）
- **Week 2-3**: 实现 Phase 2（验证机制）
- **Month 2**: 完成 Phase 3（分层存储）
- **Month 3**: 实现 Phase 4（智能更新）

## 向后兼容

在整个迁移过程中保持向后兼容：

1. 保留原有的 `extracted_knowledge.md` 文件
2. 新系统可以读取旧格式
3. 逐步迁移，不影响现有功能
4. 提供降级选项

## 成功标准

- ✅ 减少 50% 的过时信息错误
- ✅ 知识验证响应时间 < 100ms
- ✅ 置信度准确率 > 85%
- ✅ 用户满意度提升
- ✅ 维护成本降低

这个迁移计划确保了平滑过渡，同时逐步实现动态记忆系统的所有优势。