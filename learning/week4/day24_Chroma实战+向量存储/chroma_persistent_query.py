# 直接查询，不需要重新添加数据
import chromadb
from chromadb.utils import embedding_functions

# 初始化
ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="BAAI/bge-small-zh-v1.5"
)

# 加载已有数据（自动读取 my_notes_db）
client = chromadb.PersistentClient(path="./my_notes_db")
collection = client.get_collection("notes", embedding_function=ef)

# 直接查询
results = collection.query(
    query_texts=["AI"],
    n_results=3
)

print("查询结果：")
for doc, meta, dist in zip(
    results['documents'][0],
    results['metadatas'][0],
    results['distances'][0]
):
    print(f"[{meta['category']}] {doc}")
    print(f"  相似度：{1-dist:.4f}")