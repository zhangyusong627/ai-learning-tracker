# Layer 5 · 错误处理（Error Handling）最小演示
#
# 运行：python3 layer5_error_handling_demo.py
# 教学点：按失败性质分类处理——瞬时失败重试(带退避+封顶) / 永久失败不重试 / 空结果不致命。
# 所有输入/输出/状态用 █ 标记，跑起来看真实流程。

import time

MAX_RETRIES = 3


def tool(behavior, attempt):
    """模拟下游工具，behavior 控制本次表现：
       'transient' = 前两次超时、第三次成功
       'permanent' = 参数非法，永远失败
       'empty'     = 返回成功但无数据（None）
    """
    if behavior == "transient":
        if attempt < 3:
            raise TimeoutError(f"timeout #{attempt}")
        return f"data #{attempt}"
    if behavior == "permanent":
        raise ValueError(f"invalid param #{attempt}")
    if behavior == "empty":
        return None  # 成功但空


def classify_error(e):
    """失败分类：瞬时(可重试) vs 永久(不可重试)"""
    if isinstance(e, (TimeoutError, RuntimeError)):
        return "transient"
    return "permanent"


def call_with_retry(behavior):
    print(f"█【输入】调用工具 behavior={behavior}")
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            result = tool(behavior, attempt)
            if result is None:
                print(f"█【状态】第{attempt}次：成功但空结果（不致命）")
                print("█【输出】返回 None，模型应换路径或显式说明缺失")
                return None
            print(f"█【输出】第{attempt}次成功:", result)
            return result
        except Exception as e:
            kind = classify_error(e)
            print(f"█【状态】第{attempt}次失败({kind}): {e}")
            if kind == "permanent":
                print("█【输出】永久失败，不重试，直接上报/转人工")
                return None
            # 瞬时失败：退避后重试（演示用短退避）
            wait = 0.2 * attempt
            print(f"█【状态】瞬时失败，退避 {wait:.1f}s 后重试（最大 {MAX_RETRIES} 次）")
            time.sleep(wait)
    print(f"█【输出】重试 {MAX_RETRIES} 次耗尽，降级转人工")
    return None


if __name__ == "__main__":
    print("=" * 60)
    print("场景1：瞬时失败（超时）→ 重试 → 第3次成功")
    print("=" * 60)
    call_with_retry("transient")

    print()
    print("=" * 60)
    print("场景2：永久失败（参数非法）→ 不重试，直接放弃")
    print("=" * 60)
    call_with_retry("permanent")

    print()
    print("=" * 60)
    print("场景3：成功但空结果 → 不致命，标记信息缺失")
    print("=" * 60)
    call_with_retry("empty")
