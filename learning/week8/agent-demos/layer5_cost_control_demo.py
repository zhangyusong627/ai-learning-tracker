# Layer 5 · 成本控制（Cost Control）最小演示
#
# 运行：python3 layer5_cost_control_demo.py
# 教学点：两道成本闸——max_steps 兜底防烧钱 + 模型分层(Model Tiered)降本。
# 所有输入/输出用 █ 标记，跑起来看真实数据。（单价为合成示例）

# 模型单价（每 1k token，仅示例）
PRICE = {"cheap": 0.0001, "strong": 0.001}


def model_call(tier, tokens):
    cost = tokens / 1000 * PRICE[tier]
    return tokens, cost


def scenario_max_steps():
    """无 max_steps 会死循环；有 max_steps 强制截断"""
    print("█【输入】一个会重复点单的笨 Agent（无终止会死循环）")
    MAX_STEPS = 5
    steps = 0
    total_tokens = 0
    while True:  # 故意写成会一直循环
        steps += 1
        total_tokens += 100
        if steps >= MAX_STEPS:
            print(f"█【状态】触发 max_steps={MAX_STEPS} 兜底，强制截断")
            break
    print(f"█【输出】实际执行 {steps} 步，消耗 {total_tokens} token（未被烧穿）")


def scenario_tiered():
    """模型分层：简单步用 cheap，复杂推理用 strong"""
    print("█【输入】3 步任务：路由(简) / 查询(简) / 生成建议(复杂)")
    plan = [("路由分类", "cheap", 50), ("工具查询", "cheap", 80), ("生成治理建议", "strong", 300)]
    total_cost = 0.0
    for name, tier, tok in plan:
        used, cost = model_call(tier, tok)
        total_cost += cost
        print(f"█【状态】{name}: {tier} 模型, {used} token, ${cost:.4f}")
    all_strong = sum(tok for _, _, tok in plan) / 1000 * PRICE["strong"]
    print(f"█【输出】分层成本 ${total_cost:.4f} vs 全强模型 ${all_strong:.4f}")


if __name__ == "__main__":
    print("=" * 60)
    print("场景1：max_steps 兜底防烧钱")
    print("=" * 60)
    scenario_max_steps()

    print()
    print("=" * 60)
    print("场景2：模型分层降本")
    print("=" * 60)
    scenario_tiered()
