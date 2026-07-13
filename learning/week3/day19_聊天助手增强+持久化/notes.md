# Day 19: 聊天助手增强+记录持久化

## 学习目标
- 构建一个完整的聊天助手
- 实现对话记录持久化
- 综合运用之前学的所有知识

## 学习时间
2026年6月20日

---

## 1. 今天要做什么？

### 聊天助手增强
把之前学的所有组件整合起来，构建一个功能完整的聊天助手：
- PromptTemplate（模板化）
- LCEL（链式调用）
- Memory（多轮对话）
- OutputParser（格式化输出）
- Function Calling（工具调用）

### 记录持久化
把对话记录保存到文件，下次打开可以继续聊天：
- 保存对话历史到 JSON 文件
- 从文件加载历史记录
- 实现"记忆"功能

---

## 2. 核心概念

### 2.1 聊天助手架构

```
用户输入
    ↓
PromptTemplate（格式化）
    ↓
ChatModel（LLM）
    ↓
OutputParser（解析）
    ↓
返回结果
```

### 2.2 持久化原理

```
对话记录 → JSON 文件（保存）
JSON 文件 → 对话记录（加载）
```

### 2.3 完整流程

```
1. 加载历史记录
2. 用户输入
3. 格式化 Prompt（包含历史）
4. LLM 处理
5. 解析输出
6. 保存新记录
7. 返回结果
```

---

## 3. 代码示例

### 3.1 基础聊天助手

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_deepseek import ChatDeepSeek

# 初始化
llm = ChatDeepSeek(model="deepseek-chat", api_key="sk-xxx", temperature=0.7)
output_parser = StrOutputParser()

# 创建 Prompt 模板
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个有用的助手，请用中文回答问题。"),
    ("human", "{input}")
])

# 创建 Chain
chain = prompt | llm | output_parser

# 调用
result = chain.invoke({"input": "你好，我是小明"})
print(result)
```

### 3.2 带 Memory 的聊天助手

```python
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_deepseek import ChatDeepSeek

# 初始化
llm = ChatDeepSeek(model="deepseek-chat", api_key="sk-xxx", temperature=0.7)
output_parser = StrOutputParser()

# 创建带 Memory 的 Prompt 模板
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个有用的助手，请用中文回答问题。"),
    MessagesPlaceholder(variable_name="history"),  # 历史记录占位符
    ("human", "{input}")
])

# 创建 Chain
chain = prompt | llm | output_parser

# 模拟对话
history = []
result1 = chain.invoke({"history": history, "input": "你好，我是小明"})
print("助手：", result1)

# 更新历史
history.append(("human", "你好，我是小明"))
history.append(("assistant", result1))

result2 = chain.invoke({"history": history, "input": "我叫什么名字？"})
print("助手：", result2)
```

### 3.3 记录持久化

```python
import json
from pathlib import Path

# 保存历史到文件
def save_history(history, filename="chat_history.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

# 从文件加载历史
def load_history(filename="chat_history.json"):
    if Path(filename).exists():
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    return []
```

### 3.4 完整聊天助手

```python
import json
from pathlib import Path
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_deepseek import ChatDeepSeek

class ChatAssistant:
    def __init__(self, api_key, model="deepseek-chat"):
        self.llm = ChatDeepSeek(model=model, api_key=api_key, temperature=0.7)
        self.output_parser = StrOutputParser()
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "你是一个有用的助手，请用中文回答问题。"),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}")
        ])
        self.chain = self.prompt | self.llm | self.output_parser
        self.history = []
        self.history_file = "chat_history.json"
        self.load_history()

    def load_history(self):
        if Path(self.history_file).exists():
            with open(self.history_file, "r", encoding="utf-8") as f:
                self.history = json.load(f)

    def save_history(self):
        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)

    def chat(self, user_input):
        result = self.chain.invoke({
            "history": self.history,
            "input": user_input
        })
        self.history.append({"role": "human", "content": user_input})
        self.history.append({"role": "assistant", "content": result})
        self.save_history()
        return result
```

---

## 4. 实操任务

### 任务 1：创建聊天助手
创建一个基础的聊天助手，支持多轮对话。

### 任务 2：实现记录持久化
把对话记录保存到 JSON 文件。

### 任务 3：增强功能
添加清除历史、显示历史等功能。

---

## 5. 测验

1. MessagesPlaceholder 的作用是什么？
2. 为什么要用 MessagesPlaceholder 而不是普通变量？
3. 如何实现对话记录的持久化？
4. 聊天助手的核心组件有哪些？
5. 如何实现清除历史功能？

---

## 6. 测验答案

1. **MessagesPlaceholder 的作用是什么？**
   - 占位符，用于接收历史消息列表

2. **为什么需要 _convert_history 方法？**
   - 将 JSON 字典转换为 LangChain 消息对象

3. **聊天助手的核心组件有哪些？**
   - PromptTemplate、ChatModel、StrOutputParser、History、JSON 持久化

4. **如何实现清除历史功能？**
   - 清空列表 + 保存到文件（保证下次启动也是空的）

5. **为什么要每次对话都保存历史？**
   - 防止程序崩溃丢失记录，实现"记忆"功能

---

## 7. 实现思路详解

### 7.1 核心架构

```
用户输入
    ↓
PromptTemplate（格式化，包含历史）
    ↓
ChatModel（LLM）
    ↓
StrOutputParser（解析）
    ↓
返回结果 + 保存历史
```

### 7.2 关键组件作用

| 组件 | 作用 |
|------|------|
| ChatPromptTemplate | 定义对话格式（system + history + human） |
| MessagesPlaceholder | 接收历史消息列表 |
| HumanMessage/AIMessage | LangChain 消息对象 |
| StrOutputParser | 解析 LLM 输出为字符串 |
| JSON 文件 | 持久化历史记录 |

### 7.3 数据流

```
用户输入 → 转换历史格式 → Invoke Chain → LLM 处理 → 更新历史 → 保存文件
```

### 7.4 与 httpx 版本对比

| 方面 | httpx 版本 | LangChain 版本 |
|------|-----------|---------------|
| 调用方式 | 手动构造请求 | Chain 自动处理 |
| Memory 管理 | 手动 | 自动 |
| Prompt 模板 | 字符串拼接 | 模板化 |
| 扩展性 | 低 | 高 |
| 代码量 | 多 | 少 |

---

## 8. 学习心得

1. **MessagesPlaceholder 是核心** - 让历史记录可以作为 Prompt 的一部分传给 LLM
2. **格式转换很重要** - JSON 字典需要转换为 LangChain 消息对象
3. **持久化防止丢失** - 每次对话都保存，保证数据安全
4. **LangChain 更简洁** - 相比 httpx 直接调用，代码量少、扩展性高
5. **大模型是无状态的** - 我们通过历史记录让它看起来"有状态"
