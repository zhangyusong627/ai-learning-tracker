# -*- coding: utf-8 -*-
"""
Layer 2：打印 DeepSeek 返回的【完整原始响应】（含 choices / finish_reason / usage 信封）。

之前 layer2_show_raw_io.py 打印的是 data["choices"][0]["message"]（剥出来的内层）。
这里打印完整的 data，让你看到真实的 HTTP 响应长什么样。
"""

import json
import urllib.request
import urllib.error
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
        data = json.loads(resp.read().decode("utf-8"))

    print("=" * 70)
    print("DeepSeek 返回的【完整原始响应】（真实 HTTP body）")
    print("=" * 70)
    print(json.dumps(data, ensure_ascii=False, indent=2))

    print("\n" + "=" * 70)
    print("三个最该盯住的字段")
    print("=" * 70)
    choice = data["choices"][0]
    print(f"1) finish_reason = {choice['finish_reason']!r}")
    print("   → 'tool_calls' 表示模型停下来是为了调工具；'stop' 表示它答完了")
    print(f"2) message.role = {choice['message']['role']!r}")
    print(f"   message.tool_calls 数量 = {len(choice['message'].get('tool_calls', []))}")
    print(f"3) usage = {data.get('usage')}")
    print("   → 这次调用花了多少 token（Layer 5 成本控制要盯这个）")


if __name__ == "__main__":
    main()
