# learning/week3/day18_OutputParser+Function-Calling/practice/output_parser.py

import os

from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.runnables import RunnableParallel
from langchain_deepseek import ChatDeepSeek

load_dotenv()


# 创建 LLM 实例
llm = ChatDeepSeek(
    model="deepseek-chat",
    api_key=os.environ["DEEPSEEK_API_KEY"],
    temperature=0.7
)

# 创建 Prompt
prompt = PromptTemplate.from_template("用一句话介绍{city}")

# 创建 Chain（使用 StrOutputParser）
chain = prompt | llm | StrOutputParser()

# 执行
result = chain.invoke({"city": "北京"})
print("StrOutputParser 结果：", result)
print("类型：", type(result))


from langchain_core.output_parsers import JsonOutputParser

# 创建 JsonOutputParser
json_parser = JsonOutputParser()

# 创建 Prompt（告诉 LLM 返回 JSON）
json_prompt = PromptTemplate.from_template("""请用 JSON 格式介绍{city}。

{format_instructions}

城市信息：""")

# 创建 Chain
json_chain = json_prompt | llm | json_parser

# 执行
result = json_chain.invoke({
    "city": "北京",
    "format_instructions": json_parser.get_format_instructions()
})
print("\nJsonOutputParser 结果：", result)
print("类型：", type(result))
