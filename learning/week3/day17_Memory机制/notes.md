# Day 17 - LangChain Memory 机制

## 学习时间
2026年6月19日

## 学习目标
- 理解 Memory 的本质
- 掌握手动实现 Memory 的方法
- 理解 LangChain 的三种 Memory 类型
- 掌握 BufferMemory、SummaryMemory、BufferWindowMemory 的区别

---

## 一、什么是 Memory？

**一句话**：Memory 就是"笔记本"，记录历史对话，需要时查出来。

### 生活类比

```
你去咖啡店：
你：我要一杯美式
店员：要冰的还是热的？
你：冰的
店员：好的，冰美式一杯

店员能记住，是因为他保存了聊天记录。
```

### 为什么需要 Memory？

```
默认情况：
你：我叫小明
AI：你好，小明！
你：我叫什么？
AI：你叫什么？  ← AI 忘了！

原因：大模型每次调用都是独立的，没有"记忆"。
```

---

## 二、Memory 的本质

### 核心原理

```python
# 1. 创建一个列表存储历史
history = []

# 2. 每次对话都追加进去
history.append({"role": "user", "content": "我叫小明"})
history.append({"role": "assistant", "content": "你好，小明！"})

# 3. 需要时从里面查找历史
for item in history:
    if "我叫" in item["content"]:
        name = item["content"].replace("我叫", "")
        print(f"你叫{name}")
```

### 工作流程

```
第一次对话：
你："我叫小明"
    ↓
[Memory 记录: {input: "我叫小明", output: "你好，小明！"}]
    ↓
AI："你好，小明！"

第二次对话：
你："我叫什么？"
    ↓
[Memory 读取历史 + 新问题一起发给 AI]
    ↓
AI："你叫小明呀！"  ← 记住了！
```

---

## 三、手动实现 Memory

### 代码实现

```python
history = []

def chat(user_input):
    # 1. 存用户输入
    history.append({"role": "user", "content": user_input})

    # 2. 如果用户问"我叫什么"，从历史里找
    if "我叫什么" in user_input or "我是谁" in user_input:
        for item in history:
            if item["role"] == "user" and "我叫" in item["content"]:
                name = item["content"].replace("我叫", "")
                return f"你叫{name}呀！"

    # 3. 存 AI 回复
    ai_response = f"收到：{user_input}"
    history.append({"role": "assistant", "content": ai_response})

    return ai_response

# 测试
print(chat("我叫小明"))      # 收到
print(chat("我喜欢苹果"))    # 收到
print(chat("我叫什么？"))    # 你叫小明呀！
```

### 运行结果

```
第1轮： 收到：我叫小明
第2轮： 收到：我喜欢苹果
第3轮： 你叫小明呀！
```

---

## 四、LangChain 实现 Memory

### 代码实现

```python
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

load_dotenv()

llm = ChatOpenAI(
    model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
    openai_api_key=os.getenv("DEEPSEEK_API_KEY"),
    openai_api_base=os.getenv("DEEPSEEK_BASE_URL"),
    temperature=0
)

# 手动实现 Memory（本质就是 history 列表）
history = []

def chat(user_input):
    # 1. 存用户输入
    history.append(HumanMessage(content=user_input))
    # 2. 把整个历史发给 AI
    response = llm.invoke(history)
    # 3. 存 AI 回复
    history.append(response)
    return response.content

# 测试
print("第1轮：", chat("你好，我叫小明"))
print("第2轮：", chat("我喜欢吃苹果"))
print("第3轮：", chat("你还记得我叫什么吗？"))
```

### 运行结果

```
第1轮： 你好，小明！很高兴认识你！😊
第2轮： 哈哈，苹果可是个健康又美味的选择！🍎
第3轮： 当然记得啦！你刚才说过自己叫小明～😊
```

### 对比手动实现

| 手动实现 | LangChain 实现 |
|----------|----------------|
| `history.append({"role": "user", "content": "..."})` | `history.append(HumanMessage(content="..."))` |
| `history.append({"role": "assistant", "content": "..."})` | `history.append(response)` |
| 自己写逻辑找历史 | `llm.invoke(history)` 自动带上历史 |

**本质没变，都是"存历史、查历史"。**

---

## 五、Memory 的问题

### 问题：对话越来越长

```python
history = [
    {"role": "user", "content": "第1句话"},
    {"role": "assistant", "content": "第1句回复"},
    # ... 共 2000 条记录
]
```

### 会导致什么？

1. **上下文窗口爆炸** → 超出模型限制
2. **记忆丢失** → 更早的对话可能被截断
3. **Token 消耗高** → 成本越来越高
4. **响应变慢** → 处理更多文本

---

## 六、三种 Memory 类型

### 1. BufferMemory（全部保存）

```python
from langchain.memory import ConversationBufferMemory

memory = ConversationBufferMemory(return_messages=True)
```

**特点**：
- 完整记录所有对话
- 适合短对话
- Token 消耗随对话增长

**适合场景**：
- 需要完整历史的场景
- 短对话（< 20 轮）

---

### 2. SummaryMemory（自动总结）

```python
from langchain.memory import ConversationSummaryMemory

memory = ConversationSummaryMemory(llm=llm)
```

**特点**：
- 自动总结历史对话
- 保留关键信息
- 节省 Token

**适合场景**：
- 长对话
- 需要节省成本
- 不需要完整历史

---

### 3. BufferWindowMemory（只保留最近 K 轮）

```python
from langchain.memory import ConversationBufferWindowMemory

memory = ConversationBufferWindowMemory(k=5)
```

**特点**：
- 只保留最近 K 轮对话
- 更早的对话自动丢弃
- 平衡上下文和成本

**适合场景**：
- 客服系统
- 聊天机器人
- 需要近期上下文，但不需要完整历史

---

## 七、对比实验

### 实验代码

```python
# 方式1：BufferMemory（全部存下来）
buffer_history = []
for i in range(10):
    buffer_history.append(HumanMessage(content=f"第{i+1}轮对话"))
print(f"记录条数：{len(buffer_history)}")  # 10

# 方式2：SummaryMemory（自动总结）
summary_history = []
summary_text = ""
if len(summary_history) > 6:
    # 自动总结
    summary_text = "用户连续测试记忆功能..."
    summary_history.clear()
print(f"记录条数：{len(summary_history)}")  # 0
print(f"总结内容：{summary_text}")
```

### 实验结果

| 方式 | 记录条数 | 特点 |
|------|----------|------|
| BufferMemory | 20 条 | 全部保存，完整但占空间 |
| SummaryMemory | 4 条 + 总结 | 自动压缩，省空间 |

---

## 八、核心概念总结

| 概念 | 一句话解释 |
|------|------------|
| **Memory** | "笔记本"，存历史、查历史 |
| **BufferMemory** | 全部保存，适合短对话 |
| **SummaryMemory** | 自动总结，适合长对话 |
| **BufferWindowMemory** | 只保留最近 K 轮，适合客服 |
| **history 列表** | Memory 的本质实现 |
| **HumanMessage** | LangChain 的用户消息格式 |
| **llm.invoke(history)** | 把历史一起发给 AI |

---

## 九、练习题

### 题目 1：Memory 的本质

Memory 的本质是什么？

**答案**：就是一个"笔记本"，记录历史对话，需要时查出来。

---

### 题目 2：为什么需要 Memory？

为什么默认情况下 AI 记不住之前的对话？

**答案**：因为大模型每次调用都是独立的，没有"记忆"。

---

### 题目 3：BufferMemory vs SummaryMemory

什么时候用 BufferMemory，什么时候用 SummaryMemory？

**答案**：
- 短对话用 BufferMemory
- 长对话用 SummaryMemory

---

### 题目 4：BufferWindowMemory 适合什么场景？

BufferWindowMemory 适合什么场景？

**答案**：客服系统、聊天机器人，需要近期上下文但不需要完整历史。

---

### 题目 5：LangChain 和手动实现的区别

LangChain 的 Memory 和手动实现的 history 列表有什么区别？

**答案**：本质没变，都是"存历史、查历史"，LangChain 只是封装了。

---

## 十、学习心得

- Memory 的本质 = "笔记本"，存历史、查历史
- 手动实现了 Memory（history 列表）
- LangChain 的 Memory 就是封装了手动实现
- 三种 Memory 类型适合不同场景：
  - BufferMemory：短对话
  - SummaryMemory：长对话
  - BufferWindowMemory：客服系统
- 对话越来越长会导致上下文窗口爆炸、Token 消耗高

---

## 十一、待复习内容

- [ ] Memory 的本质
- [ ] 手动实现 Memory 的方法
- [ ] LangChain 的三种 Memory 类型
- [ ] BufferMemory、SummaryMemory、BufferWindowMemory 的区别
- [ ] 什么时候用哪种 Memory

---

## 十二、下一步学习

- [ ] Day 18：聊天助手增强 + 记录持久化
- [ ] 用 Memory 知识实现聊天助手的持久化

---

## 十三、代码文件

- `01_memory_basics.py` - 手动实现 Memory
- `02_langchain_memory.py` - LangChain 实现 Memory
- `03_memory_types.py` - 三种 Memory 类型对比

---

*笔记创建时间：2026年6月19日*
*学习时长：2小时*
*掌握程度：★★★★☆*
