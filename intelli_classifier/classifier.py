from typing import List, Literal
from langchain_core.language_models import BaseChatModel
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama.llms import OllamaLLM
from jinja2 import Template
from utils.general import ROOT, get_categories, get_special_cases, get_txt_content


# 获取 Ollama 模型实例
def get_ollama(model="qwen2.5:latest", base_url="http://localhost:11434"):
    return OllamaLLM(model=model, base_url=base_url)


class CategoryClassifier:
    def __init__(self, llm: BaseChatModel):
        """初始化分类器"""
        self.llm = llm

    def _llm_classifier_query(self, text: str, categories: List[dict]) -> str:
        """
        分类器工具函数，借助大模型对输入文本进行分类，结合类别名和类别描述，并添加"其他"类别。

        参数:
        - text (str): 待分类文本
        - categories (list of dict): 分类类别列表，每个类别包含 'name' 和 'description'，
          例如：
          [
            {'name': '体育', 'description': '与运动和比赛相关的内容'},
            {'name': '科技', 'description': '与技术和科学有关的内容'}
          ]。

        返回:
        - class (str): 预测类别。
        """
        jinja_template = Template(get_txt_content(ROOT / "prompts/classifier.jinja"))
        prompt = jinja_template.render(text=text, categories=categories)
        chain = self.llm | StrOutputParser()
        return chain.invoke(prompt)

    def _wrapper_category(self, categories: List[dict]) -> List[dict]:
        """包装类别,只保留name字段"""
        return [{"name": category["name"]} for category in categories]

    def _get_category(self, categories: List[dict], name: str) -> dict:
        """根据名称获取类别"""
        for category in categories:
            if category["name"] == name:
                return category
        return None

    def _predict_category(self, text: str, current_categories: List[dict], current_depth: int, max_depth: int) -> List[str]:
        """递归预测类别"""
        # 如果已达到最大深度或没有类别,返回空列表
        if current_depth > max_depth or not current_categories:
            return []
            
        # 获取当前层级的类别
        wrapped_categories = self._wrapper_category(current_categories)
        
        # 使用大模型预测当前层级
        predicted = self._llm_classifier_query(text, wrapped_categories)
        
        # 验证预测类别是否存在
        category = self._get_category(current_categories, predicted)
        if not category:
            return ["其他"] + [""] * (max_depth - current_depth)
            
        # 递归预测下一层级
        if category.get("children"):
            sub_categories = self._predict_category(text, category["children"], current_depth + 1, max_depth)
            return [predicted] + sub_categories
        else:
            # 如果没有子类别,用空字符串填充剩余深度
            return [predicted] + [""] * (max_depth - current_depth)

    def classify(self, text: str, categories: List[dict], max_depth: int = 1) -> List[str]:
        """
        对文本进行多层级分类

        参数:
        - text (str): 待分类文本
        - categories (List[dict]): 类别列表
        - max_depth (int): 最大分类深度

        返回:
        - List[str]: 分类结果列表
        """
        return self._predict_category(text, categories, 1, max_depth)


def classify_consume_type(text: str, cate: Literal["支出", "收入"]) -> List[str]:
    """对收入/支出类型进行分类"""
    # 特例池定义 - 按类别和子类别组织
    special_cases = get_special_cases(cate)
    categories = get_categories(cate)
    
    # 检查是否在特例池中
    for category in special_cases:
        # 检查是否有子类别
        if "children" in category:
            for child in category["children"]:
                if any(case.lower() in text.lower() for case in child["cases"]):
                    return [category["name"], child["name"]]
        # 没有子类别的情况
        elif "cases" in category:
            if any(case.lower() in text.lower() for case in category["cases"]):
                return [category["name"], ""]
            
    # 不在特例池中,使用大模型分类
    llm = get_ollama()
    classifier = CategoryClassifier(llm)
    classify_result = classifier.classify(text, categories, 2)
    # 如果二级分类是"其他", 则返回一级分类
    if classify_result[1] == "其他":
        return [classify_result[0], ""]
    return classify_result
