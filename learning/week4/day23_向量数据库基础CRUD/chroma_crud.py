import chromadb
from chromadb.utils import embedding_functions

#创建客户端
client = chromadb.Client()

#指定embedding模型
embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="BAAI/bge-small-zh-v1.5")

#创建集合
collection = client.create_collection(name="my_documents", embedding_function=embedding_function)

#添加数据
collection.add(
    documents=["Python是一种编程语言", "JavaScript主要用于网页开发", "机器学习需要数学基础"],
    ids=["doc1", "doc2", "doc3"]
)

#查询数据
results = collection.query(
    query_texts=["编程"],
    n_results=2
)

print(results)

#更新数据
collection.update(
    ids=["doc1"],
    documents=["Python是一种解释型编程语言"],
)

results = collection.get(ids=["doc1"])

print(results["documents"])

# 删除前：看看有几条数据
print(f"删除前：{collection.count()} 条数据")

# 删除数据
collection.delete(ids=["doc2"])

# 删除后：看看剩几条
print(f"删除后：{collection.count()} 条数据")

# 验证
results = collection.get()
print(f"剩余数据：{results['documents']}")