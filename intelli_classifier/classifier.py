from typing import Literal
from langchain_core.output_parsers import JsonOutputParser
from langchain_ollama.llms import OllamaLLM
from jinja2 import Template
from pydantic import BaseModel, Field
from utils import ROOT, get_txt_content, get_categories


# 获取 Ollama 模型实例
def get_ollama(model="qwen2.5:latest", base_url="http://localhost:11434"):
    return OllamaLLM(model=model, base_url=base_url)


# 定义分类信息 Pydantic 模型
class CateInfo(BaseModel):
    category: str = Field(description="支出分类")
    subcategory: str = Field(description="支出子分类")


# 查询支出分类
def query_expenditure(text: str, consume_type: Literal["支出", "收入"]):
    # 根据消费类型选择相应的模板
    if consume_type == "支出":
        jinja_template = Template(get_txt_content(ROOT / "prompt/expenditure.jinja"))
    else:
        jinja_template = Template(get_txt_content(ROOT / "prompt/income.jinja"))

    # 获取分类信息
    categories = get_categories(consume_type)

    # 使用 JsonOutputParser 解析输出
    parser = JsonOutputParser(pydantic_object=CateInfo)

    # 渲染 Jinja2 模板
    prompt = jinja_template.render(
        text=text, categories=categories, output_format=parser.get_format_instructions()
    )

    # 获取 Ollama LLM 实例并进行推理
    llm = get_ollama()
    chain = llm | parser

    # 调用链式推理
    return chain.invoke(prompt)
