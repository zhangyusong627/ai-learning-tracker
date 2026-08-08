#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Layer 6 多智能体 demo：编排者-工作者（Orchestrator-Workers）拓扑

AI 写代码，用户自己跑看真实 I/O。所有输入输出用 █ 标记。
本 demo 用合成数据模拟多个 Agent 协作，不调用真实 LLM。
要看的核心：
  1. 多 Agent 之间通过"消息传递"协作（编排者派活、收结果、汇总）
  2. 每个 Agent 各自有独立的上下文（token 各自算，不互相污染）
  3. 协调开销真实存在（编排者的拆解/汇总也消耗 token）
"""
import time


class Worker:
    """工作者 Agent：负责一个子任务（模拟 LLM 推理 + token 消耗）"""

    def __init__(self, name, skill):
        self.name = name
        self.skill = skill
        self.tokens = 0

    def process(self, task):
        """模拟处理一个子任务"""
        print(f"  █【输入】Worker[{self.name}] 收到子任务: {task}")
        time.sleep(0.1)
        result = f"{self.skill}处置完成: {task}"
        cost = len(task) + len(result)
        self.tokens += cost
        print(f"  █【输出】Worker[{self.name}] 返回: {result} | 消耗 {cost} token")
        return result


class Orchestrator:
    """编排者 Agent：拆解任务、路由给 Worker、汇总结果（模拟 LLM 决策）"""

    def __init__(self, workers):
        self.workers = workers
        self.tokens = 0

    def decompose(self, user_request):
        """把用户请求拆成子任务"""
        print(f"  █【输入】编排者收到用户请求: {user_request}")
        subtasks = [s for s in user_request.split("、")]
        cost = len(user_request) + len(str(subtasks))
        self.tokens += cost
        print(f"  █【输出】编排者拆解为 {len(subtasks)} 个子任务: {subtasks} | 消耗 {cost} token")
        return subtasks

    def route(self, subtask):
        """确定性路由：按关键词分派给对应 Worker"""
        if "指标" in subtask or "异常" in subtask:
            return self.workers[0]
        return self.workers[1]

    def aggregate(self, results):
        """汇总各 Worker 的结果（模拟 LLM 总结）"""
        summary = "；".join(results)
        cost = len(summary)
        self.tokens += cost
        print(f"  █【输出】编排者汇总为最终答复: {summary} | 消耗 {cost} token")
        return summary


def main():
    print("=" * 64)
    print("Layer 6 多智能体 demo：编排者-工作者（Orchestrator-Workers）")
    print("=" * 64)

    # 两个 Worker 各司其职，上下文彼此独立
    analyst = Worker("分析员", "指标异常分析")
    rule_guard = Worker("规则员", "合规规则校验")
    orchestrator = Orchestrator([analyst, rule_guard])

    user_request = "恒誉今日异常指标、单笔上限合规校验"
    print(f"█【输入】用户请求: {user_request}\n")

    # 1) 编排者拆解
    subtasks = orchestrator.decompose(user_request)

    # 2) 路由 + 并行执行（这里简化串行，实际可并发）
    print("\n--- 编排者路由派活 ---")
    results = []
    for sub in subtasks:
        w = orchestrator.route(sub)
        print(f"  █【状态】路由: {sub} -> Worker[{w.name}]")
        results.append(w.process(sub))

    # 3) 汇总
    print("\n--- 编排者汇总 ---")
    final = orchestrator.aggregate(results)

    print("\n" + "=" * 64)
    print("█【输出】协调开销统计（多 Agent 的代价）:")
    print(f"  编排者 token: {orchestrator.tokens}")
    print(f"  Worker[分析员] token: {analyst.tokens}")
    print(f"  Worker[规则员] token: {rule_guard.tokens}")
    total = orchestrator.tokens + analyst.tokens + rule_guard.tokens
    print(f"  多 Agent 总 token: {total}")
    print(f"  （编排者的拆解+汇总占了 {orchestrator.tokens}，这就是多 Agent 的协调开销）")
    print(f"█【输出】最终答复: {final}")


if __name__ == "__main__":
    main()
