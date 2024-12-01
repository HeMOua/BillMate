import pdfplumber
import pandas as pd
from tqdm import tqdm
from datetime import datetime
from bill_parser.base import BillParserStrategy
from intelli_classifier.classifier import classify_consume_type
from utils import build_data_structure, get_categories, run_in_thread_pool

__all__ = ['ICBCBillParser']


# 具体策略：解析工商银行账单（PDF）
class ICBCBillParser(BillParserStrategy):
    
    def filter_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """过滤不需要的数据"""
        # 筛选有效数据并计算总数
        valid_rows = df[df["交易金额"].notna()]
        
        print('工商银行账单处理'.center(80, '*'))
        print(f"总记录数: {len(df)}")
        print(f"无效记录数: {len(df) - len(valid_rows)}")
        print(f"有效记录数: {len(valid_rows)}")
        
        return valid_rows

    def add_line(self, table_data, row):
        cate, subcate = classify_consume_type(str(row), get_categories("支出"), True)
        
        # 解析原始数据
        col_time = datetime.strptime(row["交易日期"], "%Y%m%d").strftime("%Y-%m-%d %H:%M")
        # 根据金额正负判断收支类型
        amount = float(row["交易金额"])
        col_type = "支出" if amount < 0 else "收入"
        col_category = cate
        col_subcategory = subcate
        col_amount = amount
        col_ledger = "日常生活"
        col_fromaccount = "工商银行" if col_type == "支出" else row["对方户名"]
        col_toaccount = row["对方户名"] if col_type == "支出" else "工商银行"
        col_notes = f'{row["交易类型"]}\n{row["交易说明"]}'

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
        try:
            # 尝试直接打开PDF
            pdf = pdfplumber.open(file_path)
        except:
            # 如果打开失败,提示用户输入密码
            password = "462402"
            try:
                pdf = pdfplumber.open(file_path, password=password)
            except:
                raise ValueError("密码错误或PDF文件损坏")
        
        with pdf as pdf:
            data = []
            for page in pdf.pages:
                table = page.extract_table()
                if table:
                    data.extend(table)
            
            # 假设 PDF 表格的列名
            columns = ["交易日期", "交易时间", "交易类型", "交易金额", "账户余额", "对方户名", "对方账号", "交易说明"]
            df = pd.DataFrame(data[1:], columns=columns)
            
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