from bill_parser import *
from bill_merger import BillMerger


# 使用
if __name__ == "__main__":
    # 初始化合并器
    merger = BillMerger()

    # 注册解析策略
    merger.register_parser("wechat", WeChatBillParser())
    merger.register_parser("alipay", AlipayBillParser())
    merger.register_parser("icbc", ICBCBillParser())

    # 提供文件路径
    bill_files = {
        "wechat": "wechat_bill.xlsx",
        "alipay": "alipay_bill.xlsx",
        "icbc": "icbc_bill.pdf"
    }

    # 合并账单
    merged_bill = merger.merge_bills(bill_files)
    print(merged_bill)

    # 保存合并后的账单
    merged_bill.to_excel("merged_bill.xlsx", index=False)
