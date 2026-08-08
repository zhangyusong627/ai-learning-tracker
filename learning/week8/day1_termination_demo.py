# -*- coding: utf-8 -*-
"""Day 1 终止条件演示：Agent 的三种"刹车"。"""

# 模拟一个"永远觉得差一点"的模型（真实模型也可能这样）
def stubborn_model(state):
    # 无论查了几次，都回答"还需要再查一次"
    return {"tool": "query_metrics", "args": {"institution": "A"}}


def run_agent(model, max_steps=5):
    state = {"data": {}, "steps": 0}
    while True:  # 没有兜底的循环
        if state["steps"] >= max_steps:          # 兜底终止 ①
            print(f"⚠️ 转满 {max_steps} 圈，强制终止（兜底刹车生效）")
            break
        decision = model(state)
        if decision is None:                     # 正常终止 ②
            print("✅ 模型说够了，正常终止")
            break
        state["steps"] += 1
        print(f"第{state['steps']}圈：又去查了一次（模型就是不停）")


print("=== 演示 1：只有兜底，模型永远不停 ===")
run_agent(stubborn_model)


# 正常模型：查两次就说够了
def normal_model(state):
    if state["steps"] < 2:
        return {"tool": "query_metrics", "args": {"institution": "A"}}
    return None  # 查完两次，主动收工


print("\n=== 演示 2：模型正常收工 ===")
run_agent(normal_model)
