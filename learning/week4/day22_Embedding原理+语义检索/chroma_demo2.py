import chromadb
from chromadb.utils import embedding_functions

# 使用 BGE 模型（和昨天一样）
ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="BAAI/bge-small-zh-v1.5"
)

# 创建客户端
client = chromadb.Client()

# 创建集合时指定 embedding 函数
collection = client.create_collection(
    name="my_notes",
    embedding_function=ef  # 关键！
)

# 添加数据
collection.add(
    documents=[
        "Python 是一种编程语言",
        "JavaScript 用于网页开发",
        "机器学习需要数学基础",
        "今天天气不错"
    ],
    ids=["note1", "note2", "note3", "note4"]
)

# 搜索
results = collection.query(
    query_texts=["编程"],
    n_results=2
)

print("搜索结果：")
for i, doc in enumerate(results['documents'][0]):
    print(f"{i+1}. {doc}")