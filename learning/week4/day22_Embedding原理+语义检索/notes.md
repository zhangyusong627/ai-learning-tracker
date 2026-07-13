# Day 22: Embedding原理+语义检索

## 学习目标
- 理解 Embedding 概念：文字 → 向量
- 掌握余弦相似度：计算向量相似程度
- 使用 BGE 模型生成向量
- 实现简单的语义搜索

## 学习时间
2026年6月22日

---

## 1. 今天要做什么？

### Embedding 基础
- 理解为什么需要 Embedding
- 学习向量和相似度的概念
- 用代码生成和计算向量

### 实践任务
- 使用 BGE 模型生成中文向量
- 计算不同文本的相似度
- 实现简单的语义搜索

---

## 2. 核心概念

### 2.1 Embedding 是什么？

```
文字 → Embedding 模型 → 向量（一组数字）

"苹果手机" → [0.2, 0.8, -0.1, ...]
"iPhone"   → [0.2, 0.7, -0.1, ...]  ← 很接近！
"今天天气" → [-0.3, 0.1, 0.9, ...]  ← 差很远
```

**核心特点**：
- 语义相似的文字 → 向量相近
- 语义不同的文字 → 向量差很远

### 2.2 余弦相似度

```
cos(A, B) = (A·B) / (|A| × |B|)

范围：[-1, 1]
├── 接近 1 → 很相似
├── 接近 0 → 无关
└── 接近 -1 → 完全相反
```

### 2.3 BGE 模型

```
BAAI/bge-small-zh-v1.5
├── 中文优化
├── 开源免费
├── 本地运行
└── 向量维度：512
```

---

## 3. 代码示例

### 3.1 安装依赖

```bash
pip install sentence-transformers numpy
```

### 3.2 生成向量

```python
from sentence_transformers import SentenceTransformer
import numpy as np

# 加载模型
model = SentenceTransformer('BAAI/bge-small-zh-v1.5')

# 生成向量
texts = ["苹果手机", "iPhone", "今天天气不错"]
vectors = model.encode(texts)

# 查看结果
for i, text in enumerate(texts):
    print(f"文本: {text}")
    print(f"向量维度: {len(vectors[i])}")
    print(f"前5个数字: {vectors[i][:5].round(3)}")
    print()
```

### 3.3 计算相似度

```python
def cosine_similarity(a, b):
    """计算余弦相似度"""
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# 计算相似度
sim1 = cosine_similarity(vectors[0], vectors[1])  # 苹果手机 vs iPhone
sim2 = cosine_similarity(vectors[0], vectors[2])  # 苹果手机 vs 今天天气

print(f"苹果手机 vs iPhone: {sim1:.4f}")
print(f"苹果手机 vs 今天天气: {sim2:.4f}")
```

### 3.4 语义搜索

```python
def semantic_search(query, documents, top_k=3):
    """语义搜索"""
    # 生成向量
    query_vector = model.encode([query])[0]
    doc_vectors = model.encode(documents)

    # 计算相似度
    similarities = []
    for i, doc_vector in enumerate(doc_vectors):
        sim = cosine_similarity(query_vector, doc_vector)
        similarities.append((documents[i], sim))

    # 排序
    similarities.sort(key=lambda x: x[1], reverse=True)
    return similarities[:top_k]

# 测试
documents = [
    "iPhone 15 是苹果公司的最新手机",
    "华为 Mate 60 支持卫星通信",
    "今天北京天气晴朗",
    "明天可能有雨"
]

results = semantic_search("苹果手机", documents)
for doc, sim in results:
    print(f"[{sim:.4f}] {doc}")
```

---

## 4. 实操任务

### 任务 1：生成向量（15分钟）

```python
# 补全这段代码
texts = [
    "Python 是编程语言",
    "JavaScript 用于网页开发",
    "机器学习需要数学基础",
    # TODO: 再添加 3 个文本
]

# TODO: 用 BGE 模型生成向量
# TODO: 打印每个文本的向量维度和前5个数字
```

### 任务 2：计算相似度（15分钟）

```python
# 补全这段代码
def cosine_similarity(a, b):
    # TODO: 实现余弦相似度计算
    pass

# TODO: 计算 "Python" 和 "编程语言" 的相似度
# TODO: 计算 "Python" 和 "天气" 的相似度
# TODO: 打印结果，验证哪个更相似
```

### 任务 3：语义搜索（30分钟）

```python
# 实现一个简单的语义搜索
products = [
    "iPhone 15 Pro，苹果最新旗舰手机",
    "AirPods Pro，苹果无线降噪耳机",
    "小米电视 65 寸，4K 智能电视",
    "华为 Mate 60，支持卫星通信",
    # TODO: 再添加 5 个商品
]

def search_product(query, products, top_k=3):
    # TODO: 实现搜索功能
    pass

# 测试：搜索 "手机"
# 测试：搜索 "耳机"
```

---

## 5. 测验

1. **Embedding 是什么？**（用自己的话解释）

2. **余弦相似度的范围是多少？** 各代表什么含义？

3. **为什么"苹果手机"和"iPhone"的向量会相近？**

4. **BGE 模型的向量维度是多少？**

---

## 6. 学习心得

### 今天学到了什么？
- Embedding：文字 → 向量，语义相近 → 向量相近
- 余弦相似度：计算向量相似程度，范围 [-1, 1]
- Chroma 向量数据库：支持语义搜索
- 必须显式指定 Embedding 模型（如 BGE），否则语义搜索失效

### 遇到的问题？
- Python 代码需要借助 AI 工具，自己不会写
- Chroma 运行原理和完整功能不清楚

### 明天要学什么？
- 向量数据库的基础 CRUD

---

*最后更新：2026年6月30日*
