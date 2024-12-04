import chardet
import json
import multiprocessing as mp
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, Dict, Generator, List, Literal

ROOT = Path(__file__).parents[1]


def load_json(path: Path):
    with open(path.resolve(), "r", encoding="utf-8") as f:
        return json.load(f)


def get_txt_content(file_path):
    """获取文本文件的内容"""
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def get_categories(cate: Literal["支出", "收入"]):
    categories = load_json(ROOT / "categories.json")

    def get_category_by_type(type: Literal["支出", "收入"]):
        for category in categories:
            if category["name"] == type:
                return category["children"]
        return []

    return get_category_by_type(cate)


# 构建数据结构
def build_data_structure(fields=None):
    default_fields = [
        "账单时间",
        "类型",
        "分类",
        "子分类",
        "金额",
        "账本",
        "账户1",
        "账户2",
        "备注",
    ]
    fields = fields or default_fields
    return {field: [] for field in fields}


# 获取文件数据第一行
def find_table_start(file_path):
    with open(file_path, "rb") as f:
        for i, line in enumerate(f):
            if "交易时间" in str(line):  # 根据某列名判断表头行
                return i
    return -1


def detect_encoding(file_path):
    with open(file_path, "rb") as f:
        data = f.read(1024)
        return chardet.detect(data)["encoding"] or "utf-8"  # 回退到 utf-8


def find_table_start(file_path, encoding="auto", header_keyword="交易时间"):
    """
    查找表头所在的行号。

    参数:
        - file_path: 文件路径
        - encoding: 文件编码 ("auto" 表示自动检测)
        - header_keyword: 表头的关键字，用于判断表头行

    返回:
        - 表头行号 (0-based)，如果未找到返回 -1
    """
    # 自动检测编码
    if encoding == "auto":
        encoding = detect_encoding(file_path)

    try:
        with open(file_path, "r", encoding=encoding, errors="ignore") as f:
            for i, line in enumerate(f):
                if header_keyword in line:  # 判断表头关键字是否在当前行
                    return i
    except Exception as e:
        print(f"Error reading file: {e}")

    return -1


def run_in_thread_pool(func: Callable, params: List[Dict]) -> Generator:
    """
    使用线程池并发执行函数。

    Args:
        func (Callable): 要并发执行的函数。
        params (List[Dict]): 函数的参数列表。

    Returns:
        Generator: 函数执行结果的生成器。
    """
    max_workers = min(mp.cpu_count(), len(params))

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        tasks = [executor.submit(func, **param) for param in params]

        for task in as_completed(tasks):
            try:
                yield task.result()
            except Exception as e:
                print(f"Error in thread pool: {e}")
