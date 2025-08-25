"""
数据处理工具使用示例
"""

import pandas as pd
import numpy as np
from data_processor import DataProcessor

def create_sample_data():
    """创建示例数据"""
    # 创建包含各种数据质量问题的示例数据
    data = pd.DataFrame({
        'id': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        'name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve', 'Frank', 'Grace', 'Henry', 'Ivy', 'Jack'],
        'age': [25, 30, np.nan, 40, 35, 28, 33, np.nan, 29, 31],
        'city': ['New York', 'London', 'Paris', 'New York', 'Tokyo', 'Berlin', 'London', 'Paris', 'New York', 'Tokyo'],
        'salary': [50000, 60000, 55000, np.nan, 70000, 52000, np.nan, 58000, 54000, 61000],
        'department': ['IT', 'HR', 'Finance', 'IT', 'Marketing', 'IT', 'HR', 'Finance', 'Marketing', 'IT']
    })
    
    # 添加一些重复行
    duplicate_row = pd.DataFrame({
        'id': [11],
        'name': ['Alice'],
        'age': [25],
        'city': ['New York'],
        'salary': [50000],
        'department': ['IT']
    })
    
    data = pd.concat([data, duplicate_row], ignore_index=True)
    
    # 保存到CSV文件
    data.to_csv('employee_data.csv', index=False)
    print("示例数据已创建并保存到 'employee_data.csv'")
    return data

def main():
    """主函数 - 演示数据处理工具的使用"""
    print("=== 数据处理工具使用示例 ===\n")
    
    # 创建示例数据
    sample_data = create_sample_data()
    print("原始数据:")
    print(sample_data)
    print(f"\n数据形状: {sample_data.shape}")
    print(f"缺失值统计:\n{sample_data.isnull().sum()}")
    print(f"重复行数量: {sample_data.duplicated().sum()}")
    
    print("\n" + "="*50 + "\n")
    
    # 使用数据处理器
    processor = DataProcessor()
    
    # 1. 读取数据
    print("1. 读取CSV数据...")
    data = processor.read_csv('employee_data.csv')
    
    # 2. 查看数据信息
    print("\n2. 数据信息:")
    info = processor.get_data_info()
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    print("\n3. 清洗数据...")
    # 3. 清洗数据 - 删除重复项，用均值填充缺失值
    cleaned_data = processor.clean_data(
        remove_duplicates=True,
        handle_missing='fill_mean'
    )
    
    print("\n4. 清洗后的数据:")
    print(cleaned_data)
    print(f"\n清洗后数据形状: {cleaned_data.shape}")
    
    # 4. 保存清洗后的数据
    print("\n5. 保存清洗后的数据...")
    processor.save_data('cleaned_employee_data.csv')
    
    print("\n数据处理完成！清洗后的数据已保存到 'cleaned_employee_data.csv'")
    
    # 5. 演示其他清洗选项
    print("\n" + "="*50)
    print("其他清洗选项演示:")
    
    # 重新读取原始数据
    processor2 = DataProcessor()
    processor2.read_csv('employee_data.csv')
    
    # 用中位数填充
    print("\n用中位数填充缺失值:")
    cleaned_with_median = processor2.clean_data(
        remove_duplicates=False,
        handle_missing='fill_median'
    )
    print(cleaned_with_median.head(5))  # 只显示前5行
    
    # 删除指定列
    print("\n删除 'department' 列:")
    processor3 = DataProcessor()
    processor3.read_csv('employee_data.csv')
    cleaned_drop_columns = processor3.clean_data(
        remove_columns=['department']
    )
    print("剩余的列:", cleaned_drop_columns.columns.tolist())
    print("数据形状:", cleaned_drop_columns.shape)

if __name__ == "__main__":
    main()