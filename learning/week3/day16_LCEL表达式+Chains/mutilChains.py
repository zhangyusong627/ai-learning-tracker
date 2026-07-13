import os

from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_deepseek import ChatDeepSeek

load_dotenv()

# LLM
llm = ChatDeepSeek(
    model="deepseek-chat",
    api_key=os.environ["DEEPSEEK_API_KEY"],
    temperature=0.7
)

# Chain 1：中文 → 英文
to_english = PromptTemplate.from_template("将以下中文翻译成英文：{chinese}")

# Chain 2：英文 → 法文
to_french = PromptTemplate.from_template("将以下英文翻译成法文：{english}")

# 输出解析器
output_parser = StrOutputParser()

# 完整链路
chain = (
    to_english
    | llm
    | output_parser
    | (lambda text: {"english": text})  # 关键：把字符串转成字典
    | to_french
    | llm
    | output_parser
)

# 执行
result = chain.invoke({"chinese": "你好世界"})
print(result)
