# -*- coding: utf-8 -*-
"""Day 1 最小 Agent 循环（模拟版）：固定工作流 vs Agent 概念配套练习。

故意保留一个"终止条件键名不一致"的 bug（"历史" vs "近2小时"），
用于观察：模型永远不返回 None → 只能靠 max_steps 兜底截断。
"""
import json

TOOLS = {
    "query_metrics": {"params": ["institution", "metric"], "desc": "查询机构指标"},
    "query_history": {"params": ["institution", "hours"], "desc": "查询历史事件"},
}

METRICS = {"A": {"错误率": 0.08, "P95": 900}, "B": {"错误率": 0.01, "P95": 120}}
HISTORY = {"A": {"近2小时": ["上游对账文件晚到", "超时重试增多"]}}


def execute(tool_name, args):
    if tool_name == "query_metrics":
        m = METRICS[args["institution"]]
        return {"错误率": m["错误率"], "P95": m["P95"]}
    if tool_name == "query_history":
        return HISTORY[args["institution"]]
    raise ValueError(f"未知工具: {tool_name}")


def mock_model(state):
    if "错误率" not in state["data"]:
        return {"tool": "query_metrics", "args": {"institution": "A", "metric": "错误率"}}
    if "历史" not in state["data"]:          # ← BUG：execute 写入的是"近2小时"，这里查"历史"
        return {"tool": "query_history", "args": {"institution": "A", "hours": 2}}
    return None


def run_agent():
    state = {"data": {}, "steps": 0, "max_steps": 5}
    while state["steps"] < state["max_steps"]:
        decision = mock_model(state)
        if decision is None:
            print("Agent 决定终止（信息已足够）")
            break
        tool, args = decision["tool"], decision["args"]
        print(f"第{state['steps'] + 1}步：点单 {tool}{args}")
        result = execute(tool, args)
        print(f"  执行结果: {result}")
        state["data"].update(result)
        state["steps"] += 1
    else:
        print("达到最大步数，强制终止（兜底生效）")
    return state


if __name__ == "__main__":
    state = run_agent()
    print("最终状态:", json.dumps(state["data"], ensure_ascii=False))
