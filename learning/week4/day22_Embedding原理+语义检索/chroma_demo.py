import chromadb

# 1. 创建客户端（内存模式）
client = chromadb.Client()

# 2. 创建集合（类似 MySQL 的表）
collection = client.create_collection("my_notes")

# 3. 添加数据
collection.add(
    documents=[
        "Python 是一种编程语言",
        "JavaScript 用于网页开发",
        "机器学习需要数学基础",
        "今天天气不错"
    ],
    ids=["note1", "note2", "note3", "note4"]
)

print(f"添加了 {collection.count()} 条数据")

# 4. 搜索
results = collection.query(
    query_texts=["编程"],  # 搜索"编程"
    n_results=2           # 返回 2 个结果
)

print("\n搜索结果：")
for i, doc in enumerate(results['documents'][0]):
    print(f"{i+1}. {doc}")