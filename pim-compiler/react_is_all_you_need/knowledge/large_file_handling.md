# 大文件处理知识

## 处理策略

当遇到大文件（超过1000字符）时，使用分段读取策略：

### 1. 评估文件大小
首先使用 `execute_command` 检查文件大小：
```bash
wc -c filename  # 字节数
wc -l filename  # 行数
```

### 2. 分段读取方案

#### 方案A：使用系统命令（推荐）
```bash
# 读取特定行范围
sed -n '100,200p' file.py  # 读取100-200行

# 读取前N行
head -100 file.py

# 读取后N行
tail -100 file.py

# 组合使用
head -200 file.py | tail -100  # 读取101-200行
```

#### 方案B：使用Python脚本
```python
execute_command("""python3 -c "
with open('file.py') as f:
    lines = f.readlines()
    print(''.join(lines[100:200]))  # 读取100-200行
"
""")
```

### 3. 智能分段策略

对于不同类型的文件：

#### Python文件
- 优先读取文件头部（imports和类定义）
- 然后读取特定函数（搜索def关键字）
- 最后读取主程序部分

#### 配置文件
- 通常较小，可以完整读取
- 或按section分段读取

#### 日志文件
- 优先读取最新内容（tail）
- 或搜索特定时间段

### 4. 内容定位技巧

```bash
# 搜索函数定义
grep -n "def function_name" file.py  # 获取行号

# 搜索类定义
grep -n "class ClassName" file.py

# 然后用sed读取该函数/类的内容
sed -n '150,200p' file.py  # 假设函数在150-200行
```

### 5. 决策流程

```
文件读取请求
├── 文件 < 2000字符 → 直接read_file
├── 文件 > 2000字符
│   ├── 需要完整内容 → 分段读取
│   └── 需要特定部分 → 定位后精确读取
└── 文件 > 10000字符 → 先分析结构，再有针对性读取
```

## 最佳实践

1. **先了解后读取** - 先用wc/grep了解文件结构
2. **按需读取** - 只读取需要的部分
3. **智能分段** - 根据文件类型选择分段策略
4. **避免重复** - 记住已读取的部分

## 注意事项

- read_file工具现在支持offset和limit参数（如果可用）
- execute_command的输出也有限制（约500字符）
- 对于超大文件，考虑先生成摘要