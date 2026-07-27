from sentence_transformers import SentenceTransformer
import numpy as np

# 加载模型
model = SentenceTransformer('BAAI/bge-small-zh-v1.5')

# 你的文本
texts = [
    "Python 是编程语言",
    "JavaScript 用于网页开发",
    "机器学习需要数学基础",
    # TODO: 再添加 3 个你感兴趣的文本
    "上海今天下暴雨了",
    "Java 适合开发后端",
    "明天是女儿玥玥 4 岁的生日"
]

# TODO: 用 BGE 模型生成向量
vectors = model.encode(texts)

# TODO: 打印每个文本的向量维度和前5个数字
for i, text in enumerate(texts):
    print(f"\n文本: {text}")
    print(f"向量维度: {len(vectors[i])}")
    print(f"前5个数字: {vectors[i][:5].round(3)}")


# 计算相似度
def cosine_similarity(a, b):
    """计算余弦相似度"""
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# 计算相似度矩阵
print("=" * 60)
print("相似度对比：")
print("=" * 60)

# 两两对比
for i in range(len(texts)):
    for j in range(i+1, len(texts)):
        sim = cosine_similarity(vectors[i], vectors[j])
        print(f"\n{texts[i]}")
        print(f"  vs {texts[j]}")
        print(f"  相似度: {sim:.4f}")

print("\n" + "=" * 60)