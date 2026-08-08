# -*- coding: utf-8 -*-
"""
Layer 4：状态管理（State Management）Demo —— 资金系统异常分析助手

教学目的：
1. 看清 Agent 的"工作记忆"到底是什么 —— 就是那个 messages 数组
2. 看到 messages 每一轮都在长大 → 代价（token 成本、上下文窗口、模型变晕）
3. 看到模型本身无状态：它不"记得"上一轮，是代码把历史整串重发，它才"看到"
4. 学一个解法：把关键结论外化成"显式状态对象"（scratchpad），和 chat 历史分开管
5. 学另一个解法：压缩（compaction）——历史太长时，把前面的对话总结成一段

运行方式（你自己跑，看真实输入输出）：
  cd learning/week8/agent-demos
  python3 layer4_state_management_demo.py

前提：DEEPSEEK_API_KEY 已设置、代理已开。只用标准库，不用装包。
"""

import json
from layer2_tool_calling_demo import LLMClient


# ---------------------------------------------------------------------------
# 工具定义：在 Layer 2 三个只读工具基础上，加一个 update_state（显式状态）
# ---------------------------------------------------------------------------
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "query_metrics",
            "description": "查询指定资金机构当前的运行指标，包含授信成功率、放款平均延迟(毫秒)、"
                           "近一小时授信失败率、对账差异笔数。当用户提到某机构指标异常、"
                           "失败率升高、延迟变慢时使用。参数 institution 为机构简称。",
            "parameters": {
                "type": "object",
                "properties": {
                    "institution": {"type": "string", "description": "机构简称，如 恒誉消金 / 云腾 / 衡丰"}
                },
                "required": ["institution"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "query_history",
            "description": "查询指定机构历史上发生过的类似异常事件及当时处理方式。"
                           "当用户问'以前有没有类似情况'、'历史上有没有发生过'时使用。"
                           "参数 institution 为机构简称。",
            "parameters": {
                "type": "object",
                "properties": {
                    "institution": {"type": "string", "description": "机构简称，如 恒誉消金 / 云腾 / 衡丰"}
                },
                "required": ["institution"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "query_governance_rules",
            "description": "查询当前生效的治理规则，包含授信限流阈值(笔/秒)、"
                           "熔断阈值(连续失败率%)、对账差异告警阈值。当用户问'当前限流多少'、"
                           "'熔断规则是什么'、'阈值能不能调'时使用。无需参数。",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_state",
            "description": "把调查过程中的重要进展记录到工作记忆（显式状态）。"
                           "每查到一个关键事实或得出一个结论，就调用它记下来，"
                           "这样即使后面对话很长，关键结论也不会丢。",
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {
                        "type": "string",
                        "description": "记录类别，三选一："
                                       "'investigated'（已查过什么）、"
                                       "'finding'（得出的结论/发现）、"
                                       "'pending'（还缺什么/待确认）",
                        "enum": ["investigated", "finding", "pending"],
                    },
                    "value": {"type": "string", "description": "要记录的具体内容，一句话写清"},
                },
                "required": ["key", "value"],
            },
        },
    },
]


# ---------------------------------------------------------------------------
# 工具实现（合成数据，代码层执行）
# ---------------------------------------------------------------------------
def query_metrics(institution: str) -> str:
    data = {
        "恒誉消金": {"授信成功率": "91.2%", "放款平均延迟": "320ms",
                    "近一小时授信失败率": "8.8%", "对账差异笔数": "3 笔"},
        "云腾": {"授信成功率": "98.5%", "放款平均延迟": "110ms",
                "近一小时授信失败率": "1.1%", "对账差异笔数": "0 笔"},
        "衡丰": {"授信成功率": "97.1%", "放款平均延迟": "150ms",
                "近一小时授信失败率": "1.9%", "对账差异笔数": "1 笔"},
    }
    return json.dumps(data.get(institution, {"error": "未知机构"}), ensure_ascii=False)


def query_history(institution: str) -> str:
    data = {
        "恒誉消金": [
            {"时间": "2026-03-12", "事件": "授信失败率升至 7.5%", "原因": "上游征信接口超时未降级",
             "处理": "临时调高限流+加超时降级"},
            {"时间": "2026-05-20", "事件": "放款延迟突增", "原因": "资方通道切换", "处理": "回切主通道"},
        ],
        "云腾": [{"时间": "2026-01-08", "事件": "对账差异 5 笔", "原因": "日期格式不一致",
                  "处理": "统一格式后重跑"}],
        "衡丰": [{"时间": "2026-04-15", "事件": "熔断触发", "原因": "连续失败率超 5%", "处理": "熔断10分钟后恢复"}],
    }
    return json.dumps(data.get(institution, []), ensure_ascii=False)


def query_governance_rules() -> str:
    rules = {"授信限流阈值": "50 笔/秒", "熔断阈值": "连续失败率 >= 5% 触发熔断",
             "对账差异告警阈值": ">= 5 笔触发告警"}
    return json.dumps(rules, ensure_ascii=False)


TOOL_IMPL = {
    "query_metrics": query_metrics,
    "query_history": query_history,
    "query_governance_rules": query_governance_rules,
}


SYSTEM_PROMPT = (
    "你是一个资金系统异常分析助手。当用户描述资金系统异常时，"
    "你应该先调用合适的工具查询相关信息（指标、历史、治理规则），"
    "再根据工具返回的真实数据给出分析。不要编造数据，只基于工具返回结果说话。"
    "调查过程中，每获得一个重要发现，请调用 update_state 工具记录到工作记忆。"
)


# ---------------------------------------------------------------------------
# 修复：基类 chat_with_tools 只返回 message，丢掉了 usage / finish_reason。
# 这里子类化，把响应顶层的 usage 和 finish_reason 挂到 message 上，
# 这样脚本里才能真实打印"累计 token 在涨""finish_reason 是 tool_calls 还是 stop"。
# ---------------------------------------------------------------------------
class StatefulClient(LLMClient):
    def chat_with_tools(self, system, user, tools, messages=None):
        if messages is None:
            messages = []
        if not messages:
            messages = [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ]
        payload = {
            "model": self.model,
            "messages": messages,
            "tools": tools,
            "tool_choice": "auto",
            "temperature": 0.1,
            "max_tokens": 2000,
        }
        import urllib.request
        import urllib.error
        req = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"API HTTP 错误 {e.code}")
        msg = data["choices"][0]["message"]
        msg["usage"] = data.get("usage", {})               # 修复：挂上用量
        msg["finish_reason"] = data["choices"][0].get("finish_reason")  # 修复：挂上停止原因
        return msg


# ---------------------------------------------------------------------------
# 辅助：把 messages 数组打印成"可读快照"（不dump全部内容，只看结构在长大）
# ---------------------------------------------------------------------------
def snapshot(msgs):
    lines = []
    for i, m in enumerate(msgs):
        role = m.get("role")
        if role == "assistant" and m.get("tool_calls"):
            n = len(m["tool_calls"])
            lines.append(f"  [{i}] assistant  ← 含 {n} 个 tool_calls（模型点单）")
        elif role == "tool":
            lines.append(f"  [{i}] tool      ← 工具结果(tool_call_id={m.get('tool_call_id','')[:12]}...)")
        elif role == "assistant":
            c = m.get("content") or ""
            lines.append(f"  [{i}] assistant  ← 文本 {len(c)} 字")
        else:
            c = m.get("content") or ""
            lines.append(f"  [{i}] {role:<8} ← {len(c)} 字")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------
def run_demo():
    client = StatefulClient()
    user_question = "恒誉消金的授信失败率最近好像变高了，帮我看看怎么回事，还要不要调限流阈值"

    # 显式状态对象（与 messages 分开的"工作记忆"）
    state = {"investigated": [], "finding": [], "pending": []}

    print("█" * 70)
    print("█ 用户提问：", user_question)
    print("█" * 70)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_question},
    ]

    running_prompt_tokens = 0
    max_rounds = 4

    for round_i in range(1, max_rounds + 1):
        print(f"\n{'=' * 70}")
        print(f"█ 第 {round_i} 轮：调用模型之前")
        print(f"{'=' * 70}")
        print("█【输入】当前准备发给模型的 messages 快照（注意它在长大）：")
        print(snapshot(messages))
        print(f"█【输入】数组长度 = {len(messages)} 条")

        msg = client.chat_with_tools(SYSTEM_PROMPT, user_question, TOOLS, messages)

        # 累计本轮回传的 prompt token（关键：每轮都把整个历史重发，所以它在涨）
        usage = msg.get("usage", {})
        pt = usage.get("prompt_tokens", 0)
        running_prompt_tokens += pt

        print(f"\n█【输出】模型返回：finish_reason={msg.get('finish_reason')}  "
              f"本轮 prompt_tokens={pt}  累计 prompt_tokens={running_prompt_tokens}")
        print(f"█【输出】模型原始 content：{(msg.get('content') or '')[:200]}")

        if msg.get("tool_calls"):
            messages.append(msg)  # 助手消息（含 tool_calls）只追加一次
            for tc in msg["tool_calls"]:
                fn = tc["function"]
                name = fn["name"]
                args = json.loads(fn["arguments"]) if fn.get("arguments") else {}

                if name == "update_state":
                    # 解法：把结论外化到显式状态对象，而不是只留在 messages 里
                    key = args.get("key")
                    val = args.get("value")
                    if key in state:
                        state[key].append(val)
                    print(f"  █【输出-状态】模型调用 update_state：{key} += {val}")
                    messages.append({"role": "tool", "tool_call_id": tc["id"],
                                     "content": json.dumps({"ok": True}, ensure_ascii=False)})
                    continue

                if name not in TOOL_IMPL:
                    result = json.dumps({"error": f"未知工具 {name}"}, ensure_ascii=False)
                    print(f"  █【输出-拦截】未知工具，拒绝执行")
                else:
                    result = TOOL_IMPL[name](**args)
                    print(f"  █【输出-工具】{name}({args}) → {result}")

                messages.append({"role": "tool", "tool_call_id": tc["id"], "content": result})

            # 每轮结束打印当前显式状态（和 chat 历史是两套东西）
            print(f"\n█【状态】当前显式状态对象（独立于 messages）：")
            print(f"  investigated: {state['investigated']}")
            print(f"  finding:      {state['finding']}")
            print(f"  pending:      {state['pending']}")
            continue

        print(f"\n█【输出】模型最终回答：\n{msg.get('content', '')}")
        break
    else:
        print("\n█【兜底】达到最大轮数，强制停止（防死循环）")

    # -----------------------------------------------------------------------
    # 解法二：压缩（compaction）—— 历史太长时，把前面对话总结成一段
    # -----------------------------------------------------------------------
    print(f"\n{'=' * 70}")
    print("█ 演示：压缩（compaction）")
    print(f"{'=' * 70}")
    print(f"█【输入】把完整对话（{len(messages)} 条）发给模型，让它压成 ≤120 字摘要")
    compact_prompt = (
        "请把以上整段对话压缩成一段不超过 120 字的摘要，"
        "必须保留：①已查了哪些机构 ②核心结论 ③还缺什么。不要保留工具调用的原始 JSON。"
    )
    # 用真实模型做压缩：把现有 messages 末尾追加一条压缩指令，且不带工具
    compact_messages = messages + [{"role": "user", "content": compact_prompt}]
    compact_payload = {
        "model": client.model,
        "messages": compact_messages,
        "tools": [],            # 压缩时不给工具，强制它只总结
        "temperature": 0.1,
        "max_tokens": 400,
    }
    import urllib.request
    req = urllib.request.Request(
        f"{client.base_url}/chat/completions",
        data=json.dumps(compact_payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {client.api_key}"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        cdata = json.loads(resp.read().decode("utf-8"))
    summary = cdata["choices"][0]["message"].get("content", "")
    print(f"█【输出】压缩后摘要（约 {len(summary)} 字）：\n  {summary}")
    print(f"█【对比】压缩前 messages={len(messages)} 条；压缩后只需 1 条摘要即可替代前面大量历史")


if __name__ == "__main__":
    run_demo()
