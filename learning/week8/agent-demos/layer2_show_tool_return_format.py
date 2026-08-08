# -*- coding: utf-8 -*-
"""
Layer 2：展示【代码执行工具后，返回给模型的报文格式】。
也就是那些 role:"tool" 的消息到底长什么样。只看原始报文，不拆解。
"""

import json
import urllib.request

import layer2_tool_calling_demo as demo

client = demo.LLMClient()

# 第一轮：拿模型的 tool_calls
messages = [
    {"role": "system", "content": demo.SYSTEM_PROMPT},
    {"role": "user", "content": "恒誉消金的授信失败率最近好像变高了，帮我看看怎么回事"},
]
payload = {"model": client.model, "messages": messages, "tools": demo.TOOLS,
           "tool_choice": "auto", "temperature": 0.1, "max_tokens": 2000}
req = urllib.request.Request(f"{client.base_url}/chat/completions",
    data=json.dumps(payload).encode(), headers={"Content-Type": "application/json",
    "Authorization": f"Bearer {client.api_key}"}, method="POST")
with urllib.request.urlopen(req, timeout=60) as resp:
    first = json.loads(resp.read().decode())

assistant_msg = first["choices"][0]["message"]

# 第二轮：代码执行每个工具，构造 tool 报文，拼回去
messages.append(assistant_msg)   # 先放模型的"点单"消息

print("=" * 70)
print("代码逐个执行工具后，构造出来、准备发回给模型的【tool 报文】")
print("（每条就是追加进 messages 的一个对象，原样 json.dumps）")
print("=" * 70)

for tc in assistant_msg["tool_calls"]:
    fn = tc["function"]
    name = fn["name"]
    args = json.loads(fn["arguments"]) if fn.get("arguments") else {}
    result = demo.TOOL_IMPL[name](**args)   # 代码真正执行工具

    tool_msg = {
        "role": "tool",
        "tool_call_id": tc["id"],
        "content": result,          # 注意：content 永远是字符串
    }
    print("\n--- 一条 tool 报文 ---")
    print(json.dumps(tool_msg, ensure_ascii=False))

print("\n" + "=" * 70)
print("第二轮实际发给模型的 messages 数组尾部（assistant点单 + 上面3条tool）")
print("=" * 70)
tail = messages[-4:]   # 最后4条：1条assistant + 3条tool
print(json.dumps(tail, ensure_ascii=False, indent=2))
