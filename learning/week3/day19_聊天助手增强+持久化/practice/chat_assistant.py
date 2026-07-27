"""
聊天助手 - LangChain 版本
基于 Day 19: 聊天助手增强+记录持久化
"""

import json
import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_deepseek import ChatDeepSeek
from langchain_core.messages import HumanMessage, AIMessage

load_dotenv()


class ChatAssistant:
    """基于 LangChain 的聊天助手"""

    def __init__(self, api_key: str, model: str = "deepseek-chat"):
        self.llm = ChatDeepSeek(model=model, api_key=api_key, temperature=0.7)
        self.output_parser = StrOutputParser()

        # Prompt 模板（包含历史记录占位符）
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "你是一个有用的助手，请用中文回答问题。"),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}")
        ])

        # 创建 Chain
        self.chain = self.prompt | self.llm | self.output_parser

        # 对话历史
        self.history: list[dict] = []

        # 历史记录文件
        self.history_file = Path("chat_history.json")

        # 加载历史记录
        self.load_history()

    def load_history(self):
        """从文件加载历史记录"""
        if self.history_file.exists():
            with open(self.history_file, "r", encoding="utf-8") as f:
                self.history = json.load(f)
            print(f"✅ 已加载 {len(self.history)} 条历史记录")

    def save_history(self):
        """保存历史记录到文件"""
        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)

    def chat(self, user_input: str) -> str:
        """对话"""
        # 转换历史记录格式
        history_messages = self._convert_history()

        # 调用 Chain
        result = self.chain.invoke({
            "history": history_messages,
            "input": user_input
        })

        # 更新历史
        self.history.append({"role": "human", "content": user_input})
        self.history.append({"role": "assistant", "content": result})

        # 保存历史
        self.save_history()

        return result

    def _convert_history(self):
        """将历史记录转换为 LangChain 消息格式"""
        messages = []
        for item in self.history:
            if item["role"] == "human":
                messages.append(HumanMessage(content=item["content"]))
            elif item["role"] == "assistant":
                messages.append(AIMessage(content=item["content"]))
        return messages

    def clear_history(self):
        """清除历史记录"""
        self.history = []
        self.save_history()
        print("✅ 历史记录已清除")

    def show_history(self):
        """显示历史记录"""
        if not self.history:
            print("📝 暂无历史记录")
            return

        print(f"\n📝 历史记录 ({len(self.history) // 2} 轮对话):")
        print("-" * 50)
        for i in range(0, len(self.history), 2):
            human = self.history[i]["content"]
            assistant = self.history[i + 1]["content"] if i + 1 < len(self.history) else ""
            print(f"👤 你: {human}")
            print(f"🤖 助手: {assistant}")
            print()


def main():
    """主函数"""
    # 配置
    API_KEY = os.environ["DEEPSEEK_API_KEY"]

    # 创建助手
    assistant = ChatAssistant(api_key=API_KEY)

    print("=" * 50)
    print("🤖 聊天助手 (LangChain 版本)")
    print("=" * 50)
    print("输入 'quit' 退出")
    print("输入 'clear' 清除历史")
    print("输入 'history' 查看历史")
    print("=" * 50)

    while True:
        user_input = input("\n👤 你: ").strip()

        if not user_input:
            continue

        if user_input.lower() == "quit":
            print("👋 再见！")
            break

        if user_input.lower() == "clear":
            assistant.clear_history()
            continue

        if user_input.lower() == "history":
            assistant.show_history()
            continue

        # 对话
        result = assistant.chat(user_input)
        print(f"\n🤖 助手: {result}")


if __name__ == "__main__":
    main()
