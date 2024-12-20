from pathlib import Path
from bill_parser import *
from bill_merger.base import BillMerger
from intelli_classifier.classifier import classify_consume_type
from utils.general import get_categories


ROOT = Path(__file__).parent


if __name__ == "__main__":
    root_path = ROOT / "data"
    
    # 初始化合并器
    merger = BillMerger(root_path)

    # 注册解析策略
    merger.register_parser("wechat", WeChatBillParser())
    merger.register_parser("alipay", AlipayBillParser())
    merger.register_parser("icbc", ICBCBillParser())

    # 提供文件路径
    bill_files = {
        "alipay": "alipay/alipay_record_20241205_220221.csv",
        "wechat": "wechat/微信支付账单(20240621-20241130).csv",
        "icbc": "icbc/hisdetail1733407445806.csv",
    }

    # 合并账单
    merged_bill = merger.merge_bills(bill_files)

    # 保存合并后的账单
    merged_bill.to_excel(root_path / "merged_bill.xlsx", index=False)

    print(f"账单合并完成，保存到 {root_path / 'merged_bill.xlsx'}")
