# 数据处理工具

这是一个用于处理CSV数据的Python工具，包含数据读取、清洗和保存功能。

## 功能特性

1. **CSV读取**: 安全地读取CSV文件，包含错误处理
2. **数据清洗**: 
   - 删除重复行
   - 处理缺失值（删除或填充）
   - 删除指定列
3. **数据信息**: 获取数据的基本信息和统计
4. **数据保存**: 将处理后的数据保存到CSV文件

## 安装依赖

```bash
pip install pandas numpy
```

## 使用方法

### 基本使用

```python
from data_processor import DataProcessor

# 创建处理器实例
processor = DataProcessor()

# 读取CSV文件
data = processor.read_csv('your_data.csv')

# 清洗数据
cleaned_data = processor.clean_data(
    remove_duplicates=True,
    handle_missing='fill_mean'
)

# 保存清洗后的数据
processor.save_data('cleaned_data.csv')
```

### 高级选项

```python
# 删除指定列
cleaned_data = processor.clean_data(
    remove_columns=['unnecessary_column']
)

# 用中位数填充缺失值
cleaned_data = processor.clean_data(
    handle_missing='fill_median'
)

# 获取数据信息
info = processor.get_data_info()
print(info)
```

## 运行测试

```bash
python -m pytest test_processor.py -v
```

## 示例

运行示例代码查看工具的完整使用方法：

```bash
python example_usage.py
```