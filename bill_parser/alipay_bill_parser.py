import datetime
import pandas as pd
from bill_parser.base import BillParserStrategy

from utils import build_output_data_structure

__all__ = ['AlipayBillParser']


# 具体策略：解析支付宝账单
class AlipayBillParser(BillParserStrategy):

    

    def parse(self, file_path):
        df = pd.read_csv(file_path, encoding='utf-8')

        # 定义目标数据框的结构
        output_data = build_output_data_structure()

        # 遍历原始数据并填充目标数据
        for index, row in df.iterrows():
            col_time = datetime.strptime(row["交易时间"], "%Y/%m/%d %H:%M").strftime("%Y-%m-%d %H:%M")
            col_type = "支出" if row["收/支"] == "支出" else "收入"
            col_category = row["交易分类"]
            col_subcategory = ""  # 子分类信息缺失，可手动填充
            col_amount = -float(row["金额"]) if col_type == "支出" else float(row["金额"])
            col_ledger = "日常生活"  # 假设账本固定为“日常生活”，可根据实际分类逻辑修改
            col_fromaccount = row["收/付款方式"]
            col_toaccount = ""  # 暂无对应字段
            col_notes = row["备注"]

            # 添加到输出数据中
            output_data["时间"].append(col_time)
            output_data["类型"].append(col_type)
            output_data["分类"].append(col_category)
            output_data["子分类"].append(col_subcategory)
            output_data["金额"].append(col_amount)
            output_data["账本"].append(col_ledger)
            output_data["转出账户"].append(col_fromaccount)
            output_data["转入账户"].append(col_toaccount)
            output_data["备注"].append(col_notes)

        return pd.DataFrame(output_data)