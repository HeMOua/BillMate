import pandas as pd
from bill_parser.base import BillParserStrategy

from utils import detect_encoding, find_table_start

__all__ = ["WeChatBillParser"]


# 具体策略：解析微信账单
class WeChatBillParser(BillParserStrategy):
    def parse(self, file_path):
        encoding = detect_encoding(file_path)
        start_row = find_table_start(file_path)
        df = pd.read_csv(
            file_path, encoding=encoding, encoding_errors="ignore", skiprows=start_row
        )
        return df
