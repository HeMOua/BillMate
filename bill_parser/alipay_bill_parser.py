import pandas as pd
from tqdm import tqdm
from datetime import datetime
from bill_parser.base import BillParserStrategy
from intelli_classifier.classifier import classify_consume_type
from utils import build_data_structure, find_table_start, detect_encoding, get_categories, run_in_thread_pool

__all__ = ["AlipayBillParser"]


# 具体策略：解析支付宝账单
class AlipayBillParser(BillParserStrategy):
    
    def filter_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """过滤不需要的数据"""
        # 筛选有效数据并计算总数
        valid_type_rows = df[df["收/支"].isin(["支出", "收入"])]
        zero_amount_rows = valid_type_rows[valid_type_rows["金额"] == 0]
        valid_rows = valid_type_rows[valid_type_rows["金额"] != 0]
        
        print('支付宝账单处理'.center(80, '*'))
        print(f"总记录数: {len(df)}")
        print(f"收支类型无效记录数: {len(df) - len(valid_type_rows)}")
        print(f"金额为0的记录数: {len(zero_amount_rows)}")
        print(f"有效记录数: {len(valid_rows)}")
        
        return valid_rows

    def add_line(self, table_data, row):
        cate, subcate = classify_consume_type(str(row), get_categories("支出"), True)
        
        # 解析原始数据
        col_time = datetime.strptime(row["交易时间"], "%Y-%m-%d %H:%M:%S").strftime(
            "%Y-%m-%d %H:%M"
        )
        col_type = "支出" if row["收/支"] == "支出" else "收入"
        col_category = cate
        col_subcategory = subcate
        col_amount = (
            -float(row["金额"]) if col_type == "支出" else float(row["金额"])
        )
        col_ledger = "日常生活"  # 假设账本固定为"日常生活"，可根据实际分类逻辑修改
        col_fromaccount = "支付宝"  # row["收/付款方式"]
        col_toaccount = ""  # 暂无对应字段
        note = f'\n{row["备注"]}' if pd.notna(row["备注"]) else ""
        col_notes = f'{row["商品说明"]}{note}'

        # 添加到输出数据中
        table_data["账单时间"].append(col_time)
        table_data["类型"].append(col_type)
        table_data["分类"].append(col_category)
        table_data["子分类"].append(col_subcategory)
        table_data["金额"].append(col_amount)
        table_data["账本"].append(col_ledger)
        table_data["账户1"].append(col_fromaccount)
        table_data["账户2"].append(col_toaccount)
        table_data["备注"].append(col_notes)

    def parse(self, file_path):
        encoding = detect_encoding(file_path)
        start_row = find_table_start(file_path, encoding=encoding)
        df = pd.read_csv(
            file_path, encoding=encoding, encoding_errors="ignore", skiprows=start_row
        )

        # 定义目标数据框的结构
        output_data = build_data_structure()
        
        # 过滤数据
        valid_rows = self.filter_data(df)
        total_count = len(valid_rows)
        
        params = [{'table_data': output_data, 'row': row} for idx, row in valid_rows.iterrows()]

        list(tqdm(run_in_thread_pool(self.add_line, params), total=total_count, desc="处理支付宝账单"))

        return pd.DataFrame(output_data)
