# -*- coding: utf-8 -*-
"""
Layer 3：Agent 范式演示。
- 范式一 Plan-and-Execute：先让模型制定调查计划（不调工具），再按计划 ReAct 执行。
- 范式三 Reflection：让模型审查自己刚给出的分析，挑毛病。
（范式二 ReAct = 下面的执行循环本身，即 Layer 2 那套 think→act→observe）
"""

import json
import urllib.request

import layer2_tool_calling_demo as demo

client = demo.LLMClient()


def chat(messages, tools=None, tool_choice="auto"):
    payload = {"model": client.model, "messages": messages,
               "temperature": 0.1, "max_tokens": 2000}
    if tools:
        payload["tools"] = tools
        payload["tool_choice"] = tool_choice
    req = urllib.request.Request(
        f"{client.base_url}/chat/completions",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json",
                 "Authorization": f"Bearer {client.api_key}"},
        method="POST")
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode())


user_q = "恒誉消金的授信失败率最近好像变高了，帮我看看怎么回事"

# ===== 范式一 Plan-and-Execute：先规划（不调工具）=====
print("=" * 70)
print("【Plan-and-Execute】第一步：先让模型制定调查计划（纯文本，不调工具）")
print("=" * 70)
plan_msgs = [
    {"role": "system", "content": "你是一个资金系统异常分析助手。在动手查询之前，请先用纯文本列出你打算执行的调查步骤计划（每一步对应后续要调用的工具或动作）。不要调用任何工具，只输出计划。"},
    {"role": "user", "content": user_q},
]
plan_text = chat(plan_msgs, tools=None)["choices"][0]["message"]["content"]
print(plan_text)

# ===== 范式一执行：按 ReAct 跑工具 =====
print("\n" + "=" * 70)
print("【执行】按上面的计划，用 ReAct（边想边做）方式调工具拿数据")
print("=" * 70)
exec_msgs = [
    {"role": "system", "content": demo.SYSTEM_PROMPT},
    {"role": "user", "content": user_q},
]
r1 = chat(exec_msgs, tools=demo.TOOLS)
assistant = r1["choices"][0]["message"]
exec_msgs.append(assistant)
print("模型点单:", [tc["function"]["name"] for tc in assistant.get("tool_calls", [])])
for tc in assistant.get("tool_calls", []):
    fn = tc["function"]
    args = json.loads(fn["arguments"]) if fn.get("arguments") else {}
    result = demo.TOOL_IMPL[fn["name"]](**args)
    exec_msgs.append({"role": "tool", "tool_call_id": tc["id"], "content": result})
r2 = chat(exec_msgs, tools=demo.TOOLS)
final_answer = r2["choices"][0]["message"]["content"]
print("\n最终分析（ReAct 执行结果）:\n")
print(final_answer)

# ===== 范式三 Reflection：自我反思 =====
print("\n" + "=" * 70)
print("【Reflection】让模型审查自己刚才的分析，挑毛病")
print("=" * 70)
ref_msgs = [
    {"role": "system", "content": "你是一个严格的技术 reviewer。下面是一段资金系统异常分析，请指出它可能的遗漏、错误或证据不足的地方。只做审查，不要重写。"},
    {"role": "user", "content": f"原始问题：{user_q}\n\n待审查的分析：\n{final_answer}"},
]
print(chat(ref_msgs, tools=None)["choices"][0]["message"]["content"])
