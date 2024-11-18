import pandas as pd
from abc import ABC, abstractmethod
from bill_parser.base import BillParserStrategy
import pdfplumber

__all__ = ['ICBCBillParser']


# 具体策略：解析工商银行账单（PDF）
class ICBCBillParser(BillParserStrategy):
    def parse(self, file_path):
        with pdfplumber.open(file_path) as pdf:
            data = []
            for page in pdf.pages:
                table = page.extract_table()
                if table:
                    data.extend(table)
            # 假设 PDF 表格的第一行是列名
            df = pd.DataFrame(data[1:], columns=data[0])
        return df