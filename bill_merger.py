import pandas as pd
from typing import Dict

from bill_parser.base import BillParserStrategy


# 上下文类：账单合并器
class BillMerger:
    def __init__(self):
        self.parsers: Dict[str, BillParserStrategy] = {}

    def register_parser(self, bill_type, parser: BillParserStrategy):
        """注册账单解析策略"""
        self.parsers[bill_type] = parser

    def merge_bills(self, bill_files):
        """合并账单"""
        merged_df = pd.DataFrame()
        for bill_type, file_path in bill_files.items():
            parser = self.parsers.get(bill_type)
            if not parser:
                raise ValueError(f"No parser registered for bill type: {bill_type}")
            bill_df = parser.parse(file_path)
            merged_df = pd.concat([merged_df, bill_df], ignore_index=True)
        return merged_df
