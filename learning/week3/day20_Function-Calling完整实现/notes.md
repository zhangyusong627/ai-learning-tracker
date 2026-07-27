# Day 20: Function Calling 完整实现

## 学习目标
- 掌握多个工具的定义和调用
- 实现工具调用的错误处理
- 构建实际应用场景
- 集成到聊天助手

## 学习时间
2026年6月21日

---

## 1. 今天要做什么？

### Function Calling 完整实战
基于 Day 18 的基础知识，进行更完整的实战：
- 多个工具的定义和调用
- 工具调用的错误处理
- 实际应用场景
- 集成到聊天助手

### 实际应用场景
构建一个功能完整的助手，支持：
- 天气查询
- 计算器
- 数据库查询
- 更多工具扩展

---

## 2. 核心概念

### 2.1 多工具调用

```python
from langchain_core.tools import tool

@tool
def get_weather(city: str) -> str:
    """获取指定城市的天气信息"""
    return f"{city}天气晴朗"

@tool
def calculate(expression: str) -> str:
    """计算数学表达式"""
    return str(eval(expression))

# 绑定多个工具
llm_with_tools = llm.bind_tools([get_weather, calculate])
```

### 2.2 工具调用流程

```
用户输入
    ↓
LLM 判断需要调用工具
    ↓
LLM 返回工具调用请求
    ↓
执行工具
    ↓
将结果返回给 LLM
    ↓
LLM 生成最终回答
```

### 2.3 错误处理

```python
@tool
def safe_calculate(expression: str) -> str:
    """安全计算数学表达式"""
    try:
        result = eval(expression)
        return str(result)
    except Exception as e:
        return f"计算错误：{str(e)}"
```

---

## 3. 代码示例

### 3.1 多工具调用

```python
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_deepseek import ChatDeepSeek

# 定义多个工具
@tool
def get_weather(city: str) -> str:
    """获取指定城市的天气信息"""
    weather_data = {"北京": "晴天，25度", "上海": "多云，22度", "广州": "小雨，28度"}
    return weather_data.get(city, f"{city}天气未知")

@tool
def calculate(expression: str) -> str:
    """计算数学表达式，如 '2+3*4'"""
    try:
        result = eval(expression)
        return str(result)
    except Exception as e:
        return f"计算错误：{str(e)}"

# 初始化 LLM
llm = ChatDeepSeek(model="deepseek-chat", api_key="sk-xxx", temperature=0.7)

# 绑定多个工具
llm_with_tools = llm.bind_tools([get_weather, calculate])

# 测试调用
messages = [HumanMessage(content="北京天气怎么样？2+3等于多少？")]
response = llm_with_tools.invoke(messages)

# 执行工具调用
for tool_call in response.tool_calls:
    if tool_call["name"] == "get_weather":
        result = get_weather.invoke(tool_call["args"])
    elif tool_call["name"] == "calculate":
        result = calculate.invoke(tool_call["args"])

    messages.append(response)
    messages.append(ToolMessage(content=result, tool_call_id=tool_call["id"]))

# 获取最终回答
final_response = llm_with_tools.invoke(messages)
print("最终回答：", final_response.content)
```

### 3.2 集成到聊天助手

```python
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.tools import tool
from langchain_deepseek import ChatDeepSeek
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

class ToolChatAssistant:
    """支持工具调用的聊天助手"""

    def __init__(self, api_key: str, model: str = "deepseek-chat"):
        self.llm = ChatDeepSeek(model=model, api_key=api_key, temperature=0.7)
        self.output_parser = StrOutputParser()

        # 定义工具
        self.tools = [get_weather, calculate]
        self.llm_with_tools = self.llm.bind_tools(self.tools)

        # Prompt 模板
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "你是一个有用的助手，可以使用工具来回答问题。"),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}")
        ])

        # 对话历史
        self.history = []

    def chat(self, user_input: str) -> str:
        """对话（支持工具调用）"""
        # 转换历史记录
        history_messages = self._convert_history()

        # 构造消息
        messages = history_messages + [HumanMessage(content=user_input)]

        # 调用 LLM
        response = self.llm_with_tools.invoke(messages)

        # 检查是否需要调用工具
        if response.tool_calls:
            # 执行工具调用
            messages.append(response)
            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]

                # 执行对应的工具
                tool_result = self._execute_tool(tool_name, tool_args)
                messages.append(ToolMessage(content=tool_result, tool_call_id=tool_call["id"]))

            # 获取最终回答
            final_response = self.llm_with_tools.invoke(messages)
            result = final_response.content
        else:
            result = response.content

        # 更新历史
        self.history.append({"role": "human", "content": user_input})
        self.history.append({"role": "assistant", "content": result})

        return result

    def _execute_tool(self, tool_name: str, tool_args: dict) -> str:
        """执行工具"""
        for tool in self.tools:
            if tool.name == tool_name:
                return tool.invoke(tool_args)
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
```

---

## 4. 实操任务

### 任务 1：多工具调用
创建一个支持多个工具的聊天助手。

### 任务 2：错误处理
为工具添加错误处理逻辑。

### 任务 3：新增工具
添加一个新的工具（如获取时间、查询数据库等）。

---

## 5. 测验

1. 如何绑定多个工具？
2. 工具调用的完整流程是什么？
3. 如何处理工具调用的错误？
4. 如何将工具调用集成到聊天助手？
5. ToolMessage 的作用是什么？

---

## 6. 测验答案

1. **如何绑定多个工具？**
   - 使用 `llm.bind_tools([tool1, tool2, ...])` 绑定多个工具

2. **工具调用的完整流程是什么？**
   - 用户输入 → LLM 判断 → 执行工具 → 返回结果 → LLM 回答

3. **如何处理工具调用的错误？**
   - 使用 try-except 包裹工具执行代码，捕获异常并返回错误信息

4. **如何将工具调用集成到聊天助手？**
   - 在 chat 方法中检查 response.tool_calls，执行工具，将结果通过 ToolMessage 返回给 LLM

5. **ToolMessage 的作用是什么？**
   - 将工具执行结果返回给 LLM 的桥梁，让 LLM 知道工具调用的结果

---

## 7. 实现思路详解

### 7.1 核心架构

```
用户输入
    ↓
LLM（带工具）
    ↓
判断是否需要调用工具
    ↓
如果需要：
    - 返回工具调用请求
    - 执行工具
    - 将结果通过 ToolMessage 返回
    - LLM 生成最终回答
如果不需要：
    - 直接生成回答
```

### 7.2 关键组件

| 组件 | 作用 |
|------|------|
| @tool | 定义工具函数 |
| bind_tools() | 绑定工具到 LLM |
| tool_calls | LLM 返回的工具调用请求 |
| ToolMessage | 将工具结果返回给 LLM |
| try-except | 错误处理 |

### 7.3 组合调用流程

```
用户输入："北京天气怎么样？现在几点了？"
    ↓
LLM 判断：需要调用 get_weather 和 get_current_time
    ↓
LLM 返回：[
    {"name": "get_weather", "args": {"city": "北京"}},
    {"name": "get_current_time", "args": {}}
]
    ↓
执行工具：
    - get_weather("北京") → "晴天，25度"
    - get_current_time() → "2026-06-20 19:05:25"
    ↓
将结果通过 ToolMessage 返回给 LLM
    ↓
LLM 生成最终回答
```

---

## 8. 学习心得

1. **多工具绑定很灵活** - bind_tools() 可以绑定任意数量的工具
2. **LLM 自动选择工具** - 根据用户输入和工具描述，LLM 自动判断调用哪个工具
3. **ToolMessage 是关键** - 将工具结果返回给 LLM 的桥梁
4. **错误处理很重要** - 工具执行可能失败，需要 try-except 包裹
5. **组合调用很强大** - 一次请求可以调用多个工具，提高效率
