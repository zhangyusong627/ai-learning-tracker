# -*- coding: utf-8 -*-
"""Day 1 真实 Agent Demo：资金系统异常分析助手（Function Calling 版）

调用真实 DeepSeek 模型，走真实的"模型点单 → 代码执行 → 结果回传 → 再决策"循环。
场景：给出一家机构的异常指标，让 Agent 自己决定查什么、查几次，最后给出结论。

工程要素（对应今天学的概念）：
- 循环：while 循环，模型每次返回 tool_calls 就执行，没有 tool_calls 就终止
- 工具：只读工具（查询指标/历史/规则），全部无副作用
- 状态：消息列表就是显式状态（每轮把工具结果追加进去，模型只能看到代码写回的内容）
- 终止：模型主动终止（不再要工具）+ max_steps 兜底
- 失败恢复：工具执行异常会捕获并回传错误给模型

依赖：pip install openai ｜ 环境变量 DEEPSEEK_API_KEY（或 LLM_API_KEY）
"""
import json
import os

from openai import OpenAI

BASE_URL = os.environ.get("LLM_BASE_URL", "https://api.deepseek.com")
API_KEY = os.environ.get("LLM_API_KEY") or os.environ.get("DEEPSEEK_API_KEY")
MODEL = os.environ.get("LLM_MODEL", "deepseek-chat")

if not API_KEY:
    raise SystemExit("缺少 DEEPSEEK_API_KEY / LLM_API_KEY 环境变量")

client = OpenAI(base_url=BASE_URL, api_key=API_KEY)

# ===== 模拟数据源（合成，只读）=====
METRICS = {
    "恒誉": {"错误率": 0.08, "P95延迟ms": 900, "QPS": 3200, "线程池队列": 850},
    "云腾": {"错误率": 0.01, "P95延迟ms": 120, "QPS": 4500, "线程池队列": 60},
}
HISTORY = {
    "恒誉": [
        {"time": "10:00", "event": "上游对账文件晚到"},
        {"time": "10:30", "event": "超时重试量突增"},
    ],
}
RULES = [
    {"name": "错误率红线", "condition": "错误率 > 0.05", "action": "人工介入"},
    {"name": "P95红线", "condition": "P95延迟 > 500ms", "action": "人工介入"},
]

# ===== 工具定义（给模型看的"菜单"，OpenAI Function Calling schema）=====
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "query_metrics",
            "description": "查询指定机构的实时性能指标（错误率/P95延迟/QPS/线程池队列）",
            "parameters": {
                "type": "object",
                "properties": {"institution": {"type": "string", "description": "机构名称"}},
                "required": ["institution"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "query_history",
            "description": "查询指定机构最近2小时的历史事件记录",
            "parameters": {
                "type": "object",
                "properties": {"institution": {"type": "string", "description": "机构名称"}},
                "required": ["institution"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "query_rules",
            "description": "查询平台的治理规则（哪些指标超限需要人工介入）",
            "parameters": {"type": "object", "properties": {}},
        },
    },
]

# ===== 工具执行层（真正的"厨师"）=====
def execute_tool(name: str, args: dict) -> str:
    if name == "query_metrics":
        inst = args["institution"]
        if inst not in METRICS:
            raise ValueError(f"机构 {inst} 不存在")
        return json.dumps(METRICS[inst], ensure_ascii=False)
    if name == "query_history":
        inst = args["institution"]
        return json.dumps(HISTORY.get(inst, []), ensure_ascii=False)
    if name == "query_rules":
        return json.dumps(RULES, ensure_ascii=False)
    raise ValueError(f"未知工具: {name}")


# ===== Agent 循环 =====
def run_agent(user_problem: str, max_steps: int = 6) -> None:
    # 显式状态 = 消息列表（代码统一维护，模型只能读+通过工具结果间接更新）
    messages = [
        {"role": "system", "content":
         "你是资金系统异常分析助手。你的职责：诊断问题、给出结论。"
         "只使用给定的工具获取信息，不要编造数据。"
         "结论必须引用你实际查到的数据。查完信息后，用中文给出诊断结论。"},
        {"role": "user", "content": user_problem},
    ]

    print(f"=== 问题: {user_problem} ===\n")
    for step in range(1, max_steps + 1):
        print(f"── 第 {step} 轮：模型思考决策 ──")
        resp = client.chat.completions.create(
            model=MODEL, messages=messages, tools=TOOLS, temperature=0.2,
        )
        msg = resp.choices[0].message

        # 模型决定不再调工具 → 正常终止
        if not msg.tool_calls:
            print(f"模型结论: {msg.content}\n")
            print("✅ 模型主动终止（不再需要工具）")
            return

        # 模型点单 → 代码执行 → 回传结果
        for tc in msg.tool_calls:
            name = tc.function.name
            args = json.loads(tc.function.arguments or "{}")
            print(f"  ↳ 点单: {name}{args}")
            try:
                result = execute_tool(name, args)   # 代码真正执行
                print(f"    执行结果: {result[:120]}")
            except Exception as e:
                result = f"工具执行失败: {e}"        # 失败恢复：把错误回传模型
                print(f"    ⚠️ {result}")
            # 把模型点单和工具结果都追加进状态（显式状态更新）
            messages.append({
                "role": "assistant",
                "content": None,
                "tool_calls": [{"id": tc.id, "type": "function",
                                "function": {"name": name, "arguments": tc.function.arguments}}],
            })
            messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})

    print(f"\n⚠️ 达到最大步数 {max_steps}，强制终止（兜底刹车）")


if __name__ == "__main__":
    run_agent("恒誉的异常指标是：错误率 8%、P95 延迟 900ms、线程池队列 850。请诊断可能原因并给出处理建议。")
