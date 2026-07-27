"""
Function Calling 完整实现 - 多工具聊天助手
基于 Day 20: Function Calling 完整实现
"""

import json
import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.tools import tool
from langchain_deepseek import ChatDeepSeek
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

load_dotenv()


# ==================== 定义工具 ====================

@tool
def get_weather(city: str) -> str:
    """获取指定城市的天气信息"""
    weather_data = {
        "北京": "晴天，25度，适合外出",
        "上海": "多云，22度，微风",
        "广州": "小雨，28度，记得带伞",
        "深圳": "晴天，27度，阳光明媚"
    }
    return weather_data.get(city, f"{city}天气信息暂无，请自行查询")


@tool
def calculate(expression: str) -> str:
    """计算数学表达式，如 '2+3*4' 或 '10/2'"""
    try:
        # 安全计算（实际项目中应使用更安全的计算方式）
        result = eval(expression)
        return f"计算结果：{expression} = {result}"
    except ZeroDivisionError:
        return "计算错误：除数不能为零"
    except Exception as e:
        return f"计算错误：{str(e)}"


@tool
def get_current_time() -> str:
    """获取当前时间"""
    now = datetime.now()
    return f"当前时间：{now.strftime('%Y-%m-%d %H:%M:%S')}"


@tool
def search_knowledge(query: str) -> str:
    """搜索知识库"""
    # 模拟知识库搜索
    knowledge = {
        "python": "Python 是一种解释型、面向对象的高级编程语言",
        "langchain": "LangChain 是用于构建 LLM 应用的框架",
        "ai": "人工智能是模拟人类智能的技术"
    }

    query_lower = query.lower()
    results = []
    for key, value in knowledge.items():
        if key in query_lower:
            results.append(value)

    if results:
        return "搜索结果：\n" + "\n".join(results)
    return "未找到相关知识"


# ==================== 聊天助手类 ====================

class ToolChatAssistant:
    """支持工具调用的聊天助手"""

    def __init__(self, api_key: str, model: str = "deepseek-chat"):
        self.llm = ChatDeepSeek(model=model, api_key=api_key, temperature=0.7)
        self.output_parser = StrOutputParser()

        # 定义工具列表
        self.tools = [get_weather, calculate, get_current_time, search_knowledge]

        # 绑定工具到 LLM
        self.llm_with_tools = self.llm.bind_tools(self.tools)

        # Prompt 模板
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "你是一个有用的助手，可以使用工具来回答问题。请根据用户需求选择合适的工具。"),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}")
        ])

        # 对话历史
        self.history: list[dict] = []
        self.history_file = Path("tool_chat_history.json")

        # 加载历史记录
        self.load_history()

    def load_history(self):
        """从文件加载历史记录"""
        if self.history_file.exists():
            with open(self.history_file, "r", encoding="utf-8") as f:
                self.history = json.load(f)
            print(f"✅ 已加载 {len(self.history) // 2} 轮历史记录")

    def save_history(self):
        """保存历史记录到文件"""
        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)

    def chat(self, user_input: str) -> str:
        """对话（支持工具调用）"""
        # 1. 转换历史记录
        history_messages = self._convert_history()

        # 2. 构造消息列表
        messages = history_messages + [HumanMessage(content=user_input)]

        # 3. 调用 LLM（带工具）
        response = self.llm_with_tools.invoke(messages)

        # 4. 检查是否需要调用工具
        if response.tool_calls:
            print(f"\n🔧 检测到工具调用：")
            for tool_call in response.tool_calls:
                print(f"   - {tool_call['name']}({tool_call['args']})")

            # 5. 执行工具调用
            messages.append(response)
            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                tool_id = tool_call["id"]

                # 执行对应的工具
                tool_result = self._execute_tool(tool_name, tool_args)
                print(f"   📊 结果：{tool_result}")

                # 将结果返回给 LLM
                messages.append(ToolMessage(content=tool_result, tool_call_id=tool_id))

            # 6. 获取最终回答
            final_response = self.llm_with_tools.invoke(messages)
            result = final_response.content
        else:
            # 没有工具调用，直接返回
            result = response.content

        # 7. 更新历史
        self.history.append({"role": "human", "content": user_input})
        self.history.append({"role": "assistant", "content": result})
        self.save_history()

        return result

    def _execute_tool(self, tool_name: str, tool_args: dict) -> str:
        """执行工具"""
        for t in self.tools:
            if t.name == tool_name:
                try:
                    return t.invoke(tool_args)
                except Exception as e:
                    return f"工具执行错误：{str(e)}"
        return f"未知工具：{tool_name}"

    def _convert_history(self):
        """转换历史记录格式"""
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

    def show_tools(self):
        """显示可用工具"""
        print("\n🔧 可用工具：")
        print("-" * 50)
        for t in self.tools:
            print(f"   - {t.name}: {t.description}")


def main():
    """主函数"""
    # 配置
    API_KEY = os.environ["DEEPSEEK_API_KEY"]

    # 创建助手
    assistant = ToolChatAssistant(api_key=API_KEY)

    print("=" * 50)
    print("🤖 工具聊天助手 (Function Calling)")
    print("=" * 50)
    print("输入 'quit' 退出")
    print("输入 'clear' 清除历史")
    print("输入 'history' 查看历史")
    print("输入 'tools' 查看可用工具")
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

        if user_input.lower() == "tools":
            assistant.show_tools()
            continue

        # 对话
        result = assistant.chat(user_input)
        print(f"\n🤖 助手: {result}")


if __name__ == "__main__":
    main()
