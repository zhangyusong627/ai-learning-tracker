"""
安全模块 - 防止 Prompt 注入攻击
"""

import re


class PromptGuard:
    """Prompt 注入防护"""

    # 危险关键词
    DANGEROUS_KEYWORDS = [
        "忽略", "系统提示", "你的指令", "覆盖", "假装",
        "忽略之前", "忽略上面", "输出系统", "显示系统"
    ]

    # 注入模式
    INJECTION_PATTERNS = [
        r"忽略.*指令",
        r"系统提示",
        r"你的.*是",
        r"假装.*是",
        r"输出.*prompt",
        r"显示.*prompt"
    ]

    @staticmethod
    def check_input(user_input: str) -> tuple[bool, str]:
        """
        检查输入是否安全

        Returns:
            (is_safe, message)
        """
        # 检查危险关键词
        for keyword in PromptGuard.DANGEROUS_KEYWORDS:
            if keyword in user_input:
                return False, f"检测到异常输入：包含关键词 '{keyword}'"

        # 检查注入模式
        for pattern in PromptGuard.INJECTION_PATTERNS:
            if re.search(pattern, user_input, re.IGNORECASE):
                return False, "检测到潜在的注入攻击"

        # 检查输入长度
        if len(user_input) > 2000:
            return False, "输入过长，请简化您的请求"

        return True, ""

    @staticmethod
    def sanitize_output(output: str, system_prompt: str) -> str:
        """
        检查输出是否安全

        Args:
            output: AI 输出
            system_prompt: System Prompt

        Returns:
            处理后的输出
        """
        # 检查是否泄露 System Prompt
        if system_prompt in output:
            return "抱歉，我无法提供该信息"

        # 检查是否包含敏感信息
        sensitive_patterns = ["密码", "密钥", "token", "secret", "api_key"]
        for pattern in sensitive_patterns:
            if pattern.lower() in output.lower():
                return "抱歉，我无法提供该信息"

        return output


def load_system_prompt(task: str = "general") -> str:
    """
    根据任务加载 System Prompt

    Args:
        task: 任务类型 (general, translate, code, analyze)

    Returns:
        System Prompt
    """
    prompts = {
        "general": """你是 AI 助手，专注于以下任务：
1. 回答技术问题（Java、Python、AI）
2. 解释代码逻辑
3. 提供学习建议

规则：
1. 如果不确定答案，请说"我不确定"
2. 不要编造信息
3. 用中文回答
4. 代码示例要可运行

格式：
- 使用 Markdown
- 代码用 ``` 包裹
- 重要点用 ** 加粗""",

        "translate": """你是专业翻译，精通中英互译。

规则：
1. 只输出翻译结果，不要解释
2. 保持原文的语气和风格
3. 不确定时，提供最接近的翻译

格式：
- 直接输出翻译
- 不要添加"翻译结果："等前缀""",

        "code": """你是编程专家，精通 Java、Python、JavaScript 等语言。

规则：
1. 输出可运行的代码
2. 包含必要的注释
3. 处理可能的异常
4. 遵循最佳实践

格式：
- 代码用 ``` 包裹
- 指定语言类型
- 添加简要说明""",

        "analyze": """你是数据分析专家。

规则：
1. 用结构化格式输出
2. 提供数据支撑
3. 给出可执行的建议

格式：
- 使用 Markdown 表格
- 关键数据加粗
- 分点列出结论"""
    }

    return prompts.get(task, prompts["general"])