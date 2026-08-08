# Layer 5 · 人工闸门（Human-in-the-Loop / Approval Gate）最小演示
#
# 运行：python3 layer5_human_in_the_loop_demo.py
# 教学点：模型只"提案"不"执行"；高风险动作经 确定性预校验 → 人工审批 → 才执行。
# 所有输入/输出/状态用 █ 标记，跑起来看真实流程。

# ---------------------------------------------------------------------------
# 1. 动作分级：只读自动执行，写操作需审批
# ---------------------------------------------------------------------------
READ_ONLY = {"query_metrics", "query_history", "query_governance_rules"}


def classify_risk(action):
    """动作分级：safe（自动执行）vs requires_approval（需人工闸门）"""
    if action["type"] in READ_ONLY:
        return "safe"
    return "requires_approval"


# ---------------------------------------------------------------------------
# 2. 确定性预校验：硬编码规则先筛，规则拒绝不进人工队列
# ---------------------------------------------------------------------------
AMOUNT_LIMIT = 1_000_000  # 单笔调整金额上限 100 万


def deterministic_precheck(action):
    if action["type"] == "suggest_adjustment":
        if action.get("amount", 0) > AMOUNT_LIMIT:
            return False, f"金额 {action['amount']} 超单笔上限 {AMOUNT_LIMIT}，规则拒绝"
    return True, "通过预校验"


# ---------------------------------------------------------------------------
# 3. 真正执行：仅当通过闸门后由 Harness 调用
# ---------------------------------------------------------------------------
def execute(action):
    return f"已执行 {action['type']} | payload={action.get('payload')}"


# ---------------------------------------------------------------------------
# 4. 审计轨迹
# ---------------------------------------------------------------------------
audit_log = []


def audit(event):
    audit_log.append(event)
    print(f"  [审计] {event}")


# ---------------------------------------------------------------------------
# 模型提案方：只生成建议，绝不自己执行
# ---------------------------------------------------------------------------
def agent_propose(amount):
    return {
        "type": "suggest_adjustment",
        "payload": "调高恒誉熔断阈值 5%→8%",
        "amount": amount,
    }


# ---------------------------------------------------------------------------
# Harness 主流程
# ---------------------------------------------------------------------------
def harness_run(proposal, approval_provider=input):
    print("█【输入】模型提案:", proposal)

    risk = classify_risk(proposal)
    print("█【状态】动作分级:", risk)

    # 只读：自动执行，无闸门
    if risk == "safe":
        result = execute(proposal)
        print("█【输出】只读动作自动执行:", result)
        audit(f"auto-exec | {proposal['type']} | {result}")
        return

    # 高风险：先确定性预校验
    ok, msg = deterministic_precheck(proposal)
    print("█【状态】确定性预校验:", msg)
    if not ok:
        print("█【输出】规则拒绝，不进人工队列:", msg)
        audit(f"rule-reject | {proposal['type']} | {msg}")
        return

    # 人工闸门：暂停，等待人类批准/拒绝
    print("█【状态】进入人工闸门，等待审批...")
    decision = approval_provider("  请审批 (approve/reject): ").strip().lower()
    print("█【输入】人类决策:", decision)

    if decision == "approve":
        result = execute(proposal)
        print("█【输出】人工批准，已执行:", result)
        audit(f"human-approve | {proposal['type']} | {result}")
    else:
        print("█【输出】人工拒绝，已中止，未执行任何动作")
        audit(f"human-reject | {proposal['type']} | 未执行")


if __name__ == "__main__":
    print("=" * 60)
    print("场景 A：金额 200 万 → 应被确定性规则直接拒绝（无需人工）")
    print("=" * 60)
    harness_run(agent_propose(amount=2_000_000))

    print()
    print("=" * 60)
    print("场景 B：金额 80 万 → 通过预校验 → 进入人工闸门（等你输入）")
    print("=" * 60)
    harness_run(agent_propose(amount=800_000))

    print()
    print("=" * 60)
    print("审计轨迹汇总：")
    for i, e in enumerate(audit_log, 1):
        print(f"  {i}. {e}")
