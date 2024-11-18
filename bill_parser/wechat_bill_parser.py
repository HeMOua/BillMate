import pandas as pd
from abc import ABC, abstractmethod
from bill_parser.base import BillParserStrategy

__all__ = ['WeChatBillParser']


# 具体策略：解析微信账单
class WeChatBillParser(BillParserStrategy):
    def parse(self, file_path):
        return pd.read_excel(file_path)
