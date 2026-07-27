# learning/week3/day18_OutputParser+Function-Calling/practice/function_calling.py

import os

from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langchain_deepseek import ChatDeepSeek

load_dotenv()

# 创建 LLM 实例
llm = ChatDeepSeek(
    model="deepseek-chat",
    api_key=os.environ["DEEPSEEK_API_KEY"],
    temperature=0.7
)

# 定义一个工具（函数）
@tool
def get_weather(city: str) -> str:
    """获取指定城市的天气信息"""
    # 这里模拟调用天气 API
    weather_data = {
        "北京": "晴天，25度",
        "上海": "多云，22度",
        "广州": "小雨，28度"
    }
    return weather_data.get(city, f"{city}天气未知")

# 查看工具信息
print("工具名称：", get_weather.name)
print("工具描述：", get_weather.description)
print("工具参数：", get_weather.args)


# 将工具绑定到 LLM
llm_with_tools = llm.bind_tools([get_weather])

# 用户提问
messages = [HumanMessage(content="北京天气怎么样？")]

# LLM 判断需要调用工具
response = llm_with_tools.invoke(messages)

print("\nLLM 响应：", response)
print("工具调用：", response.tool_calls)

# 执行工具调用
tool_result = get_weather.invoke(response.tool_calls[0]["args"])
print("\n工具执行结果：", tool_result)

# 把结果返回给 LLM
from langchain_core.messages import ToolMessage

messages.append(response)  # 添加 LLM 的响应
messages.append(ToolMessage(content=tool_result, tool_call_id=response.tool_calls[0]["id"]))  # 添加工具结果

# LLM 用工具结果回答用户
final_response = llm_with_tools.invoke(messages)
print("\n最终回答：", final_response.content)
