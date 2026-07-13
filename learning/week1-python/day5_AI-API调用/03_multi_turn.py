"""
AI API 调用 - 第三步：多轮对话
让 AI 记住你说过的话
"""
import os

import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ["DEEPSEEK_API_KEY"]
BASE_URL = "https://api.deepseek.com"

# 对话历史
messages = []

def chat(user_input):
    """发送消息并获取回复"""
    # 把用户消息加入历史
    messages.append({"role": "user", "content": user_input})

    # 调用 API
    resp = requests.post(
        f"{BASE_URL}/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "deepseek-chat",
            "temperature": 0,
            "messages": messages  # 把整个对话历史发给 AI
        }
    )

    # 获取回复
    data = resp.json()
    assistant_reply = data['choices'][0]['message']['content']

    # 把 AI 回复也加入历史
    messages.append({"role": "assistant", "content": assistant_reply})

    return assistant_reply

# 开始对话
print("=== 多轮对话演示 ===\n")

# 第一轮
print("你: 我叫小明")
print("AI:", chat("我叫小明"))
print()

# 第二轮
print("你: 我叫什么名字？")
print("AI:", chat("我叫什么名字？"))
print()

# 第三轮
print("你: 你能做什么？")
print("AI:", chat("你能做什么？"))
print()

# 查看对话历史
print("=== 对话历史 ===")
for msg in messages:
    role = "你" if msg['role'] == 'user' else "AI"
    print(f"{role}: {msg['content'][:30]}...")
