import pandas as pd
from tqdm import tqdm
from datetime import datetime
from bill_parser.base import BillParserStrategy
from intelli_classifier.classifier import classify_consume_type
from utils.general import build_data_structure, detect_encoding, find_table_start, get_categories, run_in_thread_pool

__all__ = ['ICBCBillParser']


# 具体策略：解析工商银行账单（PDF）
class ICBCBillParser(BillParserStrategy):
    
    def filter_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """过滤不需要的数据"""
        valid_type_rows = df[
            ~(df["摘要"].str.contains("理财|基金", na=False)) & 
            ~(df["交易场所"].str.contains("基金|理财", na=False))
        ]
        
        print('工商银行账单处理'.center(80, '*'))
        print(f"总记录数: {len(df)}")
        print(f"收支类型无效记录数: {len(df) - len(valid_type_rows)}")
        print(f"有效记录数: {len(valid_type_rows)}")
        
        return valid_type_rows

    def add_line(self, table_data, row):

        # 去除首位空白符
        row = row.str.strip()
        # 解析原始数据
        col_time = datetime.strptime(row["交易日期"], "%Y-%m-%d").strftime("%Y-%m-%d %H:%M")
        col_type = "收入" if row["记账金额(收入)"] != '' else "支出"
        col_category, col_subcategory = classify_consume_type(str(row), get_categories(col_type), True)
        col_amount = -float(row["记账金额(支出)"].replace(",", "")) if col_type == "支出" else float(row["记账金额(收入)"].replace(",", ""))
        col_ledger = "日常生活"
        col_fromaccount = "工商银行"
        col_toaccount = ""
        col_notes = row["摘要"]

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
        start_row = find_table_start(file_path, encoding=encoding, header_keyword="交易日期")
        
        # 检查并修复表头行末尾的逗号
        with open(file_path, 'r', encoding=encoding) as f:
            lines = f.readlines()
            header_line = lines[start_row].strip()
            if not header_line.endswith(','):
                lines[start_row] = header_line + ',\n'
                with open(file_path, 'w', encoding=encoding) as f:
                    f.writelines(lines)

        df = pd.read_csv(
            file_path, encoding=encoding, encoding_errors="ignore", skiprows=start_row
        )

        # 忽略最后一行
        df = df.iloc[:-1]

        # 定义目标数据框的结构
        output_data = build_data_structure()
        
        # 过滤数据
        valid_rows = self.filter_data(df)
        total_count = len(valid_rows)
        
        # 构建参数列表
        params = [{'table_data': output_data, 'row': row} for idx, row in valid_rows.iterrows()]
        
        # 使用线程池处理数据
        list(tqdm(run_in_thread_pool(self.add_line, params), total=total_count, desc="处理工商银行账单"))
        
        # 返回处理后的DataFrame
        return pd.DataFrame(output_data)