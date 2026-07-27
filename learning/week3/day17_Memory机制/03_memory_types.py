"""
对比实验：BufferMemory vs SummaryMemory
========================================
Buffer：全部存下来（我们之前的做法）
Summary：自动总结，节省空间
"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv()

llm = ChatOpenAI(
    model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
    openai_api_key=os.getenv("DEEPSEEK_API_KEY"),
    openai_api_base=os.getenv("DEEPSEEK_BASE_URL"),
    temperature=0
)

# ===== 方式1：BufferMemory（全部存下来）=====
print("=" * 50)
print("方式1：BufferMemory（全部存下来）")
print("=" * 50)

buffer_history = []

def chat_buffer(user_input):
    buffer_history.append(HumanMessage(content=user_input))
    response = llm.invoke(buffer_history)
    buffer_history.append(response)
    return response.content

# 模拟 10 轮对话
for i in range(10):
    chat_buffer(f"这是第{i+1}轮对话，我在测试记忆功能")

print(f"\n对话轮数：10")
print(f"历史记录条数：{len(buffer_history)}")
print(f"历史记录总字符数：{sum(len(m.content) for m in buffer_history)}")


# ===== 方式2：SummaryMemory（自动总结）=====
print("\n" + "=" * 50)
print("方式2：SummaryMemory（自动总结）")
print("=" * 50)

summary_history = []
summary_text = ""  # 存储总结

def chat_summary(user_input):
    global summary_text

    # 如果历史太长，先总结
    if len(summary_history) > 6:
        # 把历史总结成一段话
        summary_prompt = [
            SystemMessage(content="请用中文总结以下对话内容，保留关键信息，控制在100字以内："),
            *summary_history
        ]
        summary_response = llm.invoke(summary_prompt)
        summary_text = summary_response.content
        summary_history.clear()
        print(f"\n[自动总结] {summary_text}")

    # 构建上下文：总结 + 最近对话
    context = []
    if summary_text:
        context.append(SystemMessage(content=f"之前的对话总结：{summary_text}"))
    context.extend(summary_history)
    context.append(HumanMessage(content=user_input))

    response = llm.invoke(context)
    summary_history.append(HumanMessage(content=user_input))
    summary_history.append(response)
    return response.content

# 模拟 10 轮对话
for i in range(10):
    chat_summary(f"这是第{i+1}轮对话，我在测试记忆功能")

print(f"\n对话轮数：10")
print(f"最近历史记录条数：{len(summary_history)}")
print(f"总结内容：{summary_text[:50]}...")


# ===== 对比 =====
print("\n" + "=" * 50)
print("对比总结")
print("=" * 50)
print(f"""
BufferMemory：
  - 记录条数：{len(buffer_history)}（全部保存）
  - 适合：短对话、需要完整历史

SummaryMemory：
  - 记录条数：{len(summary_history)}（只保留最近几轮）
  - 总结内容：自动压缩历史
  - 适合：长对话、节省 Token
""")
