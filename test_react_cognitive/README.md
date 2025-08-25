# 计数器模块

这是一个简单的计数器模块，提供了计数器的基本功能：增加、减少和重置。

## 功能特性

- 增加计数器的值 (increment)
- 减少计数器的值 (decrement)
- 重置计数器的值 (reset)
- 获取当前计数器的值 (get_value)

## 使用方法

### 1. 使用全局计数器函数

模块提供了全局计数器函数，可以直接使用：

```python
import counter

# 增加计数器
counter.increment()     # 默认增加1
counter.increment(5)    # 增加指定值

# 减少计数器
counter.decrement()     # 默认减少1
counter.decrement(3)    # 减少指定值

# 重置计数器
counter.reset()         # 重置为0
counter.reset(10)       # 重置为指定值

# 获取当前值
current_value = counter.get_value()
```

### 2. 使用Counter类

如果需要多个独立的计数器，可以使用Counter类：

```python
import counter

# 创建计数器实例
my_counter = counter.Counter()      # 默认初始值为0
your_counter = counter.Counter(10)  # 指定初始值为10

# 使用计数器方法
my_counter.increment()
my_counter.decrement(2)
my_counter.reset(5)
current_value = my_counter.get_value()
```

## 运行示例

运行示例程序查看功能演示：

```bash
python example.py
```

## 方法说明

### 全局函数

- `increment(step=1)`: 增加计数器的值，默认增加1
- `decrement(step=1)`: 减少计数器的值，默认减少1
- `reset(value=0)`: 重置计数器的值，默认重置为0
- `get_value()`: 获取当前计数器的值

### Counter类方法

- `Counter(initial_value=0)`: 构造函数，创建一个新的计数器
- `increment(step=1)`: 增加计数器的值，默认增加1
- `decrement(step=1)`: 减少计数器的值，默认减少1
- `reset(value=0)`: 重置计数器的值，默认重置为0
- `get_value()`: 获取当前计数器的值