# -*- coding: utf-8 -*-
"""
Layer 2 透明化脚本：把"发给模型的原始请求"和"模型返回的原始响应"原样打印。

目的：让学习者看清工具调用链路每一步的输入/输出，而不是只看处理后的结果。

只跑 1 轮（模型第一次返回），因为我们想看的就是"模型第一次到底吐了什么"。
"""

import json
import layer2_tool_calling_demo as demo


def dump(title, obj):
    """打印一个对象，带标题。"""
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)
    print(json.dumps(obj, ensure_ascii=False, indent=2))


def run():
    client = demo.LLMClient()
    user_q = "恒誉消金的授信失败率最近好像变高了，帮我看看怎么回事"

    # ---- 构造请求 ----
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

    # 1) 输入：发出去的是什么
    dump("【输入 1】发给 DeepSeek 的请求体（节选 tools 前 1 个，否则太长）", {
        "model": payload["model"],
        "tool_choice": payload["tool_choice"],
        "messages": payload["messages"],
        "tools[0]（共 3 个）": payload["tools"][0],
    })

    # 2) 输出：模型第一次返回的原始响应
    # 直接调底层，拿原始 message
    raw = client.chat_with_tools(demo.SYSTEM_PROMPT, user_q, demo.TOOLS, messages)

    dump("【输出 1】模型第一次返回的原始 message（重点看 tool_calls）", raw)

    # 3) 代码层做什么：把 tool_calls 解析出来，逐个执行
    print("\n" + "=" * 70)
    print("【代码层】拿到上面的 tool_calls 后，代码做的事")
    print("=" * 70)
    executed = []  # 缓存：(tool_call_id, name, args, result)
    for tc in raw.get("tool_calls", []):
        fn = tc["function"]
        name = fn["name"]
        args = json.loads(fn["arguments"]) if fn.get("arguments") else {}
        print(f"  解析出：要调 {name}，参数 {args}")
        print(f"  代码查表 TOOL_IMPL['{name}'] → 执行 → 得到结果字符串")
        result = demo.TOOL_IMPL[name](**args)
        print(f"  结果：{result}")
        executed.append((tc["id"], name, args, result))

    # 4) 回传：把助手消息 + 每个工具结果拼回去，再发一轮
    messages.append(raw)  # 助手原话（含 tool_calls）
    for tid, name, args, result in executed:
        messages.append({
            "role": "tool",
            "tool_call_id": tid,
            "content": result,
        })
    dump("【输入 2】拼好工具结果后，发给模型的第二轮请求（messages 最后 4 条是新加的）", {
        "messages[-4]（助手原话，含 tool_calls）": messages[-4],
        "messages[-3]（工具1结果）": messages[-3],
        "messages[-2]（工具2结果）": messages[-2],
        "messages[-1]（工具3结果）": messages[-1],
    })
    print("\n（至此模型拿到全部工具结果，第二轮会输出最终分析——见 layer2_tool_calling_demo.py 的运行结果）")


if __name__ == "__main__":
    run()
