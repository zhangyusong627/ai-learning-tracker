# Day 26: 文本切分策略

## 学习目标
- 理解 RAG 中为什么必须做文本切分
- 掌握 LangChain 官方的 7 种切分器
- 学会用 LangChain TextSplitter 做切分
- 理解 chunk_size 和 chunk_overlap 对检索质量的影响

## 学习时间
2026年7月4日

---

## 1. 为什么需要文本切分？

```
RAG 检索的瓶颈：

一篇 50 页的 PDF（约 3 万字）
├── Embedding 模型上限：通常 512~8192 Token
├── 向量数据库：存一个大向量 vs 存 100 个小向量
└── 检索精度：大段文本 → 语义模糊，小段文本 → 语义精准

结论：必须把长文档切成小块（Chunk），每块单独做 Embedding 存入向量库
```

### 切分好坏直接决定 RAG 效果

| 切分太粗 | 切分太细 |
|---------|---------|
| 检索命中但答案被淹没在大段文本里 | 丢失上下文，回答不完整 |
| LLM 上下文窗口被浪费 | Chunk 数量爆炸，存储和检索成本高 |

### 核心原因

1. **语义稀释**：Embedding 输出维度固定（如 512 维），长文本会被压缩，细节丢失
2. **检索粒度**：需要更精确的匹配，找到相关的段落而非整篇文章
3. **上下文窗口**：LLM 有长度限制，不能把整篇文章都给它

---

## 2. LangChain 官方切分器（7种）

**官方文档**：https://python.langchain.com/docs/concepts/text_splitters/

| 切分器 | 类型 | 适用场景 | 推荐度 |
|--------|------|----------|--------|
| CharacterTextSplitter | 按字符 | 最简单，快速原型 | ⭐⭐ |
| RecursiveCharacterTextSplitter | 递归字符 | ⭐ 推荐，大多数场景 | ⭐⭐⭐⭐⭐ |
| TokenTextSplitter | 按 Token | 考虑模型 Token 限制 | ⭐⭐⭐⭐ |
| MarkdownHeaderTextSplitter | 按 Markdown 标题 | Markdown 文档 | ⭐⭐⭐⭐ |
| HTMLHeaderTextSplitter | 按 HTML 标签 | HTML 文档 | ⭐⭐⭐ |
| SemanticChunker | 语义切分 | 高质量问答系统 | ⭐⭐⭐⭐ |
| SentenceTransformersTokenTextSplitter | Sentence-Transformers | 使用 ST 模型时 | ⭐⭐⭐ |

---

## 3. 各切分器详解

### 3.1 CharacterTextSplitter（按字符切分）

```python
from langchain_text_splitters import CharacterTextSplitter

splitter = CharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    separator="\n"  # 按换行符切分
)

text = "你的长文本..."
chunks = splitter.split_text(text)
```

**优点**：实现最简单，速度快
**缺点**：不关心语义边界，可能切断句子/段落
**适用**：快速原型、对质量要求不高的场景

---

### 3.2 RecursiveCharacterTextSplitter（递归字符切分）⭐ 推荐

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    separators=["\n\n", "\n", "。", "！", "？", "，", " ", ""],
    length_function=len
)

text = "你的长文本..."
chunks = splitter.split_text(text)
```

**切分优先级**：`\n\n`（段落）→ `\n`（换行）→ `。！？`（句子）→ `，`（逗号）→ ` `（空格）→ `""`（字符）

**逻辑**：
1. 先尝试按段落（`\n\n`）切分
2. 如果某段超过 chunk_size，再按 `\n` 切
3. 如果还超，按句子（`。！？`）切
4. 最后才按单个字符切

**优点**：保留语义边界，效果好
**缺点**：需要选择合适的 separator
**适用**：大多数 RAG 场景（推荐首选）

---

### 3.3 TokenTextSplitter（按 Token 切分）

```python
from langchain_text_splitters import TokenTextSplitter

splitter = TokenTextSplitter(
    chunk_size=100,  # 按 Token 数切分
    chunk_overlap=20
)

text = "你的长文本..."
chunks = splitter.split_text(text)
```

**优点**：考虑模型 Token 限制，更精确
**缺点**：需要 Token 计算库
**适用**：需要精确控制 Token 数量的场景

---

### 3.4 MarkdownHeaderTextSplitter（按 Markdown 标题切分）

```python
from langchain_text_splitters import MarkdownHeaderTextSplitter

headers_to_split_on = [
    ("#", "标题1"),
    ("##", "标题2"),
    ("###", "标题3"),
]

splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)

markdown_text = """
# 第一章 介绍
这是介绍内容。

## 1.1 背景
这是背景内容。

## 1.2 目标
这是目标内容。

# 第二章 方法
这是方法内容。
"""

chunks = splitter.split_text(markdown_text)
```

**优点**：天然保留文档结构，按标题层级切分
**缺点**：只适用于 Markdown 格式
**适用**：Markdown 文档、技术文档

---

### 3.5 HTMLHeaderTextSplitter（按 HTML 标签切分）

```python
from langchain_text_splitters import HTMLHeaderTextSplitter

headers_to_split_on = [
    ("h1", "标题1"),
    ("h2", "标题2"),
    ("h3", "标题3"),
]

splitter = HTMLHeaderTextSplitter(headers_to_split_on=headers_to_split_on)

html_text = """
<h1>第一章</h1>
<p>这是内容。</p>
<h2>1.1 小节</h2>
<p>这是小节内容。</p>
"""

chunks = splitter.split_text(html_text)
```

**优点**：按 HTML 结构切分
**缺点**：只适用于 HTML 格式
**适用**：HTML 文档、网页内容

---

### 3.6 SemanticChunker（语义切分）

```python
from langchain_experimental.text_splitter import SemanticChunker
from langchain_community.embeddings import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-small-zh-v1.5")

splitter = SemanticChunker(
    embeddings,
    breakpoint_threshold_type="percentile",  # 使用百分位数
    breakpoint_threshold_amount=85  # 85% 百分位
)

text = "你的长文本..."
chunks = splitter.split_text(text)
```

**原理**：
1. 先对每个句子做 Embedding
2. 计算相邻句子的余弦相似度
3. 当相似度突然下降时 → 话题切换 → 在此切分

**优点**：语义最连贯，检索质量最高
**缺点**：需要调用 Embedding 模型，速度慢、成本高
**适用**：高质量问答系统、知识库

---

### 3.7 SentenceTransformersTokenTextSplitter

```python
from langchain_text_splitters import SentenceTransformersTokenTextSplitter

splitter = SentenceTransformersTokenTextSplitter(
    chunk_size=100,
    model_name="BAAI/bge-small-zh-v1.5"
)

text = "你的长文本..."
chunks = splitter.split_text(text)
```

**优点**：使用 Sentence-Transformers 模型，Token 计算更准确
**缺点**：需要安装 sentence-transformers
**适用**：使用 Sentence-Transformers 模型时

---

## 4. 核心参数：chunk_size 和 chunk_overlap

### chunk_size（块大小）

```
chunk_size = 每个 Chunk 的最大字符数（或 Token 数）

常见选择：
├── 256 tokens  → 精准检索，适合短问答
├── 512 tokens  → 平衡选择（推荐起点）
├── 1024 tokens → 适合需要上下文的场景
└── 2048+ tokens → 接近全文，一般不推荐

经验法则：先用 512，根据实际效果调整
```

### chunk_overlap（重叠区域）

```
为什么需要重叠？

无重叠：
Chunk 1: [...AAAA]
Chunk 2: [BBBB...]  ← A 和 B 之间的关联被切断

有重叠（overlap=50）：
Chunk 1: [...AAAABBB]
Chunk 2: [AABBBBB...]  ← 重叠区域保持上下文连贯

常见选择：chunk_size 的 10%~20%
例如 chunk_size=500 → overlap=50~100
```

### 参数选择对比表

| 场景 | chunk_size | chunk_overlap | 理由 |
|------|-----------|---------------|------|
| 短问答（FAQ） | 256 | 50 | 精准匹配问题 |
| 通用问答 | 512 | 100 | 平衡精度和上下文 |
| 长文档摘要 | 1024 | 200 | 需要更多上下文 |
| 代码检索 | 按函数 | 1 行 | 保持函数完整性 |

---

## 5. 实操任务

### 任务 1：手写固定长度切分

```python
def fixed_size_chunk(text, chunk_size=500, overlap=50):
    """纯手写固定长度切分"""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
    return chunks

# 测试
text = "这是一段测试文本。" * 100
chunks = fixed_size_chunk(text, chunk_size=200, overlap=20)
print(f"切分成 {len(chunks)} 块")
```

### 任务 2：手写按句子切分

```python
import re

def sentence_split(text, chunk_size=500):
    """按句子切分，保证不在句子中间断开"""
    sentences = re.split(r'(?<=[。！？.!?])', text)
    chunks = []
    current = ""
    for sent in sentences:
        if len(current) + len(sent) > chunk_size:
            chunks.append(current.strip())
            current = sent
        else:
            current += sent
    if current.strip():
        chunks.append(current.strip())
    return chunks

# 测试
text = "第一句话。第二句话！第三句话？第四句话。" * 50
chunks = sentence_split(text, chunk_size=100)
print(f"切分成 {len(chunks)} 块")
```

### 任务 3：用 LangChain 切分并对比效果

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

text = "你的测试文本..."

# 不同 chunk_size
small = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=20)
medium = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
large = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)

print(f"小块 (200): {len(small.split_text(text))} 个 chunk")
print(f"中块 (500): {len(medium.split_text(text))} 个 chunk")
print(f"大块 (1000): {len(large.split_text(text))} 个 chunk")
```

### 任务 4：Markdown 标题切分

```python
from langchain_text_splitters import MarkdownHeaderTextSplitter

markdown_text = """
# LangChain 入门

## 什么是 LangChain
LangChain 是一个用于构建 LLM 应用的框架。

## 核心概念
- Chains
- Agents
- Memory

# RAG 技术

## 什么是 RAG
RAG = Retrieval-Augmented Generation

## RAG 流程
1. 文档切分
2. 向量化
3. 检索
4. 生成
"""

headers_to_split_on = [
    ("#", "一级标题"),
    ("##", "二级标题"),
]

splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
chunks = splitter.split_text(markdown_text)

for i, chunk in enumerate(chunks):
    print(f"\n--- Chunk {i+1} ---")
    print(chunk)
```

---

## 6. 测验

1. **为什么不能把整篇文档直接做 Embedding？**
   答：Embedding 模型有 Token 上限，且大段文本语义模糊，检索精度差。维度固定（如 512 维），长文本会被压缩，细节丢失。

2. **RecursiveCharacterTextSplitter 的切分优先级？**
   答：段落（`\n\n`）→ 换行（`\n`）→ 句子（`。！？`）→ 逗号（`，`）→ 空格（` `）→ 字符（`""`）

3. **chunk_overlap 设置多少合适？**
   答：chunk_size 的 10%~20%。例如 chunk_size=500 → overlap=50~100

4. **什么时候该用语义切分？**
   答：高质量问答系统，对检索精度要求高，且预算允许（需要调用 Embedding 模型）

5. **LangChain 有哪些官方切分器？**
   答：CharacterTextSplitter、RecursiveCharacterTextSplitter、TokenTextSplitter、MarkdownHeaderTextSplitter、HTMLHeaderTextSplitter、SemanticChunker、SentenceTransformersTokenTextSplitter

---

## 7. 学习心得

### 今天学到了什么？
- 文本切分的概念：为什么需要切分长文本
- LangChain 官方的 7 种切分器
- 每种切分器的原理和适用场景
- 核心参数：chunk_size 和 chunk_overlap
- 重叠窗口的作用：防止切分点信息丢失

### 遇到的问题？
- Python 不熟，需要 AI 辅助写代码，但能看懂

### 参考资料
- LangChain 官方文档：https://python.langchain.com/docs/concepts/text_splitters/
- LangChain TextSplitters：https://python.langchain.com/docs/how_to/recursive_text_splitter/

---

*最后更新：2026年7月4日*
