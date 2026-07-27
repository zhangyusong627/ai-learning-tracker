import os

from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_deepseek import ChatDeepSeek

load_dotenv()

# 创建大模型对象
llm = ChatDeepSeek(
    model="deepseek-chat",
    api_key=os.environ["DEEPSEEK_API_KEY"],
    temperature=0.7
    )

# 创建提示词模板
prompt = PromptTemplate.from_template("你是一个翻译助手，请将以下内容翻译成{language}: {text}")

# 创建输出解析器
output_parser = StrOutputParser()

# 创建链式调用
chain = prompt | llm | output_parser

# 执行链式调用
result = chain.invoke({
    "language": "中文",
    "text": "Hello, how are you?"
})

print(result)


# 完整的多步链路
full_chain = (
    PromptTemplate.from_template("用 {language} 写一个函数：{task}")
    | llm
    | StrOutputParser()
    | PromptTemplate.from_template("解释以下代码的功能：\n\n{code}")
    | llm
    | StrOutputParser()
)

result2 = full_chain.invoke({
    "language": "Python",
    "task": "计算斐波那契数列第n项",
    "code": "placeholder"  # 这个会被覆盖
})

print(result2)
