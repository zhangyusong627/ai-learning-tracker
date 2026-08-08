# -*- coding: utf-8 -*-
"""Day 2 显式状态演示：状态由代码统一管理 vs 模型自己记"""

# ===== 不显式：模型靠"自己记得"判断（坏示范）=====
def bad_agent():
    # 模拟模型第一次查了错误率，结果在对话里但"没写进状态"
    model_memory = "我记得查过错误率了"   # 只在模型脑子里
    # 第二次：模型说"我已经查过了，直接分析吧"
    # 但代码侧没有任何记录 → 无法审计、无法恢复、无法验证
    return "模型说：我查过了，但代码啥也不知道"


# ===== 显式：状态由代码统一管理（好示范）=====
def good_agent():
    state = {"data": {}, "steps": 0}        # 状态：代码的地盘

    # 第 1 轮：模型点单查错误率
    state["steps"] += 1
    result = {"错误率": 0.08}               # 工具返回
    state["data"].update(result)            # ← 代码写入状态（显式）
    print(f"第{state['steps']}轮后 state = {state}")

    # 第 2 轮：模型想"再查一次历史"——但先看状态
    if "历史" not in state["data"]:
        state["steps"] += 1
        state["data"]["历史"] = ["上游晚到"]
        print(f"第{state['steps']}轮后 state = {state}")

    # 任何时候都能审计：查状态就知道模型做过什么
    print(f"\n审计：共 {state['steps']} 步，数据含 {list(state['data'].keys())}")
    return state


print("=== 不显式（坏）===")
print(bad_agent())
print("\n=== 显式（好）===")
good_agent()
