# -*- coding: utf-8 -*-
"""
Layer 2 工具调用机制 Demo —— 资金系统异常分析助手（最小版）

教学目的：
1. 用真实大模型（DeepSeek）跑通一次完整的工具调用链路
2. 理解工具定义三要素：名称、描述、参数结构
3. 理解"模型点单、代码执行"——模型只输出 JSON，真正执行的是代码

场景：资金系统出现异常（恒誉消金授信失败率变高），Agent 自主决定查什么工具。

注意：本文件是学习 demo，不进作品集仓库。工具返回的是合成数据（非真实公司资料）。
"""

import json
import os
import urllib.request
import urllib.error


# ---------------------------------------------------------------------------
# 1. 大模型客户端（OpenAI 兼容协议，与 RAG 作品集同源）
# ---------------------------------------------------------------------------
class LLMClient:
    """最小化的 LLM 客户端，支持 tools 参数（工具调用）。"""

    def __init__(self, base_url=None, api_key=None, model=None):
        self.base_url = (base_url or os.environ.get("LLM_BASE_URL")
                         or "https://api.deepseek.com").rstrip("/")
        self.api_key = api_key or os.environ.get("LLM_API_KEY") or os.environ.get("DEEPSEEK_API_KEY")
        self.model = model or os.environ.get("LLM_MODEL") or "deepseek-chat"
        if not self.api_key:
            raise RuntimeError("缺少 LLM API key：请设置环境变量 DEEPSEEK_API_KEY")

    def chat_with_tools(self, system, user, tools, messages=None):
        """带工具的对话调用。返回模型原始响应（可能是工具调用，也可能是最终文本）。"""
        if messages is None:
            messages = []
        # 只在第一轮注入 system + user，后续轮次 messages 已包含历史
        if not messages:
            messages = [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ]

        payload = {
            "model": self.model,
            "messages": messages,
            "tools": tools,
            "tool_choice": "auto",  # 让模型自己决定要不要调工具、调哪个
            "temperature": 0.1,
            "max_tokens": 2000,
        }
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
            body = e.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"API HTTP 错误 {e.code}: {body[:500]}")
        except Exception as e:
            raise RuntimeError(f"API 调用失败: {e}")
        return data["choices"][0]["message"]


# ---------------------------------------------------------------------------
# 2. 工具定义（三要素：名称、描述、参数结构）
#    注意：description 是写给模型看的，要讲清楚"什么时候该用我"
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
                    "institution": {
                        "type": "string",
                        "description": "机构简称，如 恒誉消金 / 云腾 / 衡丰",
                    }
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
                    "institution": {
                        "type": "string",
                        "description": "机构简称，如 恒誉消金 / 云腾 / 衡丰",
                    }
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
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
]


# ---------------------------------------------------------------------------
# 3. 工具实现（代码层执行，返回合成数据）
#    这是"厨房"——模型点单后，真正干活的是这里
# ---------------------------------------------------------------------------
def query_metrics(institution: str) -> str:
    """合成数据：模拟查询某机构当前运行指标。"""
    data = {
        "恒誉消金": {
            "授信成功率": "91.2%",
            "放款平均延迟": "320ms",
            "近一小时授信失败率": "8.8%",  # 正常应 < 2%
            "对账差异笔数": "3 笔",
        },
        "云腾": {
            "授信成功率": "98.5%",
            "放款平均延迟": "110ms",
            "近一小时授信失败率": "1.1%",
            "对账差异笔数": "0 笔",
        },
        "衡丰": {
            "授信成功率": "97.1%",
            "放款平均延迟": "150ms",
            "近一小时授信失败率": "1.9%",
            "对账差异笔数": "1 笔",
        },
    }
    return json.dumps(data.get(institution, {"error": "未知机构"}), ensure_ascii=False)


def query_history(institution: str) -> str:
    """合成数据：模拟查询历史事件。"""
    data = {
        "恒誉消金": [
            {"时间": "2026-03-12", "事件": "授信失败率升至 7.5%",
             "原因": "上游征信接口超时，未降级", "处理": "临时调高限流+加超时降级"},
            {"时间": "2026-05-20", "事件": "放款延迟突增",
             "原因": "资方通道切换", "处理": "回切主通道"},
        ],
        "云腾": [{"时间": "2026-01-08", "事件": "对账差异 5 笔",
                  "原因": "日期格式不一致", "处理": "统一格式后重跑"}],
        "衡丰": [{"时间": "2026-04-15", "事件": "熔断触发",
                  "原因": "连续失败率超 5%", "处理": "熔断 10 分钟后恢复"}],
    }
    return json.dumps(data.get(institution, []), ensure_ascii=False)


def query_governance_rules() -> str:
    """合成数据：模拟查询治理规则。"""
    rules = {
        "授信限流阈值": "50 笔/秒",
        "熔断阈值": "连续失败率 >= 5% 触发熔断",
        "对账差异告警阈值": ">= 5 笔触发告警",
    }
    return json.dumps(rules, ensure_ascii=False)


# 工具名 → 实现函数 的映射表（代码层安全边界：只暴露这三个）
TOOL_IMPL = {
    "query_metrics": query_metrics,
    "query_history": query_history,
    "query_governance_rules": query_governance_rules,
}


# ---------------------------------------------------------------------------
# 4. 主流程：跑通"模型点单 → 代码执行 → 结果回传 → 模型继续"
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = (
    "你是一个资金系统异常分析助手。当用户描述资金系统异常时，"
    "你应该先调用合适的工具查询相关信息（指标、历史、治理规则），"
    "再根据工具返回的真实数据给出分析。不要编造数据，只基于工具返回结果说话。"
    "如果信息不足，明确说明还缺什么。"
)


def run_demo():
    client = LLMClient()
    user_question = "恒誉消金的授信失败率最近好像变高了，帮我看看怎么回事"

    print("=" * 70)
    print(f"用户提问：{user_question}")
    print("=" * 70)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_question},
    ]

    max_rounds = 5  # 兜底：最多 5 轮，防止模型无限调工具
    for round_i in range(1, max_rounds + 1):
        print(f"\n--- 第 {round_i} 轮：调用模型 ---")
        msg = client.chat_with_tools(SYSTEM_PROMPT, user_question, TOOLS, messages)

        # 情况 A：模型决定调工具
        if msg.get("tool_calls"):
            # 助手消息（含 tool_calls）只追加一次，放在工具消息之前
            messages.append(msg)
            for tc in msg.get("tool_calls", []):
                fn = tc["function"]
                name = fn["name"]
                args = json.loads(fn["arguments"]) if fn.get("arguments") else {}

                print(f"  [模型点单] 工具={name}  参数={args}")

                # 代码层校验 + 执行（安全边界）
                if name not in TOOL_IMPL:
                    result = json.dumps({"error": f"未知工具 {name}"}, ensure_ascii=False)
                    print(f"  [代码拦截] 未知工具，拒绝执行")
                else:
                    result = TOOL_IMPL[name](**args)
                    print(f"  [代码执行] 返回={result}")

                # 把代码的"上菜"写回 messages，喂给下一轮模型
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "content": result,
                })
            continue

        # 情况 B：模型给出最终答案（没有 tool_calls）
        print(f"\n[模型最终回答]\n{msg.get('content', '')}")
        break
    else:
        print("\n[兜底终止] 达到最大轮数，强制停止（防死循环）")


if __name__ == "__main__":
    run_demo()
