from typing import List, Literal
from langchain_core.language_models import BaseChatModel
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama.llms import OllamaLLM
from jinja2 import Template
from utils.general import ROOT, get_txt_content


# 获取 Ollama 模型实例
def get_ollama(model="qwen2.5:latest", base_url="http://localhost:11434"):
    return OllamaLLM(model=model, base_url=base_url)


def llm_classifier_query(llm: BaseChatModel, text: str, categories: List[dict]):
    """
    分类器工具函数，借助大模型对输入文本进行分类，结合类别名和类别描述，并添加“其他”类别。

    参数:
    - llm (BaseChatModel): 使用的大模型
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

    chain = llm | StrOutputParser()

    return chain.invoke(prompt)


def classify_consume_type(
    text: str,
    categories: List[dict],
    predict_children: bool = False
):
    
    def wrapper_category(categories: List[dict]):
        return [{ "name":category["name"]} for category in categories]

    def get_category(categories: List[dict], name: str):
        for category in categories:
            if category["name"] == name:
                return category
        return None

    # 初始化大模型
    llm = get_ollama()

    # 获取一级类别
    first_level_categories = wrapper_category(categories)

    # 使用大模型进行分类
    first_level_category = llm_classifier_query(llm, text, first_level_categories)

    # 验证一级类别是否存在
    raw_first_category = get_category(categories, first_level_category)
    if not raw_first_category:
        return "其他", ""

    # 如果预测二级类别，则获取二级类别
    second_level_category = ""
    if predict_children and raw_first_category.get("children"):
        second_level_categories = wrapper_category(raw_first_category["children"])
        second_level_category = llm_classifier_query(llm, text, second_level_categories)
        
        # 验证二级类别是否存在
        if not get_category(raw_first_category["children"], second_level_category):
            second_level_category = "其他"

    return first_level_category, second_level_category
