# -*- coding: utf-8 -*-
"""
Layer 2 失败案例实验：故意把 query_history 的描述写烂，看模型行为变化。

对比对象：layer2_tool_calling_demo.py（描述写清楚了）
实验变量：只改 query_history 的 description，从
  "查询指定机构历史上发生过的类似异常事件及当时处理方式"
改成
  "查询历史"
其他完全不变。
"""

import json
import layer2_tool_calling_demo as demo


def run_experiment():
    # 深拷贝原始工具定义，只改 query_history 的描述
    bad_tools = json.loads(json.dumps(demo.TOOLS))
    for t in bad_tools:
        if t["function"]["name"] == "query_history":
            t["function"]["description"] = "查询历史"  # 故意写烂

    print("=" * 70)
    print("失败案例实验：query_history 描述 = '查询历史'（无机构/无异常语义）")
    print("=" * 70)

    client = demo.LLMClient()
    user_q = "恒誉消金的授信失败率最近好像变高了，帮我看看怎么回事"
    messages = [
        {"role": "system", "content": demo.SYSTEM_PROMPT},
        {"role": "user", "content": user_q},
    ]

    msg = client.chat_with_tools(demo.SYSTEM_PROMPT, user_q, bad_tools, messages)

    print("\n[模型第一轮返回]（只看它点了什么工具、传了什么参数）")
    if msg.get("tool_calls"):
        for tc in msg["tool_calls"]:
            fn = tc["function"]
            print(f"  工具={fn['name']}  参数={fn.get('arguments')}")
    else:
        print(f"  无工具调用，直接回答：{msg.get('content', '')[:300]}")


if __name__ == "__main__":
    run_experiment()
