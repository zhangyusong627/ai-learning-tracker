"""
AI API 调用 - 第一步：最简单的请求
DeepSeek API 是 OpenAI 兼容格式
"""
import os

import requests
from dotenv import load_dotenv

load_dotenv()

# DeepSeek API 配置
API_KEY = os.environ["DEEPSEEK_API_KEY"]
BASE_URL = "https://api.deepseek.com"

# 发送请求
resp = requests.post(
    f"{BASE_URL}/v1/chat/completions",
    headers={
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    },
    json={
        "model": "deepseek-chat",
        "temperature": 0.5,
        "messages": [
            {"role": "user", "content": "你好"}
        ]
    }
)

# 解析响应
data = resp.json()
print("状态码:", resp.status_code)
print("回复:", data['choices'][0]['message']['content'])
