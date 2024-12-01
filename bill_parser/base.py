import pandas as pd
from abc import ABC, abstractmethod

# 定义抽象策略
class BillParserStrategy(ABC):
    
    @abstractmethod
    def filter_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """过滤不需要的数据"""
        pass

    @abstractmethod
    def parse(self, file_path):
        """解析账单并返回 DataFrame"""
        pass