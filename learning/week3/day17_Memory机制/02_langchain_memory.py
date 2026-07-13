"""
LangChain Memory 实战
=====================
本质：就是我们刚才写的 history 列表
"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

# 加载环境变量
load_dotenv()

# 创建 DeepSeek LLM
llm = ChatOpenAI(
    model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
    openai_api_key=os.getenv("DEEPSEEK_API_KEY"),
    openai_api_base=os.getenv("DEEPSEEK_BASE_URL"),
    temperature=0
)

# 手动实现 Memory（本质就是 history 列表）
history = []

def chat(user_input):
    # 1. 存用户输入
    history.append(HumanMessage(content=user_input))
    # 2. 把整个历史发给 AI
    response = llm.invoke(history)
    # 3. 存 AI 回复
    history.append(response)
    return response.content

print("=" * 50)
print("LangChain Memory 测试")
print("=" * 50)

# 第1轮对话
print("\n--- 第1轮 ---")
response1 = chat("你好，我叫小明")
print(f"AI：{response1}")

# 第2轮对话
print("\n--- 第2轮 ---")
response2 = chat("我喜欢吃苹果")
print(f"AI：{response2}")

# 第3轮对话（测试记忆）
print("\n--- 第3轮（测试记忆）---")
response3 = chat("你还记得我叫什么吗？")
print(f"AI：{response3}")

# 查看历史记录
print("\n" + "=" * 50)
print("查看历史记录（本质就是 history 列表）")
print("=" * 50)
for msg in history:
    role = "user" if isinstance(msg, HumanMessage) else "assistant"
    print(f"  {role}: {msg.content}")

print("\n" + "=" * 50)
print("思考：这个版本和我们手写的有什么区别？")
print("=" * 50)
