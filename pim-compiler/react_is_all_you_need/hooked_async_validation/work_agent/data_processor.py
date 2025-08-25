import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
import logging

class DataProcessor:
    """
    数据处理工具类，用于处理CSV数据，包括读取和清洗功能
    """
    
    def __init__(self):
        """初始化数据处理器"""
        self.data = None
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """设置日志记录器"""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger
    
    def read_csv(self, file_path: str) -> pd.DataFrame:
        """
        读取CSV文件
        
        Args:
            file_path (str): CSV文件路径
            
        Returns:
            pd.DataFrame: 读取的数据
            
        Raises:
            FileNotFoundError: 文件未找到
            pd.errors.EmptyDataError: 文件为空
            pd.errors.ParserError: 解析错误
        """
        try:
            self.data = pd.read_csv(file_path)
            self.logger.info(f"成功读取CSV文件: {file_path}")
            self.logger.info(f"数据形状: {self.data.shape}")
            return self.data
        except FileNotFoundError:
            self.logger.error(f"文件未找到: {file_path}")
            raise
        except pd.errors.EmptyDataError:
            self.logger.error(f"文件为空: {file_path}")
            raise
        except pd.errors.ParserError:
            self.logger.error(f"CSV解析错误: {file_path}")
            raise
        except Exception as e:
            self.logger.error(f"读取CSV时发生未知错误: {str(e)}")
            raise
    
    def clean_data(self, 
                   remove_duplicates: bool = True,
                   handle_missing: str = 'drop',
                   remove_columns: Optional[List[str]] = None) -> pd.DataFrame:
        """
        清洗数据
        
        Args:
            remove_duplicates (bool): 是否删除重复行，默认True
            handle_missing (str): 处理缺失值的方式 ('drop', 'fill_mean', 'fill_median', 'fill_zero')
            remove_columns (List[str], optional): 要删除的列名列表
            
        Returns:
            pd.DataFrame: 清洗后的数据
        """
        if self.data is None:
            raise ValueError("数据未加载，请先调用read_csv方法")
        
        cleaned_data = self.data.copy()
        self.logger.info("开始数据清洗...")
        
        # 删除指定列
        if remove_columns:
            existing_columns = [col for col in remove_columns if col in cleaned_data.columns]
            if existing_columns:
                cleaned_data = cleaned_data.drop(columns=existing_columns)
                self.logger.info(f"删除列: {existing_columns}")
            missing_columns = [col for col in remove_columns if col not in cleaned_data.columns]
            if missing_columns:
                self.logger.warning(f"以下列不存在，无法删除: {missing_columns}")
        
        # 删除重复行
        if remove_duplicates:
            initial_rows = cleaned_data.shape[0]
            cleaned_data = cleaned_data.drop_duplicates()
            removed_rows = initial_rows - cleaned_data.shape[0]
            if removed_rows > 0:
                self.logger.info(f"删除了 {removed_rows} 行重复数据")
        
        # 处理缺失值
        if handle_missing == 'drop':
            initial_rows = cleaned_data.shape[0]
            cleaned_data = cleaned_data.dropna()
            removed_rows = initial_rows - cleaned_data.shape[0]
            if removed_rows > 0:
                self.logger.info(f"删除了 {removed_rows} 行包含缺失值的数据")
        elif handle_missing in ['fill_mean', 'fill_median', 'fill_zero']:
            numeric_columns = cleaned_data.select_dtypes(include=[np.number]).columns
            if len(numeric_columns) > 0:
                if handle_missing == 'fill_mean':
                    cleaned_data[numeric_columns] = cleaned_data[numeric_columns].fillna(
                        cleaned_data[numeric_columns].mean()
                    )
                    self.logger.info("使用均值填充数值列的缺失值")
                elif handle_missing == 'fill_median':
                    cleaned_data[numeric_columns] = cleaned_data[numeric_columns].fillna(
                        cleaned_data[numeric_columns].median()
                    )
                    self.logger.info("使用中位数填充数值列的缺失值")
                elif handle_missing == 'fill_zero':
                    cleaned_data[numeric_columns] = cleaned_data[numeric_columns].fillna(0)
                    self.logger.info("使用0填充数值列的缺失值")
        
        self.logger.info(f"清洗完成，最终数据形状: {cleaned_data.shape}")
        self.data = cleaned_data
        return cleaned_data
    
    def get_data_info(self) -> Dict[str, Any]:
        """
        获取数据信息
        
        Returns:
            Dict[str, Any]: 数据信息字典
        """
        if self.data is None:
            raise ValueError("数据未加载，请先调用read_csv方法")
        
        info = {
            'shape': self.data.shape,
            'columns': list(self.data.columns),
            'missing_values': self.data.isnull().sum().to_dict(),
            'data_types': self.data.dtypes.to_dict(),
            'duplicate_rows': self.data.duplicated().sum()
        }
        return info
    
    def save_data(self, file_path: str, index: bool = False) -> None:
        """
        保存数据到CSV文件
        
        Args:
            file_path (str): 保存文件路径
            index (bool): 是否保存索引，默认False
        """
        if self.data is None:
            raise ValueError("数据未加载，请先调用read_csv方法")
        
        self.data.to_csv(file_path, index=index)
        self.logger.info(f"数据已保存到: {file_path}")

# 使用示例
if __name__ == "__main__":
    # 创建示例数据
    sample_data = pd.DataFrame({
        'name': ['Alice', 'Bob', 'Charlie', 'Alice', None],
        'age': [25, 30, 35, 25, np.nan],
        'city': ['New York', 'London', 'Paris', 'New York', 'Tokyo'],
        'salary': [50000, 60000, np.nan, 50000, 70000]
    })
    sample_data.to_csv('sample_data.csv', index=False)
    
    # 使用数据处理器
    processor = DataProcessor()
    data = processor.read_csv('sample_data.csv')
    print("原始数据:")
    print(data)
    
    # 清洗数据
    cleaned_data = processor.clean_data(
        remove_duplicates=True,
        handle_missing='fill_mean'
    )
    print("\n清洗后的数据:")
    print(cleaned_data)
    
    # 获取数据信息
    info = processor.get_data_info()
    print("\n数据信息:")
    for key, value in info.items():
        print(f"{key}: {value}")