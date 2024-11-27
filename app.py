from pathlib import Path
from bill_parser import *
from bill_merger import BillMerger
from intelli_classifier.classifier import query_expenditure


ROOT = Path(__file__).parent


if __name__ == "__main__":
    print(
        query_expenditure(
            "文化休闲	App Store & Apple Music	tpa***@apple.com	App Store & Apple Music；10.02购买	支出	10	余额宝	交易成功",
            "支出",
        )
    )


# 使用
if __name__ == "__main__1":
    # 初始化合并器
    merger = BillMerger(ROOT / "data")

    # 注册解析策略
    merger.register_parser("wechat", WeChatBillParser())
    merger.register_parser("alipay", AlipayBillParser())
    merger.register_parser("icbc", ICBCBillParser())

    # 提供文件路径
    bill_files = {
        "alipay": "alipay/alipay_record_20241111_123826.csv",
        # "wechat": "wechat/微信支付账单(20240618-20240918).csv",
        # "icbc": "icbc/工商银行历史明细（申请单号：24111112531627610959）.pdf",
    }

    # 合并账单
    merged_bill = merger.merge_bills(bill_files)
    print(merged_bill)

    # 保存合并后的账单
    merged_bill.to_excel("merged_bill.xlsx", index=False)
