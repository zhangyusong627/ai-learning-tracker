import os

from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_deepseek import ChatDeepSeek

load_dotenv()

# LLM
llm = ChatDeepSeek(
    model="deepseek-chat",
    api_key=os.environ["DEEPSEEK_API_KEY"],
    temperature=0.7
)

# 输出解析器
output_parser = StrOutputParser()

# 调试函数
def debug_step(step_name, x):
    print(f"\n{'='*50}")
    print(f"步骤: {step_name}")
    print(f"数据: {x}")
    print(f"{'='*50}")
    return x

# 翻译 Chain（带调试）
chain = (
    PromptTemplate.from_template("将以下中文翻译成英文：{text}")
    | (lambda x: debug_step("1. Prompt格式化后", x))
    | llm
    | (lambda x: debug_step("2. LLM原始响应", x))
    | output_parser
    | (lambda x: debug_step("3. 解析后的字符串", x))
)

# 执行
result = chain.invoke({"text": "你好世界"})
print("\n最终结果:", result)
