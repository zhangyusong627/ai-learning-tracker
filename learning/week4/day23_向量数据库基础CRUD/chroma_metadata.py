import chromadb
from chromadb.utils import embedding_functions

#创建客户端
client = chromadb.Client()

#指定embedding模型
embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="BAAI/bge-small-zh-v1.5")

#创建集合
collection = client.create_collection(name="my_documents", embedding_function=embedding_function)


# 添加带元数据的数据
collection.add(
    documents=[
        "Python是一种编程语言",
        "JavaScript主要用于网页开发",
        "机器学习需要数学基础"
    ],
    ids=["doc1", "doc2", "doc3"],
    metadatas=[
        {"category": "编程", "creator": "张三", "created_at": "2026-07-01"},
        {"category": "编程", "creator": "张三", "created_at": "2026-07-01"},
        {"category": "AI", "creator": "李四", "created_at": "2026-07-02"}
    ]
)

print(f"添加了 {collection.count()} 条数据")


# 使用元数据筛选
results = collection.query(
    query_texts=["编程"],           # 语义搜索
    where={"category": "编程"},     # 元数据筛选
    n_results=2
)

print("搜索结果：")
for doc, metadata in zip(results['documents'][0], results['metadatas'][0]):
    print(f"- {doc}")
    print(f"  分类: {metadata['category']}, 创建者: {metadata['creator']}")