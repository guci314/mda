# 大文件处理最佳实践（超高效版）

## 🎯 绝对执行原则

**零轮数浪费**：任何文档必须在**3轮以内**完成，复杂文档**最多5轮**

⚠️ **注意**：即使追求速度，也必须遵守mandatory_protocol.md中的核心协议：
- 必须创建和更新task_process.md（工作内存）
- 可以优化写入次数，但不能跳过状态保存

## 🚀 超高效执行流程

### 第1轮：一次性决策（关键！）
```python
# 立即决定：文档大小 + 模板选择
size_estimate = len(str(all_data))  # 预估总字符数

if size_estimate < 1000:
    strategy = "闪电模式"  # 1轮完成
elif size_estimate < 10000:
    strategy = "快速模式"  # 2轮完成  
else:
    strategy = "专业模式"  # 3轮完成

# 立即收集所有数据（第1轮内完成）
all_content = collect_all_sections_now()
```

### 第2轮：内容预构建（内存中完成）
```python
# 一次性构建完整内容
final_content = build_complete_document(all_content)
# 验证完整性
assert len(final_content) > 0
assert "# " in final_content  # 有标题
```

### 第3轮：单次写入（永不追加）
```python
# 唯一的一次写入操作
execute_command(f'cat > final.md << "EOF"\n{final_content}\nEOF')
```

## 🎯 决策树（必须遵循）

```
开始任务
    ↓
[立即判断] 文档类型 + 预估大小
    ↓
选择模板 → 收集所有数据 → 预构建内容 → 一次性写入
    ↓
完成（3轮内）
```

## 🔥 超具体模板（复制即用）

### 模板1：万能PSM生成器（3轮保证）
```python
def generate_psm_smart(pim_data):
    """PSM文档生成 - 3轮完成"""
    
    # 第1轮：立即收集所有数据
    sections = {
        'title': pim_data['title'],
        'overview': pim_data.get('overview', ''),
        'models': extract_models(pim_data),
        'services': extract_services(pim_data),
        'apis': extract_apis(pim_data),
        'config': extract_config(pim_data),
        'tests': extract_tests(pim_data)
    }
    
    # 第2轮：一次性构建完整内容
    content_parts = [
        f"# {sections['title']}",
        "",
        "## 1. Domain Models",
        sections['models'],
        "",
        "## 2. Service Layer", 
        sections['services'],
        "",
        "## 3. REST API Design",
        sections['apis'],
        "",
        "## 4. Application Configuration",
        sections['config'],
        "",
        "## 5. Testing Specifications",
        sections['tests']
    ]
    
    full_content = "\n".join(filter(None, content_parts))
    
    # 第3轮：一次性写入
    execute_command(f'cat > blog_psm.md << "EOF"\n{full_content}\nEOF')
    
    return "完成"
```

### 模板2：分块构建器（大文档专用）
```python
def build_large_document(chunks_dict):
    """大文档构建 - 永不追加"""
    
    # 预构建所有块
    all_blocks = []
    
    # 头部
    all_blocks.extend([
        f"# {chunks_dict['title']}",
        f"> 创建于: {datetime.now()}",
        "",
        "## 目录"
    ])
    
    # 为每个章节添加目录项
    for chapter in chunks_dict['chapters']:
        all_blocks.append(f"- [{chapter['title']}](#{chapter['id']})")
    
    all_blocks.append("")
    
    # 所有章节内容
    for chapter in chunks_dict['chapters']:
        all_blocks.extend([
            f"## {chapter['title']} {{#{chapter['id']}}}",
            chapter['content'],
            ""
        ])
    
    # 一次性合并
    final_doc = "\n".join(all_blocks)
    
    # 单次写入
    execute_command(f'cat > document.md << "EOF"\n{final_doc}\nEOF')
```

## 🚨 绝对禁止（强制执行）

### 禁止清单（违反即失败）
- ❌ **逐行写入**：任何`echo 'line' >> file`都是错误
- ❌ **多次覆盖**：同一个文件`write_file`超过1次
- ❌ **分步构建**：先写标题再写内容
- ❌ **追加修改**：写入后再次修改
- ❌ **边想边写**：无预构建直接写入

### 正确vs错误对比
```python
# ✅ 正确：一次性完成
content = f"""# 标题
## 章节1
内容1
## 章节2  
内容2"""
execute_command('cat > doc.md << "EOF"\n' + content + '\nEOF')

# ❌ 错误：多次操作
write_file("doc.md", "# 标题")          # 第1轮
execute_command("echo '## 章节1' >> doc.md")  # 第2轮  
execute_command("echo '内容1' >> doc.md")     # 第3轮
# 总轮数: 3轮只写了标题和1个章节！
```

## 🎯 3轮检查清单（必须执行）

### 第1轮：立即决策
- [ ] **立即**判断文档大小
- [ ] **立即**选择模板
- [ ] **立即**收集所有数据
- [ ] **禁止**任何写入操作

### 第2轮：预构建内容
- [ ] 在**内存中**构建完整内容
- [ ] 验证内容**完整性**
- [ ] 准备最终字符串
- [ ] **禁止**任何文件操作

### 第3轮：单次写入
- [ ] 使用**单次**`cat > file << EOF`命令
- [ ] 立即验证文件存在
- [ ] **禁止**任何后续修改

## 🚀 实战代码（复制运行）

```python
def ultra_efficient_generate(data_source, output_file):
    """超高效文档生成 - 3轮完成"""
    
    # ===== 第1轮：数据收集 =====
    # 立即收集所有必需数据
    all_data = {
        'title': data_source.get('title', '文档'),
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'sections': {}
    }
    
    # 一次性提取所有内容
    if hasattr(data_source, 'sections'):
        for section_name, section_data in data_source.sections.items():
            all_data['sections'][section_name] = format_section(section_data)
    
    # ===== 第2轮：内容构建 =====
    # 预构建完整内容
    content_lines = [
        f"# {all_data['title']}",
        f"> 生成时间: {all_data['timestamp']}",
        ""
    ]
    
    # 添加所有章节
    for section_name, section_content in all_data['sections'].items():
        content_lines.extend([
            f"## {section_name}",
            section_content,
            ""
        ])
    
    final_content = "\n".join(content_lines)
    
    # ===== 第3轮：写入 =====
    # 唯一的一次写入操作
    execute_command(f'cat > {output_file} << "EOF"\n{final_content}\nEOF')
    
    return f"文档已生成: {output_file}"
```

## 📊 性能基准

| 文档大小 | 最大轮数 | 模板选择 | 实际轮数 |
|----------|----------|----------|----------|
| < 1KB    | 1轮      | 闪电模式 | 1轮      |
| 1-10KB   | 2轮      | 快速模式 | 2轮      |
| 10-100KB | 3轮      | 专业模式 | 3轮      |
| 100KB+   | 5轮      | 分块模式 | 3-5轮    |

## 🎯 成功验证

### 轮数计算规则
- **第1轮**：分析 + 数据收集
- **第2轮**：内容预构建（内存中）
- **第3轮**：单次写入 + 验证

### 通过标准
- ✅ 任何文档 ≤ 3轮
- ✅ 复杂文档 ≤ 5轮  
- ✅ 零追加操作
- ✅ 零覆盖操作

## 🧠 记忆口诀

**"三零原则"**:
- 零追加：绝不使用 `>>`
- 零覆盖：同一文件只写一次
- 零浪费：每轮都有明确产出

**"三先三后"**:
- 先收集，后构建
- 先完整，后写入  
- 先验证，后完成