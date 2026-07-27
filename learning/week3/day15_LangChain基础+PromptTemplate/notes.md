# Day 15 - LangChain 基础 + PromptTemplate

## 学习时间
2026年6月15日

## 学习目标
- 理解 LangChain 的作用和架构
- 掌握 Runnable 接口和管道语法
- 掌握 PromptTemplate 的使用方法

---

## 一、什么是 LangChain？

**一句话**：用于构建 LLM 应用的 Python 框架。

### Java 类比

```
LangChain 之于 LLM 应用
= Spring Boot 之于 Web 应用
```

| Spring Boot | LangChain |
|-------------|-----------|
| 简化 Web 开发 | 简化 LLM 应用开发 |
| 内置 Tomcat | 内置 LLM 调用 |
| 提供注解 | 提供模板 |
| 自动配置 | 自动串联组件 |

---

## 二、LangChain 的核心组件

| 组件 | 作用 | 对应概念 |
|------|------|----------|
| **LLM/ChatModel** | 调用大模型 | DeepSeek API 调用 |
| **PromptTemplate** | Prompt 模板 | 第二周学的 Prompt |
| **Chains** | 链式调用 | 流程编排 |
| **Memory** | 对话记忆 | 多轮对话上下文 |
| **Tools** | 工具调用 | Function Calling |
| **Document Loaders** | 文档加载 | 文件读取 |
| **Vector Stores** | 向量数据库 | Chroma/FAISS |

---

## 三、Runnable 接口（核心）

### 什么是 Runnable？

LangChain 的所有组件都实现了统一接口：**Runnable**

```python
class Runnable:
    def invoke(self, input) -> Any:
        """同步调用"""
        pass

    async def ainvoke(self, input) -> Any:
        """异步调用"""
        pass

    def stream(self, input) -> Iterator[Any]:
        """流式输出"""
        pass
```

### 为什么这样设计？

**统一接口的好处**：

```python
# 不管是什么组件，调用方式都一样
prompt.invoke(input)      # PromptTemplate
llm.invoke(input)         # ChatModel
parser.invoke(input)      # OutputParser
chain.invoke(input)       # Chain

# 可以自由组合
chain = prompt | llm | parser
```

### Java 类比

```
Runnable ≈ Java 的 Function<T, R>

// Java
Function<String, String> func = x -> x.toUpperCase();
String result = func.apply("hello");

// LangChain
prompt = PromptTemplate.from_template("...")
result = prompt.invoke({"name": "张三"})
```

---

## 四、管道语法 `|`

### 类比 Unix 管道

```bash
# Unix 管道：数据流从左到右
cat file.txt | grep "error" | sort | uniq -c

# LangChain 管道
chain = prompt | llm | parser
```

### 执行流程

```
输入数据
    ↓
prompt.invoke()  →  格式化后的字符串
    ↓
llm.invoke()     →  AI 的回复
    ↓
parser.invoke()  →  结构化数据
    ↓
返回结果
```

---

## 五、PromptTemplate 深入

### 1. 基本用法

```python
from langchain_core.prompts import PromptTemplate

# 创建模板
template = PromptTemplate(
    input_variables=["language", "code"],
    template="请将以下代码翻译成{language}：\n\n{code}"
)

# 调用模板
result = template.invoke({
    "language": "Python",
    "code": "public int add(int a, int b) { return a + b; }"
})

print(result.text)
```

### 2. 模板变量

```python
# {variable} 是占位符
template = "你是{role}，请用{language}回答"

# input_variables 定义需要传入的变量
input_variables = ["role", "language"]
```

### 3. 多行模板

```python
template = PromptTemplate.from_template("""
你是{role}。

背景信息：
{context}

问题：
{question}

请用{language}回答。
""")
```

---

## 六、ChatPromptTemplate

用于聊天模型的模板：

```python
from langchain_core.prompts import ChatPromptTemplate

# 创建聊天模板
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是{role}，用{language}回答"),
    ("human", "{question}")
])

# 使用模板
messages = prompt.invoke({
    "role": "翻译专家",
    "language": "中文",
    "question": "Hello, how are you?"
})
```

### 消息类型

| 类型 | 作用 |
|------|------|
| **system** | 定义 AI 行为 |
| **human** | 用户输入 |
| **ai** | AI 回复 |

---

## 七、实操代码

### 代码翻译模板

```python
from langchain_core.prompts import PromptTemplate

translate_template = PromptTemplate(
    input_variables=["language", "code"],
    template="请将以下代码翻译成{language}：\n\n{code}"
)

result = translate_template.invoke({
    "language": "Python",
    "code": "public int add(int a, int b) { return a + b; }"
})

print(result.text)
```

**输出**：
```
请将以下代码翻译成Python：

public int add(int a, int b) { return a + b; }
```

### 代码解释模板

```python
explain_template = PromptTemplate(
    input_variables=["level", "code"],
    template="""你是一个编程教育专家。

请用{level}的水平解释以下代码的功能：

{code}

解释要求：
1. 先说明代码的整体功能
2. 逐行解释关键代码"""
)

result2 = explain_template.invoke({
    "level": "初学者",
    "code": "for i in range(10): print(i)"
})

print(result2.text)
```

**输出**：
```
你是一个编程教育专家。

请用初学者的水平解释以下代码的功能：

for i in range(10): print(i)

解释要求：
1. 先说明代码的整体功能
2. 逐行解释关键代码
```

---

## 八、核心概念总结

| 概念 | 一句话解释 |
|------|------------|
| **LangChain** | LLM 应用开发框架 |
| **Runnable** | 统一接口，所有组件都实现 |
| **管道语法 \|** | 串联组件，数据从左到右流动 |
| **PromptTemplate** | Prompt 模板，支持变量替换 |
| **ChatPromptTemplate** | 聊天消息模板 |
| **invoke()** | 调用组件的核心方法 |
| **.text** | 获取模板输出的文本 |

---

## 九、练习题

### 题目 1：LangChain 是什么？

请用一句话解释 LangChain。

**答案**：LangChain 是一个用于构建 LLM 应用的 Python 框架。

---

### 题目 2：Runnable 接口

为什么 LangChain 要用统一的 Runnable 接口？

**答案**：为了可以自由组合、链式调用、统一调用方式。

---

### 题目 3：管道语法

`prompt | llm | parser` 数据流动方向是？

**答案**：从左到右。

---

### 题目 4：PromptTemplate

PromptTemplate 的 invoke() 方法做了什么？

**答案**：替换模板中的变量，返回格式化后的字符串。

---

### 题目 5：消息类型

ChatPromptTemplate 中的三种消息类型是什么？

**答案**：system、human、ai。

---

## 十、学习心得

- LangChain 之于 LLM = Spring Boot 之于 Web
- Runnable 是核心接口，所有组件都实现
- 管道语法让代码更简洁
- PromptTemplate 让 Prompt 可模板化、可复用
- invoke() 是调用组件的核心方法
- .text 获取模板输出的文本

---

## 十一、待复习内容

- [ ] LangChain 的核心组件
- [ ] Runnable 接口的作用
- [ ] 管道语法的执行流程
- [ ] PromptTemplate 的创建和调用
- [ ] ChatPromptTemplate 的消息类型

---

## 十二、下一步学习

- [ ] Day 16：LCEL 表达式+Chains 链路
- [ ] 深入学习 LangChain 的链式调用

---

*笔记创建时间：2026年6月15日*
*学习时长：2小时*
*掌握程度：★★★☆☆*