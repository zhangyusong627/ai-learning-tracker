# -*- coding: utf-8 -*-
"""
Layer 3 失败案例演示 —— 你自己跑，亲眼看到输入输出。

演示两件事：
  失败案例 1：ReAct 没有步数护栏会死循环（这里用 MAX_STEPS 护栏拦住，你能看到护栏怎么工作）
  失败案例 2：Plan-and-Execute 计划跑偏（计划里要查的东西，工具根本没有提供）

所有【输入】= 我们发给模型的；所有【输出】= 模型返回的原始字符串（未解析）。
运行命令（在 agent-demos 目录下）：
  python3 layer3_failure_cases.py
（需要先有 DEEPSEEK_API_KEY 环境变量；代理若关了会连不上，打开代理再跑）
"""

import json
import urllib.request

import layer2_tool_calling_demo as demo

client = demo.LLMClient()

# 统一的发请求函数：把“发出去什么”和“返回什么”都打印出来
def chat(messages, tools=None, tool_choice="auto"):
    payload = {"model": client.model, "messages": messages,
               "temperature": 0.1, "max_tokens": 2000}
    if tools:
        payload["tools"] = tools
        payload["tool_choice"] = tool_choice

    # ===================== 【输入】 =====================
    print("\n" + "█" * 72)
    print("█ 【输入】本轮发给模型的请求")
    print("█" * 72)
    print("  model     :", payload["model"])
    print("  messages  : 共 %d 条，最后 1 条是：" % len(payload["messages"]))
    print("    └─", json.dumps(payload["messages"][-1], ensure_ascii=False))
    if tools:
        print("  tools     :", [t["function"]["name"] for t in tools], "（每请求必带）")
    else:
        print("  tools     : 无（本轮回的是纯文本，不调工具）")
    # ===================================================

    req = urllib.request.Request(
        f"{client.base_url}/chat/completions",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json",
                 "Authorization": f"Bearer {client.api_key}"},
        method="POST")
    with urllib.request.urlopen(req, timeout=60) as resp:
        raw = resp.read().decode("utf-8")

    # ===================== 【输出】 =====================
    print("\n" + "█" * 72)
    print("█ 【输出】模型返回的原始字符串（resp.read() 原样，未解析）")
    print("█" * 72)
    print(raw)
    print("█" * 72)
    # ===================================================
    return json.loads(raw)


# =====================================================================
# 失败案例 1：ReAct 死循环 + 步数护栏
# =====================================================================
def failure_1_react_loop():
    print("\n" + "=" * 72)
    print("失败案例 1：ReAct 循环（展示步数护栏 MAX_STEPS 怎么防死循环）")
    print("=" * 72)
    print("要点：ReAct 是 while 循环（想→做→看→再想）。如果没有步数上限，")
    print("      模型在没想清楚时会一直调工具，无限烧 token。下面 MAX_STEPS=4 是护栏。")
    print("      （想看护栏强制截断的效果，把下面 MAX_STEPS 改成 1 再跑一次）")

    MAX_STEPS = 4   # ← 防死循环护栏：最多走 4 轮，到第 4 轮不管模型想不想继续都停
    user_q = "恒誉消金的授信失败率最近变高了，帮我全面排查一下根因"

    messages = [
        {"role": "system", "content": demo.SYSTEM_PROMPT},
        {"role": "user", "content": user_q},
    ]

    for step in range(1, MAX_STEPS + 1):
        print("\n########## ReAct 第 %d 轮 ##########" % step)
        resp = chat(messages, tools=demo.TOOLS)
        msg = resp["choices"][0]["message"]
        finish = resp["choices"][0]["finish_reason"]
        print("\n>>> 本轮回合结束标志 finish_reason =", finish,
              "（tool_calls=还想调工具 / stop=答完了）")

        messages.append(msg)

        if finish == "stop":
            print(">>> 模型给出最终答案，循环正常结束。")
            break

        # 模型还想调工具：逐个执行，再拼回 messages
        for tc in msg.get("tool_calls", []):
            fn = tc["function"]
            args = json.loads(fn["arguments"]) if fn.get("arguments") else {}
            result = demo.TOOL_IMPL[fn["name"]](**args)
            messages.append({"role": "tool", "tool_call_id": tc["id"], "content": result})

        if step == MAX_STEPS:
            print("\n>>> 已到 MAX_STEPS=%d 上限，护栏强制停止（否则会一直循环下去）。" % MAX_STEPS)


# =====================================================================
# 失败案例 2：Plan-and-Execute 计划跑偏
# =====================================================================
def failure_2_plan_divergence():
    print("\n\n" + "=" * 72)
    print("失败案例 2：Plan-and-Execute 计划跑偏")
    print("=" * 72)
    print("要点：模型先列计划，但计划里要查的东西，可能根本没有对应工具。")
    print("      执行时只能用能用的 3 个工具，计划剩下的步骤全废 → 计划跑偏。")

    user_q = "恒誉消金授信失败率升高，帮我排查根因"

    # —— 第一步：让模型出计划（纯文本，不调工具）——
    plan_msgs = [
        {"role": "system", "content": "你是资金系统异常分析助手。请先用纯文本列出调查步骤计划，"
                                       "每一步写清楚要查什么。不要调用工具，只输出计划。"},
        {"role": "user", "content": user_q},
    ]
    plan_resp = chat(plan_msgs, tools=None)
    plan_text = plan_resp["choices"][0]["message"]["content"]

    # —— 标记：计划里要查的东西，工具能不能满足 ——
    available = [t["function"]["name"] for t in demo.TOOLS]
    print("\n>>> 当前真实可用的工具只有：", available)
    print(">>> 请对照上面的【输出】计划文本：计划里提到的“失败原因码分布 / 渠道拆分 / 样本抽查”等，")
    print(">>> 在我们的工具清单里全都没有对应实现 → 计划一旦制定就僵了，执行必然跑偏。")


# =====================================================================
# 附：三种范式的循环代码结构对比（打印出来，看代码长什么样）
# =====================================================================
def show_loop_structures():
    print("\n\n" + "=" * 72)
    print("三种范式的循环代码结构对比（伪代码，看差别）")
    print("=" * 72)
    print('''
【ReAct】—— 一个 while 循环，边走边看
    while True:
        思考 = 模型(历史)            # 决定下一步调哪个工具
        if 思考.想结束: break
        结果 = 执行工具(思考.工具)
        历史.append(结果)           # 看了结果再决定下一步

【Plan-and-Execute】—— 先一次出计划，再套循环执行
    计划 = 模型(只出计划, 不调工具)   # 第一步：纯文本计划
    for 步骤 in 计划:
        结果 = 执行工具(步骤)         # 第二步：照单执行（计划僵化是风险）

【Reflection】—— 在前面任一范式产出后，多调一次做审查
    答案 = ReAct或Plan(问题)
    审查 = 模型("挑毛病: " + 答案)     # 额外一次调用 = 额外延迟+token
    最终 = 按审查修正(答案)
''')


if __name__ == "__main__":
    failure_1_react_loop()
    failure_2_plan_divergence()
    show_loop_structures()
    print("\n\n全部演示结束。你改 MAX_STEPS 的值再跑，能观察到护栏的不同行为。")
