from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer('BAAI/bge-small-zh-v1.5')

# 商品库
products = [
    "iPhone 15 Pro，苹果最新旗舰手机",
    "AirPods Pro，苹果无线降噪耳机",
    "小米电视 65 寸，4K 智能电视",
    "华为 Mate 60，支持卫星通信",
    "MacBook Pro，苹果笔记本电脑",
    "小米 14，骁龙 8 Gen 3 处理器",
    "华为耳机 FreeBuds Pro 2",
    "索尼 WH-1000XM5 降噪耳机",
    "iPad Pro，苹果平板电脑"
]

# 生成所有商品的向量
product_vectors = model.encode(products)

def search_product(query, products, product_vectors, top_k=3):
    """根据查询搜索商品"""
    # 生成查询向量
    query_vector = model.encode([query])[0]

    # 计算相似度
    similarities = []
    for i, product_vector in enumerate(product_vectors):
        sim = cosine_similarity(query_vector, product_vector)
        similarities.append((products[i], sim))

    # 按相似度排序
    similarities.sort(key=lambda x: x[1], reverse=True)

    return similarities[:top_k]

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# 测试搜索
print("=" * 50)
print("搜索 '手机'：")
print("=" * 50)
results = search_product("手机", products, product_vectors)
for product, sim in results:
    print(f"[{sim:.4f}] {product}")

print("\n" + "=" * 50)
print("搜索 '耳机'：")
print("=" * 50)
results = search_product("耳机", products, product_vectors)
for product, sim in results:
    print(f"[{sim:.4f}] {product}")

print("\n" + "=" * 50)
print("搜索 '苹果电脑'：")
print("=" * 50)
results = search_product("苹果电脑", products, product_vectors)
for product, sim in results:
    print(f"[{sim:.4f}] {product}")