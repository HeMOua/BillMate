import os
import pandas as pd
from typing import Dict
from pathlib import Path

from bill_parser.base import BillParserStrategy


# 上下文类：账单合并器
class BillMerger:
    def __init__(self, root_path):
        self.root_path = Path(root_path)
        self.parsers: Dict[str, BillParserStrategy] = {}

    def register_parser(self, bill_type, parser: BillParserStrategy):
        """注册账单解析策略"""
        self.parsers[bill_type] = parser

    def merge_bills(self, bill_files: dict):
        """合并账单"""
        columns = ["账单时间", "类型", "分类", "子分类", "金额", "账本", "账户1", "账户2", "备注", "账单图片", "报销", "优惠", "标签", "成员"]
        
        wait_merge_data = []
        for bill_type, file_path in bill_files.items():
            # 获取解析策略
            parser = self.parsers.get(bill_type)
            if not parser:
                raise ValueError(f"No parser registered for bill type: {bill_type}")
            bill_df = parser.parse(self.root_path / file_path)
            # 确保所有列都存在,不存在的列填充空值
            for col in columns:
                if col not in bill_df.columns:
                    bill_df[col] = None
            # 只保留指定的列
            bill_df = bill_df[columns]
            wait_merge_data.append(bill_df)
        
        if not wait_merge_data:
            raise ValueError("No data to merge")
        
        merged_df = pd.concat(wait_merge_data, ignore_index=True)
        # 按账单时间升序排序
        merged_df = merged_df.sort_values(by="账单时间", ascending=True)
        print(f"合并后的账单总记录数: {len(merged_df)}")
        return merged_df
