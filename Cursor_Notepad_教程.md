# Cursor 中的 Notepad 教程

## 概述

Cursor 的 Notepad 是一个强大的内置笔记功能，让您可以在编辑器中快速记录想法、代码片段、任务列表等，而无需离开开发环境。

## 快速开始

### 打开 Notepad

1. **快捷键方式**：

   - `Ctrl+Shift+N` (Windows/Linux)
   - `Cmd+Shift+N` (Mac)

2. **命令面板方式**：

   - 按 `Ctrl+Shift+P` 打开命令面板
   - 输入 "Notepad" 并选择 "Notepad: Open"

3. **菜单方式**：
   - 点击顶部菜单 `View` → `Notepad`

### 基本界面

Notepad 会在编辑器右侧打开一个面板，包含：

- **笔记列表**：显示所有保存的笔记
- **编辑区域**：当前选中笔记的内容编辑区
- **工具栏**：新建、保存、删除等操作按钮

## 核心功能

### 1. 创建笔记

````markdown
# 我的第一个笔记

## 项目想法

- 创建一个任务管理应用
- 使用 React + TypeScript
- 集成 AI 功能

## 代码片段

```javascript
const hello = () => {
  console.log("Hello, Cursor!");
};
```
````

## 待办事项

- [ ] 设置开发环境
- [ ] 创建项目结构
- [ ] 实现基础功能

````

### 2. 笔记管理

#### 新建笔记
- 点击工具栏的 `+` 按钮
- 或使用快捷键 `Ctrl+N` (在Notepad面板中)

#### 保存笔记
- 自动保存：Notepad会自动保存您的更改
- 手动保存：`Ctrl+S` (在Notepad面板中)

#### 删除笔记
- 选中笔记后点击垃圾桶图标
- 或右键选择"Delete"

#### 重命名笔记
- 双击笔记标题进行编辑
- 或右键选择"Rename"

### 3. 格式化支持

Notepad支持Markdown格式：

```markdown
# 标题1
## 标题2
### 标题3

**粗体文本**
*斜体文本*
`代码片段`

- 无序列表项1
- 无序列表项2

1. 有序列表项1
2. 有序列表项2

[链接文本](URL)

![图片描述](图片URL)

> 引用文本

```python
def hello_world():
    print("Hello, World!")
````

| 表头 1 | 表头 2 |
| ------ | ------ |
| 内容 1 | 内容 2 |

`````

### 4. 代码高亮

Notepad支持代码块语法高亮：

````markdown
```javascript
// JavaScript代码
function greet(name) {
  return `Hello, ${name}!`;
}
`````

```python
# Python代码
def greet(name):
    return f"Hello, {name}!"
```

```css
/* CSS代码 */
.greeting {
  color: blue;
  font-size: 18px;
}
```

````

## 高级功能

### 1. 笔记分类

使用文件夹组织笔记：

```markdown
# 项目笔记
## 前端开发
- React组件设计
- 状态管理方案

## 后端开发
- API设计
- 数据库结构

## 部署相关
- Docker配置
- CI/CD流程
```

### 2. 快速搜索

- 使用 `Ctrl+F` 在当前笔记中搜索
- 使用 `Ctrl+Shift+F` 在所有笔记中搜索

### 3. 导出功能

可以将笔记导出为：
- Markdown文件 (.md)
- 纯文本文件 (.txt)
- HTML文件 (.html)

### 4. 同步功能

如果启用了Cursor的同步功能，您的笔记会在不同设备间同步。

## 使用场景

### 1. 项目开发笔记

```markdown
# 项目开发日志

## 2024-01-15
### 完成功能
- 用户认证系统
- 数据库连接配置

### 遇到的问题
- 跨域请求问题
- 解决方案：配置CORS中间件

### 下一步计划
- [ ] 实现用户权限管理
- [ ] 添加日志记录功能
```

### 2. 代码片段收集

```markdown
# 常用代码片段

## React Hooks
```javascript
// 自定义Hook：useLocalStorage
function useLocalStorage(key, initialValue) {
  const [storedValue, setStoredValue] = useState(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      return initialValue;
    }
  });

  const setValue = value => {
    try {
      setStoredValue(value);
      window.localStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
      console.log(error);
    }
  };

  return [storedValue, setValue];
}
```

## Python工具函数
```python
# 文件操作工具
import os
import shutil

def safe_copy(src, dst):
    """安全复制文件，如果目标存在则备份"""
    if os.path.exists(dst):
        backup = dst + '.backup'
        shutil.copy2(dst, backup)
    shutil.copy2(src, dst)
```
```

### 3. 学习笔记

```markdown
# 学习笔记：TypeScript高级特性

## 泛型
- 提供类型安全的代码复用
- 语法：`function identity<T>(arg: T): T`

## 装饰器
- 用于类、方法、属性的元编程
- 语法：`@decorator`

## 高级类型
- 联合类型：`string | number`
- 交叉类型：`A & B`
- 条件类型：`T extends U ? X : Y`
```

### 4. 会议记录

```markdown
# 团队会议记录

## 会议信息
- 日期：2024-01-15
- 时间：14:00-15:30
- 参与者：张三、李四、王五

## 讨论内容
1. 项目进度回顾
2. 技术方案讨论
3. 下一步计划

## 决策事项
- [x] 采用React 18新特性
- [x] 使用TypeScript进行类型检查
- [ ] 下周完成用户界面设计

## 行动项
- 张三：负责组件库搭建
- 李四：负责API接口设计
- 王五：负责测试用例编写
```

## 快捷键参考

| 功能 | Windows/Linux | Mac |
|------|---------------|-----|
| 打开Notepad | `Ctrl+Shift+N` | `Cmd+Shift+N` |
| 新建笔记 | `Ctrl+N` | `Cmd+N` |
| 保存笔记 | `Ctrl+S` | `Cmd+S` |
| 搜索笔记 | `Ctrl+F` | `Cmd+F` |
| 全局搜索 | `Ctrl+Shift+F` | `Cmd+Shift+F` |
| 删除笔记 | `Delete` | `Delete` |

## 最佳实践

### 1. 笔记组织
- 使用清晰的标题结构
- 按项目或主题分类
- 定期整理和归档

### 2. 内容管理
- 使用Markdown格式保持一致性
- 添加日期和标签便于查找
- 定期备份重要笔记

### 3. 工作流程
- 在开发前记录需求和计划
- 开发过程中记录问题和解决方案
- 完成后总结经验和教训

## 常见问题

### Q: 笔记保存在哪里？
A: 笔记保存在Cursor的本地配置目录中，具体位置因操作系统而异。

### Q: 可以导入现有的Markdown文件吗？
A: 目前Notepad主要支持在内部创建和编辑，但可以通过复制粘贴的方式导入内容。

### Q: 笔记会占用太多存储空间吗？
A: 不会，Notepad使用纯文本格式，占用空间很小。

### Q: 可以与他人共享笔记吗？
A: 如果启用了Cursor的同步功能，可以在不同设备间同步，但无法直接与他人共享。

## 总结

Cursor的Notepad是一个简单而强大的笔记工具，特别适合开发者在编码过程中快速记录想法、代码片段和项目信息。通过合理使用，可以显著提高开发效率和知识管理能力。

记住：好的笔记习惯是优秀开发者的重要技能之一！
````
