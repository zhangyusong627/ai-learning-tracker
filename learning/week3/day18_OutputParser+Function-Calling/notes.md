# Day 18 - OutputParser + Function Calling

## 学习时间
2026年6月19日

## 学习目标
- 掌握 OutputParser 各类型
- 理解 Function Calling 原理
- 掌握 Function Calling 完整流程
- 理清 Prompt/ContextWindow/Skills/FunctionCalling/MCP 的区别

---

## 一、OutputParser（输出解析器）

### 1.1 什么是 OutputParser？

OutputParser 就是**输出解析器**，把 LLM 的原始输出转换成你想要的格式。

### 1.2 生活类比

```
厨师（LLM）做好了菜
    ↓
服务员（OutputParser）把菜端给你
    ↓
你吃到的是摆盘精美的菜
```

LLM 返回的是复杂的 AIMessage 对象，包含很多元数据。但你通常只需要文本内容，或者需要 JSON 格式。

OutputParser 就是帮你做这个转换的。

---

### 1.3 常见的 OutputParser

| Parser | 作用 | 输出类型 |
|--------|------|---------|
| StrOutputParser | 提取文本 | str |
| JsonOutputParser | 返回 JSON | dict |

---

### 1.4 StrOutputParser 示例

```python
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_deepseek import ChatDeepSeek

# LLM
llm = ChatDeepSeek(
    model="deepseek-chat",
    api_key="your-api-key",
    temperature=0.7
)

# Prompt
prompt = PromptTemplate.from_template("用一句话介绍{city}")

# Chain
chain = prompt | llm | StrOutputParser()

# 执行
result = chain.invoke({"city": "北京"})
print(result)  # 输出：北京是中国的首都，一座融合了悠久历史与现代文明的文化名城。
print(type(result))  # <class 'str'>
```

---

### 1.5 JsonOutputParser 示例

```python
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_deepseek import ChatDeepSeek

# LLM
llm = ChatDeepSeek(
    model="deepseek-chat",
    api_key="your-api-key",
    temperature=0.7
)

# JsonOutputParser
json_parser = JsonOutputParser()

# Prompt（告诉 LLM 返回 JSON）
prompt = PromptTemplate.from_template("""请用 JSON 格式介绍{city}。

{format_instructions}

城市信息：""")

# Chain
chain = prompt | llm | json_parser

# 执行
result = chain.invoke({
    "city": "北京",
    "format_instructions": json_parser.get_format_instructions()
})
print(result)  # 输出：{'城市名称': '北京', '英文名称': 'Beijing', ...}
print(type(result))  # <class 'dict'>
```

---

### 1.6 OutputParser 总结

| Parser | 输出类型 | 用途 |
|--------|---------|------|
| StrOutputParser | str | 提取纯文本 |
| JsonOutputParser | dict | 返回 JSON 格式 |

---

## 二、Function Calling（函数调用）

### 2.1 什么是 Function Calling？

Function Calling 就是**让 LLM 调用你定义的函数**。

### 2.2 生活类比

想象你在和 Siri 对话：

```
你：明天天气怎么样？
Siri：让我查一下天气 API...（调用 get_weather 函数）
Siri：明天晴天，25度
```

Siri 不是自己知道天气，而是调用了天气 API。

Function Calling 也是一样：LLM 不是自己知道所有信息，而是可以调用你定义的函数来获取信息。

---

### 2.3 Function Calling 的工作流程

```
1. 你定义一个函数（比如 get_weather）
2. 你告诉 LLM 这个函数是干什么的
3. 用户问问题（比如"明天天气怎么样"）
4. LLM 判断需要调用 get_weather 函数
5. LLM 返回函数名和参数
6. 你执行函数，把结果返回给 LLM
7. LLM 用函数结果回答用户
```

---

### 2.4 为什么需要 Function Calling？

LLM 的局限：
- 不知道实时信息（天气、股票、新闻）
- 不能执行代码
- 不能访问数据库
- 不能发邮件

Function Calling 让 LLM 可以：
- 查询实时信息
- 执行计算
- 访问数据库
- 调用外部 API

---

### 2.5 代码示例

```python
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_deepseek import ChatDeepSeek

# LLM
llm = ChatDeepSeek(
    model="deepseek-chat",
    api_key="your-api-key",
    temperature=0.7
)

# 定义工具（函数）
@tool
def get_weather(city: str) -> str:
    """获取指定城市的天气信息"""
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
print("LLM 响应：", response)
print("工具调用：", response.tool_calls)

# 执行工具调用
tool_result = get_weather.invoke(response.tool_calls[0]["args"])
print("工具执行结果：", tool_result)

# 把结果返回给 LLM
messages.append(response)
messages.append(ToolMessage(
    content=tool_result,
    tool_call_id=response.tool_calls[0]["id"]
))

# LLM 用工具结果回答用户
final_response = llm_with_tools.invoke(messages)
print("最终回答：", final_response.content)
```

---

### 2.6 运行结果

```
工具名称： get_weather
工具描述： 获取指定城市的天气信息
工具参数： {'city': {'title': 'City', 'type': 'string'}}

LLM 响应： content='好的，我来查询一下北京的天气情况。' ... tool_calls=[{'name': 'get_weather', 'args': {'city': '北京'}, ...}]

工具执行结果： 晴天，25度

最终回答： 北京当前的天气是**晴天**，气温**25度**，天气不错，非常适合外出活动哦！☀️
```

---

### 2.7 Function Calling 完整流程

```
用户问："北京天气怎么样？"
       ↓
LLM 判断：需要调用 get_weather 工具
       ↓
LLM 返回：tool_calls=[{name: "get_weather", args: {city: "北京"}}]
       ↓
执行工具：get_weather("北京") → "晴天，25度"
       ↓
把结果返回给 LLM
       ↓
LLM 回答："北京当前天气是晴天，25度，非常适合外出活动！"
```

---

### 2.8 关键点总结

| 步骤 | 说明 |
|------|------|
| 1. 定义工具 | 用 `@tool` 装饰器 |
| 2. 绑定工具 | `llm.bind_tools([tool])` |
| 3. LLM 判断 | 返回 `tool_calls` |
| 4. 执行工具 | `tool.invoke(args)` |
| 5. 返回结果 | 用 `ToolMessage` 包装 |
| 6. LLM 回答 | 用工具结果生成最终回答 |

---

## 三、概念辨析

### 3.1 Prompt

```python
# Prompt 就是你给 LLM 的输入
prompt = "请用Python写一个登录函数"
```

**作用**：告诉 LLM 你要什么

---

### 3.2 ContextWindow

```
LLM 能处理的最大文本长度

比如：128K tokens ≈ 10万字

输入 + 输出 = 不能超过这个限制
```

**作用**：LLM 的"工作台"大小

---

### 3.3 Skills

```markdown
# Skills = Prompt + 流程编排
当用户说"部署"时：
1. 运行 npm run build
2. 检查 dist 目录
3. 上传到服务器
```

**作用**：让 Claude Code 自动执行重复任务

---

### 3.4 FunctionCalling

```python
# 定义一个函数
@tool
def get_weather(city: str) -> str:
    """获取天气"""
    return "晴天，25度"

# LLM 可以调用这个函数
llm.bind_tools([get_weather])
```

**作用**：让 LLM 调用外部 API/函数

---

### 3.5 MCP（Model Context Protocol）

```
MCP = 标准化的协议

让 LLM 可以统一调用各种外部工具：
- 数据库
- API
- 文件系统
- 第三方服务
```

**作用**：统一 LLM 与外部工具的交互方式

---

### 3.6 它们之间的关系

```
用户输入
    ↓
[Prompt] → 给 LLM 的指令
    ↓
[ContextWindow] → LLM 处理（受窗口大小限制）
    ↓
    ├── 直接回答
    ↓
    ├── 调用 [FunctionCalling] → 执行外部函数
    ↓
    └── 使用 [Skills] → 按流程执行
    ↓
[MCP] → 标准化调用外部工具
```

---

### 3.7 总结对比

| 概念 | 是什么 | 谁用 |
|------|--------|------|
| Prompt | 输入指令 | 你给 LLM |
| ContextWindow | 处理能力 | LLM 自己 |
| Skills | 流程编排 | Claude Code |
| FunctionCalling | 调用函数 | LLM 应用 |
| MCP | 交互协议 | LLM + 外部工具 |

---

## 四、Skills vs Function Calling

### 4.1 本质区别

| | Skills | Function Calling |
|--|--------|------------------|
| **本质** | Prompt 模板 + 工作流 | LLM 调用外部函数的能力 |
| **运行环境** | Claude Code 里 | 你的 LLM 应用里 |
| **用途** | 让 Claude Code 执行重复任务 | 让 LLM 应用调用外部 API |

### 4.2 什么时候用什么？

| 场景 | 用什么 |
|------|--------|
| 用 Claude Code 开发，想让它自动执行任务 | Skills |
| 开发自己的聊天机器人/智能助手 | Function Calling |
| 开发自己的 LLM 应用 | Function Calling |

### 4.3 Skills 的价值

1. **标准化**：确保每次执行相同的任务都遵循相同的流程
2. **效率**：不需要每次都重新描述整个流程
3. **准确性**：通过预定义的步骤减少错误
4. **可复用**：团队成员可以共享相同的 Skills
5. **知识沉淀**：把最佳实践编码成 Skills

---

## 五、测验答案

1. B - Function Calling 让 LLM 调用函数获取信息
2. B - `@tool` 装饰器定义工具
3. B - `llm.bind_tools()` 绑定工具
4. B - tool_calls 是列表，包含工具名和参数
5. B - 用 `ToolMessage` 包装后返回

---

## 六、学习心得

- OutputParser 把 LLM 输出转成你想要的格式
- Function Calling 让 LLM 可以调用外部函数
- Function Calling 完整流程：定义工具 → 绑定工具 → LLM 判断 → 执行工具 → 返回结果 → LLM 回答
- Skills 是 Prompt + 流程编排，给 Claude Code 用
- FunctionCalling 是 LLM 调用外部函数的能力，给你的应用用
- MCP 是标准化协议，统一 LLM 与外部工具的交互

---

## 七、代码文件

- `output_parser.py` - OutputParser 示例
- `function_calling.py` - Function Calling 示例

---

*笔记创建时间：2026年6月19日*
*学习时长：2小时*
*掌握程度：★★★★☆*
