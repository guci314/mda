# Python语法和缩进问题修复策略

## 核心原则：一次性彻底修复

**重要**：不要逐行修复语法错误！Python的缩进和语法错误往往是整体性的，需要理解完整的代码结构。

## 缩进问题修复策略

### 1. 整体重写策略（推荐）

当遇到缩进错误时，**不要只修复报错的那一行**，而是：

```python
# ❌ 错误做法：只修复第25行
old: "        \"isbn\": \"9787532767405\","
new: "    \"isbn\": \"9787532767405\","

# ✅ 正确做法：重写整个函数或代码块
def test_add_book(client):
    # 重写整个测试函数，确保缩进一致
    response = client.post("/books/", json={
        "isbn": "9787532767406",
        "title": "解忧杂货店",
        "author": "[日] 东野圭吾",
        "publisher": "南海出版公司",
        "publish_year": 2014,
        "category": "小说",
        "total_quantity": 10,
        "available_quantity": 10,
        "location": "A-1-1"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "解忧杂货店"
```

### 2. 缩进规则检查清单

修复前必须检查：
- [ ] 使用4个空格，不是Tab
- [ ] 同一代码块内缩进一致
- [ ] 函数定义后的第一行要缩进
- [ ] if/for/while/with等语句后要缩进
- [ ] 多行字典/列表的缩进要对齐

## 大括号/括号不匹配问题

### 1. 括号配对检查策略

```python
# 使用read_file读取完整文件内容
# 然后计数括号：
def check_brackets(content):
    brackets = {
        '(': 0, ')': 0,
        '[': 0, ']': 0,
        '{': 0, '}': 0
    }
    for char in content:
        if char in brackets:
            brackets[char] += 1
    
    # 检查配对
    if brackets['('] != brackets[')']:
        return f"圆括号不匹配: ({brackets['(']}) vs ){brackets[')']})"
    if brackets['['] != brackets[']']:
        return f"方括号不匹配: [{brackets['[']}) vs ]{brackets[']'}]"
    if brackets['{'] != brackets['}']:
        return f"花括号不匹配: {{{brackets['{']}) vs }}{brackets['}']}}"
```

### 2. 修复策略

**不要添加单独的括号！** 而是找到缺失的完整结构：

```python
# ❌ 错误：只添加一个括号
old: "    })"
new: "    }))"

# ✅ 正确：理解完整的调用结构
response = client.post("/books/", json={
    "isbn": "9787532767405",
    "title": "解忧杂货店",
    # ... 完整的字典内容
})  # 这里需要完整的函数调用结束
```

## 重复代码问题

### 识别模式

如果看到这样的代码：
```python
def test_add_book(client):
    response = client.post("/books/", json={...})
    response = client.post("/books/", json={...})  # 重复
    assert response.status_code == 200
    assert response.status_code == 200  # 重复
```

### 修复策略

1. **删除重复部分**，而不是修改缩进
2. **理解测试意图**：
   - 是要测试添加两本不同的书？→ 使用不同的ISBN
   - 是复制粘贴错误？→ 删除重复部分

## 完整文件重写策略

当错误超过3个时，考虑重写整个文件：

```python
# 1. 先读取文件理解结构
content = read_file("tests/test_books.py")

# 2. 分析问题
# - 缩进混乱
# - 括号不匹配
# - 代码重复

# 3. 完整重写
new_content = '''
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import init_db

@pytest.fixture(scope="module")
def client():
    init_db()
    return TestClient(app)

def test_add_book(client):
    """测试添加图书"""
    response = client.post("/books/", json={
        "isbn": "9787532767406",
        "title": "解忧杂货店",
        "author": "[日] 东野圭吾",
        "publisher": "南海出版公司",
        "publish_year": 2014,
        "category": "小说",
        "total_quantity": 10,
        "available_quantity": 10,
        "location": "A-1-1"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "解忧杂货店"
    assert data["isbn"] == "9787532767406"

def test_add_duplicate_book(client):
    """测试添加重复图书"""
    # 第一次添加
    response = client.post("/books/", json={
        "isbn": "9787532767407",
        "title": "白夜行",
        "author": "[日] 东野圭吾",
        "publisher": "南海出版公司",
        "publish_year": 2013,
        "category": "小说",
        "total_quantity": 5,
        "available_quantity": 5,
        "location": "A-1-2"
    })
    assert response.status_code == 200
    
    # 尝试添加相同ISBN的书
    response = client.post("/books/", json={
        "isbn": "9787532767407",
        "title": "白夜行",
        "author": "[日] 东野圭吾",
        "publisher": "南海出版公司",
        "publish_year": 2013,
        "category": "小说",
        "total_quantity": 5,
        "available_quantity": 5,
        "location": "A-1-2"
    })
    assert response.status_code == 400  # 应该返回错误
'''

write_file("tests/test_books.py", new_content)
```

## 防止反复修复的检查点

在debug_notes.json中记录：

```json
{
  "fix_attempts": [
    {
      "error_id": "error_002",
      "strategy": "整体重写文件",  // 不是"修复缩进"
      "complete_rewrite": true,      // 标记为完整重写
      "actions": [{
        "type": "write_file",        // 使用write_file而不是edit_lines
        "file": "tests/test_books.py",
        "description": "完整重写测试文件，修复所有语法和缩进问题"
      }]
    }
  ],
  "lessons_learned": [
    {
      "lesson": "Python语法错误需要整体修复，不要逐行修改",
      "context": "多个缩进和括号错误同时出现"
    }
  ]
}
```

## 最重要的规则

1. **看到缩进错误 → 重写整个函数**
2. **看到括号不匹配 → 重写整个语句块**
3. **看到重复代码 → 理解意图后完整重构**
4. **错误超过3个 → 考虑重写整个文件**

记住：Python代码的结构是整体的，局部修复往往会引入新问题！