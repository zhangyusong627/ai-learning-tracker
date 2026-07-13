import os

from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel
from langchain_deepseek import ChatDeepSeek

load_dotenv()

# LLM
llm = ChatDeepSeek(
    model="deepseek-chat",
    api_key=os.environ["DEEPSEEK_API_KEY"],
    temperature=1
)

# 输出解析器
output_parser = StrOutputParser()

# 三个翻译 Chain
to_english = PromptTemplate.from_template("将以下中文翻译成英文：{text}") | llm | output_parser
to_japanese = PromptTemplate.from_template("将以下中文翻译成日文：{text}") | llm | output_parser
to_korean = PromptTemplate.from_template("将以下中文翻译成韩文：{text}") | llm | output_parser


# 并行执行
parallel = RunnableParallel(
    english=to_english,
    japanese=to_japanese,
    korean=to_korean
)

# 执行
result = parallel.invoke({"text": "你好世界"})
print(result)
