# Day 16 - LCEL 表达式 + Chains 链路

## 学习目标
- 理解 LCEL 核心概念
- 掌握多步 Chain 搭建
- 掌握 RunnableParallel 并行处理
- 掌握调试技巧

---

## 核心概念

### 1. 什么是 Chain？

Chain 就是**链路**，多个步骤串起来。

就像工厂的流水线：
```
原材料 → 加工1 → 加工2 → 加工3 → 成品
```

在 AI 应用里：
```
用户输入 → Prompt格式化 → LLM处理 → 输出解析 → 最终结果
```

---

### 2. 什么是 LCEL？

LCEL 是 LangChain Expression Language 的缩写，翻译过来就是 **LangChain 表达式语言**。

它的作用是：**把多个处理步骤用管道符号 `|` 连起来，形成一条处理链路。**

就像 Java 里的 Stream API：

```java
// Java Stream
list.stream()
    .filter(x -> x > 0)
    .map(x -> x * 2)
    .collect(Collectors.toList());
```

LCEL 也是类似的：

```python
# LCEL
chain = prompt | llm | output_parser
result = chain.invoke({"input": "你好"})
```

---

### 3. 核心点

1. **Chain = 多个组件串起来的处理链路**
2. **LCEL = 用 `|` 连接组件的语法**
3. **组件 = Runnable（统一接口）**
4. **执行 = `.invoke()` 触发整个链路**

---

## 基础用法

### 单步 Chain

```python
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_deepseek import ChatDeepSeek

# 创建 LLM 实例
llm = ChatDeepSeek(
    model="deepseek-chat",
    api_key="your-api-key",
    temperature=0.7
)

# 创建 Prompt
prompt = PromptTemplate.from_template("将以下内容翻译成{language}: {text}")

# 创建输出解析器
output_parser = StrOutputParser()

# 组合成 Chain
chain = prompt | llm | output_parser

# 执行
result = chain.invoke({
    "language": "英文",
    "text": "你好世界"
})
print(result)
```

---

## 多步 Chain

### 概念

Chain 可以串联多个 LLM 调用。比如：先生成代码，再解释代码。

### 数据流

```
{"chinese": "你好世界"}
       ↓
[Prompt 1] → "将以下中文翻译成英文：你好世界"
       ↓
[LLM] → AIMessage("Hello, how are you?")
       ↓
[OutputParser] → "Hello, how are you?"
       ↓
[Lambda] → {"english": "Hello, how are you?"}
       ↓
[Prompt 2] → "将以下英文翻译成法文：Hello, how are you?"
       ↓
[LLM] → AIMessage("Bonjour, comment allez-vous?")
       ↓
[OutputParser] → "Bonjour, comment allez-vous?"
       ↓
最终结果
```

### 代码示例

```python
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_deepseek import ChatDeepSeek

# LLM
llm = ChatDeepSeek(
    model="deepseek-chat",
    api_key="your-api-key",
    temperature=0.7
)

# Chain 1：中文 → 英文
to_english = PromptTemplate.from_template("将以下中文翻译成英文：{chinese}")

# Chain 2：英文 → 法文
to_french = PromptTemplate.from_template("将以下英文翻译成法文：{english}")

# 输出解析器
output_parser = StrOutputParser()

# 完整链路
chain = (
    to_english
    | llm
    | output_parser
    | (lambda text: {"english": text})  # 关键：把字符串转成字典
    | to_french
    | llm
    | output_parser
)

# 执行
result = chain.invoke({"chinese": "你好世界"})
print(result)
```

---

## RunnableParallel 并行处理

### 概念

RunnableParallel 用于**并行执行多个任务**。

就像工厂里的多条生产线，同时运行，最后把结果汇总。

### 代码示例

```python
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel
from langchain_deepseek import ChatDeepSeek

# LLM
llm = ChatDeepSeek(
    model="deepseek-chat",
    api_key="your-api-key",
    temperature=0.7
)

# 输出解析器
output_parser = StrOutputParser()

# 三个翻译 Chain
to_english = PromptTemplate.from_template("""将以下中文翻译成英文。

要求：
1. 只输出翻译结果
2. 不要添加任何解释或格式

中文：{text}""") | llm | output_parser

to_japanese = PromptTemplate.from_template("""将以下中文翻译成日文。

要求：
1. 只输出翻译结果
2. 不要添加任何解释或格式

中文：{text}""") | llm | output_parser

to_korean = PromptTemplate.from_template("""将以下中文翻译成韩文。

要求：
1. 只输出翻译结果
2. 不要添加任何解释或格式

中文：{text}""") | llm | output_parser

# 并行执行
parallel = RunnableParallel(
    english=to_english,
    japanese=to_japanese,
    korean=to_korean
)

# 执行
result = parallel.invoke({"text": "你好世界"})
print(result)
```

### 输出

```python
{
    'english': 'Hello, world.',
    'japanese': '「こんにちは、世界」',
    'korean': '안녕하세요, 세상'
}
```

### 与多步 Chain 的区别

| 多步 Chain | RunnableParallel |
|-----------|------------------|
| 依次执行 | 并行执行 |
| 上一步的输出是下一步的输入 | 各任务独立执行 |
| 一个输入，一个输出 | 一个输入，多个输出 |

---

## 调试技巧

### 方法：手动打印中间结果

用 lambda 函数在每个步骤后打印结果。

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

# 输出解析器
output_parser = StrOutputParser()

# 调试函数
def debug_step(step_name, x):
    print(f"\n{'='*50}")
    print(f"步骤: {step_name}")
    print(f"数据: {x}")
    print(f"{'='*50}")
    return x

# 翻译 Chain（带调试）
chain = (
    PromptTemplate.from_template("将以下中文翻译成英文：{text}")
    | (lambda x: debug_step("1. Prompt格式化后", x))
    | llm
    | (lambda x: debug_step("2. LLM原始响应", x))
    | output_parser
    | (lambda x: debug_step("3. 解析后的字符串", x))
)

# 执行
result = chain.invoke({"text": "你好世界"})
print("\n最终结果:", result)
```

### 输出结果

```
==================================================
步骤: 1. Prompt格式化后
数据: text='将以下中文翻译成英文：你好世界'
==================================================

==================================================
步骤: 2. LLM原始响应
数据: content='Hello world' additional_kwargs=... response_metadata=...
==================================================

==================================================
步骤: 3. 解析后的字符串
数据: Hello world
==================================================

最终结果: Hello world
```

### 输出解析

| 步骤 | 数据类型 | 说明 |
|------|---------|------|
| 1. Prompt 格式化后 | PromptValue | 格式化后的 Prompt 对象 |
| 2. LLM 原始响应 | AIMessage | 包含文本和元数据 |
| 3. 解析后的字符串 | str | 纯文本 |

### 为什么要用 OutputParser？

LLM 返回的是复杂的 AIMessage 对象，包含很多元数据。但你通常只需要文本内容。

`StrOutputParser()` 就是帮你提取 `content` 字段。

---

## 测验答案

1. B - LCEL 核心就是用 `|` 连接组件
2. B - StrOutputParser 返回字符串
3. B - RunnableParallel 是并行执行
4. B - lambda 函数做数据转换
5. B - 调试就是看中间结果

---

## 学习心得

LCEL 的管道语法让代码更简洁。多步 Chain 和 RunnableParallel 是处理复杂任务的利器。调试技巧帮助理解数据在链路中的流动过程。
