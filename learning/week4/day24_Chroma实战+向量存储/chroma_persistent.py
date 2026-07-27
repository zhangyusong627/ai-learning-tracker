import chromadb
from chromadb.utils import embedding_functions
from sentence_transformers import SentenceTransformer

# 1. 初始化
print("正在初始化...")
model = SentenceTransformer('BAAI/bge-small-zh-v1.5')
ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="BAAI/bge-small-zh-v1.5"
)

# 2. 创建持久化客户端
client = chromadb.PersistentClient(path="./my_notes_db")

# 3. 创建集合（如果已存在，会自动加载）
collection = client.get_or_create_collection(
    name="notes",
    embedding_function=ef
)

# 4. 添加笔记数据
notes = [
    "Python 是一种解释型编程语言，语法简洁易学",
    "JavaScript 主要用于网页开发，可以实现动态效果",
    "机器学习需要数学基础，包括线性代数和概率论",
    "深度学习是机器学习的子集，使用神经网络",
    "FastAPI 是一个现代的 Python Web 框架，性能很高",
    "LangChain 是一个用于构建 LLM 应用的框架",
    "向量数据库用于存储和检索向量，支持语义搜索",
    "Embedding 把文字变成向量，保留语义关系"
]

# 添加元数据
metadatas = [
    {"category": "编程", "difficulty": "入门"},
    {"category": "编程", "difficulty": "入门"},
    {"category": "AI", "difficulty": "进阶"},
    {"category": "AI", "difficulty": "进阶"},
    {"category": "框架", "difficulty": "入门"},
    {"category": "框架", "difficulty": "进阶"},
    {"category": "数据库", "difficulty": "进阶"},
    {"category": "AI", "difficulty": "入门"}
]

# 清空旧数据（可选）
try:
    collection.delete(where={})
except:
    pass

# 添加数据
collection.add(
    documents=notes,
    ids=[f"note_{i}" for i in range(len(notes))],
    metadatas=metadatas
)

print(f"已添加 {collection.count()} 条笔记")

# 5. 搜索函数
def search(query, category=None, top_k=3):
    """语义搜索笔记"""
    where = {"category": category} if category else None

    results = collection.query(
        query_texts=[query],
        where=where,
        n_results=top_k
    )

    print(f"\n搜索：{query}" + (f"（分类：{category}）" if category else ""))
    print("-" * 50)

    for i, (doc, meta, dist) in enumerate(zip(
        results['documents'][0],
        results['metadatas'][0],
        results['distances'][0]
    )):
        print(f"{i+1}. [{meta['category']}] {doc}")
        print(f"   相似度：{1-dist:.4f}")

# 6. 测试搜索
search("什么是编程语言")
search("AI 相关知识")
search("框架", category="框架")
search("入门级别的内容", category="入门")