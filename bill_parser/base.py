from abc import ABC, abstractmethod


# 定义抽象策略
class BillParserStrategy(ABC):
    @abstractmethod
    def parse(self, file_path):
        """解析账单并返回 DataFrame"""
        pass