# -*- coding: utf-8 -*-
"""
Layer 2：只打印 DeepSeek 返回的【原始字符串】。
不 json.loads、不排版、不拆解。网线回来是啥样就打印啥样。
"""

import json
import urllib.request
import os

import layer2_tool_calling_demo as demo


def main():
    client = demo.LLMClient()
    user_q = "恒誉消金的授信失败率最近好像变高了，帮我看看怎么回事"

    messages = [
        {"role": "system", "content": demo.SYSTEM_PROMPT},
        {"role": "user", "content": user_q},
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
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {client.api_key}",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        raw = resp.read().decode("utf-8")   # 网线回来的原文，一行不加工

    # 下面这一行是全部输出，没有别的
    print(raw)


if __name__ == "__main__":
    main()
