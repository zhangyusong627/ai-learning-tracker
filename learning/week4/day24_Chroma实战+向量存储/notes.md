# Day 24: Chroma实战+向量存储

## 学习目标
- 掌握 Chroma 集成 Embedding 模型
- 实现文本 → 向量 → 入库流程
- 实现语义检索实战
- 掌握持久化存储

## 学习时间
2026年7月4日

---

## 1. 今天要做什么？

### 持久化存储
- 数据保存到磁盘，不会丢失
- 下次运行自动加载

### 完整系统
- 把 Embedding 和 Chroma 结合起来
- 实现一个完整的语义搜索系统

---

## 2. 核心概念

### 2.1 持久化存储

```
之前（内存模式）：
client = chromadb.Client()
└── 数据只存在内存，关机就没了

现在（持久化模式）：
client = chromadb.PersistentClient(path="./my_notes_db")
└── 数据保存到磁盘，下次运行自动加载
```

### 2.2 获取集合

```python
# 获取已存在的集合（不存在会报错）
collection = client.get_collection("notes", embedding_function=ef)

# 获取或创建（推荐）
collection = client.get_or_create_collection("notes", embedding_function=ef)
```

**类比 MySQL**：
```
MySQL: SELECT * FROM notes
Chroma: client.get_collection("notes")
```

### 2.3 embedding_function 的作用

```python
collection = client.get_collection("notes", embedding_function=ef)
```

告诉 Chroma：
- 用什么模型生成向量
- 查询时用同一个模型
- 这样搜索结果才正确

---

## 3. 代码示例

### 3.1 完整的语义搜索系统

```python
import chromadb
from chromadb.utils import embedding_functions
from sentence_transformers import SentenceTransformer

# 1. 初始化
model = SentenceTransformer('BAAI/bge-small-zh-v1.5')
ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="BAAI/bge-small-zh-v1.5"
)

# 2. 创建持久化客户端
client = chromadb.PersistentClient(path="./my_notes_db")

# 3. 获取或创建集合
collection = client.get_or_create_collection(
    name="notes",
    embedding_function=ef
)

# 4. 添加数据
notes = [
    "Python 是一种解释型编程语言",
    "JavaScript 主要用于网页开发",
    "机器学习需要数学基础"
]

collection.add(
    documents=notes,
    ids=[f"note_{i}" for i in range(len(notes))],
    metadatas=[
        {"category": "编程"},
        {"category": "编程"},
        {"category": "AI"}
    ]
)

# 5. 查询
results = collection.query(
    query_texts=["编程语言"],
    n_results=2
)

print(results['documents'][0])
```

### 3.2 直接查询已有数据

```python
# 不需要重新添加数据，直接查询
client = chromadb.PersistentClient(path="./my_notes_db")
collection = client.get_collection("notes", embedding_function=ef)

results = collection.query(
    query_texts=["Python"],
    n_results=2
)

for doc, meta in zip(results['documents'][0], results['metadatas'][0]):
    print(f"[{meta['category']}] {doc}")
```

---

## 4. 实操任务

### 任务 1：创建持久化笔记库（20分钟）

```python
# 创建一个笔记库，添加 10 条笔记
# 包含元数据（category, created_at）
# 使用持久化存储
```

### 任务 2：语义搜索（20分钟）

```python
# 实现搜索功能
# 支持语义搜索 + 元数据筛选
```

### 任务 3：验证持久化（10分钟）

```python
# 运行代码添加数据
# 关闭程序
# 重新运行，验证数据是否还在
```

---

## 5. 测验

1. **什么时候需要持久化存储？**
   答：需要保存数据供后续查询时

2. **get_collection 和 get_or_create_collection 有什么区别？**
   答：get_collection 获取已存在的集合，不存在会报错；get_or_create_collection 获取或创建，不存在会自动创建

3. **embedding_function 的作用是什么？**
   答：告诉 Chroma 用什么模型生成向量，查询时用同一个模型

---

## 6. 学习心得

### 今天学到了什么？
- 持久化存储：数据保存到磁盘，不会丢失
- 获取集合：get_collection / get_or_create_collection
- embedding_function：指定 Embedding 模型
- 完整系统：Embedding + Chroma 结合，语义搜索 + 元数据筛选

### 遇到的问题？
- Python 不熟，需要 AI 辅助，但能看懂

### 明天要学什么？
- 模型微调入门

---

*最后更新：2026年7月4日*
