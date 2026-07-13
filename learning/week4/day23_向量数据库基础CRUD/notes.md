# Day 23: 向量数据库基础CRUD

## 学习目标
- 理解为什么需要向量数据库
- 学习 Chroma 基础操作
- 掌握 CRUD：创建、读取、更新、删除
- 实现向量存储和检索

## 学习时间
2026年6月23日

---

## 1. 今天要做什么？

### 为什么需要向量数据库？
- 普通数据库：按关键词搜索
- 向量数据库：按语义搜索

### Chroma 基础
- 安装和配置
- 创建集合（Collection）
- 添加、查询、更新、删除向量

---

## 2. 核心概念

### 2.1 向量数据库 vs 普通数据库

```
普通数据库（MySQL）：
├── 存储：结构化数据（表格）
├── 搜索：精确匹配（WHERE name = 'iPhone'）
└── 问题：无法理解语义

向量数据库（Chroma）：
├── 存储：向量 + 元数据
├── 搜索：语义相似（找到最相关的向量）
└── 优势：理解文字意思
```

### 2.2 Chroma 核心概念

```
Collection（集合）
├── 存放向量的容器
├── 类似 MySQL 的表
└── 每个 Collection 有独立的向量

Document（文档）
├── 原始文本
└── 例如："iPhone 15 是苹果手机"

Embedding（向量）
├── 文本的向量表示
└── 例如：[0.2, 0.8, -0.1, ...]

Metadata（元数据）
├── 附加信息
└── 例如：{"category": "手机", "price": 7999}
```

---

## 3. 代码示例

### 3.1 安装 Chroma

```bash
pip install chromadb
```

### 3.2 创建集合

```python
import chromadb
from sentence_transformers import SentenceTransformer

# 初始化
model = SentenceTransformer('BAAI/bge-small-zh-v1.5')
client = chromadb.Client()  # 内存模式

# 创建集合
collection = client.create_collection(
    name="my_documents",
    metadata={"hnsw:space": "cosine"}  # 使用余弦相似度
)

print(f"集合创建成功: {collection.name}")
```

### 3.3 添加文档（Create）

```python
# 添加文档
collection.add(
    documents=[
        "iPhone 15 是苹果公司的最新手机",
        "华为 Mate 60 支持卫星通信",
        "小米 14 搭载骁龙 8 Gen 3"
    ],
    ids=["doc1", "doc2", "doc3"],
    metadatas=[
        {"category": "手机", "brand": "苹果"},
        {"category": "手机", "brand": "华为"},
        {"category": "手机", "brand": "小米"}
    ]
)

print(f"添加了 {collection.count()} 个文档")
```

### 3.4 查询文档（Read）

```python
# 查询最相关的文档
results = collection.query(
    query_texts=["苹果手机"],  # 查询文本
    n_results=2  # 返回 2 个结果
)

print("查询结果：")
for i, doc in enumerate(results['documents'][0]):
    print(f"{i+1}. {doc}")
    print(f"   距离: {results['distances'][0][i]:.4f}")
```

### 3.5 更新文档（Update）

```python
# 更新文档
collection.update(
    ids=["doc1"],
    documents=["iPhone 15 Pro Max 是苹果最贵的手机"],
    metadatas=[{"category": "手机", "brand": "苹果", "updated": True}]
)

print("更新成功")
```

### 3.6 删除文档（Delete）

```python
# 删除文档
collection.delete(ids=["doc3"])

print(f"删除后剩余: {collection.count()} 个文档")
```

---

## 4. 实操任务

### 任务 1：创建知识库（20分钟）

```python
# 创建一个知识库，存储以下内容
knowledge = [
    "Python 是一种解释型编程语言",
    "JavaScript 主要用于网页开发",
    "机器学习需要数学基础",
    # TODO: 再添加 5 个知识点
]

# TODO: 创建 Chroma 集合
# TODO: 添加所有知识点
# TODO: 打印集合中的文档数量
```

### 任务 2：语义搜索（20分钟）

```python
# 实现搜索功能
def search_knowledge(query, collection, top_k=3):
    # TODO: 查询最相关的知识点
    # TODO: 返回结果
    pass

# 测试搜索
print("搜索 '编程语言'：")
# TODO: 调用 search_knowledge

print("\n搜索 'AI 相关'：")
# TODO: 调用 search_knowledge
```

### 任务 3：CRUD 操作（20分钟）

```python
# 完成以下操作
# 1. 添加一个新文档
# 2. 查询这个文档
# 3. 更新这个文档
# 4. 删除这个文档
# 每一步都打印结果，验证操作是否成功
```

---

## 5. 测验

1. **为什么需要向量数据库？** 普通数据库有什么问题？

2. **Chroma 的 Collection 是什么？** 类似 MySQL 的什么概念？

3. **CRUD 分别代表什么？**

4. **Chroma 默认使用什么相似度算法？**

---

## 6. 学习心得

### 今天学到了什么？
- Chroma CRUD：增删改查（add/get/update/delete）
- 元数据：添加附加信息（创建时间、创建者、来源、类别）
- 混合查询：语义搜索 + 元数据筛选

### 遇到的问题？
- Python 不熟，需要 AI 工具辅助写代码，但基本上能看懂

### 明天要学什么？
- Chroma 实战 + 向量存储

---

*最后更新：2026年6月30日*
