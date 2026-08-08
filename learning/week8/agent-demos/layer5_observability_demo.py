# Layer 5 · 可观测性（Observability）最小演示
#
# 运行：python3 layer5_observability_demo.py
# 教学点：可观测性三大支柱——日志(Logs) / 指标(Metrics) / 追踪(Traces)。
# 所有输入/输出用 █ 标记，跑起来看真实报告。（token 为合成示例值）

import time


class Observability:
    """可观测性层：收集 日志 / 指标 / 追踪 三大支柱"""

    PRICE_PER_1K = 0.001  # 假设每 1k token $0.001（仅示例）

    def __init__(self):
        self.logs = []                         # 离散事件
        self.spans = []                        # 追踪：每步名称 + 耗时
        self.metrics = {"steps": 0, "tokens": 0, "errors": 0, "cost": 0.0}

    def log(self, event):
        self.logs.append(event)
        print(f"  [LOG] {event}")

    def span(self, name):
        return _Span(self, name)

    def record_tokens(self, n):
        self.metrics["tokens"] += n
        self.metrics["cost"] += n / 1000 * self.PRICE_PER_1K

    def record_error(self):
        self.metrics["errors"] += 1

    def report(self):
        print("── 指标(Metrics) ──")
        m = self.metrics
        print(f"  步数 steps    : {m['steps']}")
        print(f"  token 累计    : {m['tokens']}")
        print(f"  错误数 errors : {m['errors']}")
        print(f"  估算成本      : ${m['cost']:.4f}")
        print("── 追踪(Traces) ──")
        for s in self.spans:
            print(f"  {s['name']:22s} 耗时 {s['dur'] * 1000:.0f}ms")
        print("── 日志(Logs) ──")
        for l in self.logs:
            print(f"  - {l}")


class _Span:
    """上下文管理器：进入记录开始日志，退出记录耗时并累加步数"""

    def __init__(self, obs, name):
        self.obs = obs
        self.name = name
        self.t0 = None

    def __enter__(self):
        self.t0 = time.time()
        self.obs.log(f"开始: {self.name}")
        return self

    def __exit__(self, exc, *a):
        dur = time.time() - self.t0
        self.obs.spans.append({"name": self.name, "dur": dur})
        self.obs.metrics["steps"] += 1
        self.obs.log(f"结束: {self.name} ({dur * 1000:.0f}ms)")


def mock_agent_step(obs, step_name, tokens):
    with obs.span(step_name):
        obs.record_tokens(tokens)
        time.sleep(0.05)  # 模拟该步耗时


if __name__ == "__main__":
    obs = Observability()
    print("█【输入】启动 Agent，跑 3 步合成任务")
    mock_agent_step(obs, "模型决策", 120)
    mock_agent_step(obs, "工具调用 query_metrics", 60)
    mock_agent_step(obs, "生成建议", 200)
    print("█【输出】运行结束，可观测性报告如下：")
    obs.report()
