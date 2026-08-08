# -*- coding: utf-8 -*-
"""把 DeepSeek 原始响应原封不动存成文件，并验证是否能被 json.loads 解析。"""

import json
import urllib.request
from pathlib import Path

import layer2_tool_calling_demo as demo

client = demo.LLMClient()
messages = [
    {"role": "system", "content": demo.SYSTEM_PROMPT},
    {"role": "user", "content": "恒誉消金的授信失败率最近好像变高了，帮我看看怎么回事"},
]
payload = {
    "model": client.model,
    "messages": messages,
    "tools": demo.TOOLS,
    "tool_choice": "auto",
    "temperature": 0.1,
    "max_tokens": 2000,
}
req = urllib.request.Request(
    f"{client.base_url}/chat/completions",
    data=json.dumps(payload).encode("utf-8"),
    headers={"Content-Type": "application/json", "Authorization": f"Bearer {client.api_key}"},
    method="POST",
)
with urllib.request.urlopen(req, timeout=60) as resp:
    raw_bytes = resp.read()          # 原始字节，一字不差

# 1) 原封不动存盘
out = Path(__file__).with_name("raw_response_sample.json")
with out.open("wb") as f:
    f.write(raw_bytes)
print("已存盘:", out)

# 2) 用标准 json.loads 解析，验证合法性
try:
    obj = json.loads(raw_bytes.decode("utf-8"))
    print("json.loads 解析结果: 成功 ✅")
    print("根字段:", list(obj.keys()))
    print("tool_calls 数量:", len(obj["choices"][0]["message"].get("tool_calls", [])))
except json.JSONDecodeError as e:
    print("json.loads 解析结果: 失败 ❌")
    print("报错信息:", e)
