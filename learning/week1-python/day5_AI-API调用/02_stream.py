"""
AI API 调用 - 第二步：流式输出
像 ChatGPT 那样逐字显示
"""
import os

import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ["DEEPSEEK_API_KEY"]
BASE_URL = "https://api.deepseek.com"

# 发送流式请求
resp = requests.post(
    f"{BASE_URL}/v1/chat/completions",
    headers={
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    },
    json={
        "model": "deepseek-chat",
        "temperature": 1,
        "stream": True,  # 关键：开启流式
        "messages": [
            {"role": "user", "content": "用一句话解释什么是 API"}
        ]
    },
    stream=True  # 这里也要 True
)

# 逐行读取
print("AI 回答: ", end="")
for line in resp.iter_lines():
    if line:
        # 跳过 "data: " 前缀
        line = line.decode('utf-8')
        if line.startswith('data: '):
            line = line[6:]
        if line == '[DONE]':
            break
        # 解析 JSON
        import json
        data = json.loads(line)
        # 提取增量内容
        delta = data['choices'][0]['delta']
        if 'content' in delta:
            print(delta['content'], end='', flush=True)
print()  # 换行
