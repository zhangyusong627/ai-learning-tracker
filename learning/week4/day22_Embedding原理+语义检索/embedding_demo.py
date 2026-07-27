from sentence_transformers import SentenceTransformer
import numpy as np

# 加载中文 Embedding 模型
model = SentenceTransformer('BAAI/bge-small-zh-v1.5')

# 测试三段文字
texts = ["苹果手机", "iPhone", "今天天气不错"]

# 生成向量
vectors = model.encode(texts)

# 打印结果
for i, text in enumerate(texts):
    print(f"\n文本: {text}")
    print(f"向量维度: {len(vectors[i])}")
    print(f"前5个数字: {vectors[i][:5].round(3)}")

# 计算相似度
def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

print("\n" + "=" * 40)
print("相似度对比：")
print("=" * 40)

# "苹果手机" vs "iPhone"
sim1 = cosine_similarity(vectors[0], vectors[1])
print(f"\n苹果手机 vs iPhone: {sim1:.4f}")

# "苹果手机" vs "今天天气"
sim2 = cosine_similarity(vectors[0], vectors[2])
print(f"苹果手机 vs 今天天气: {sim2:.4f}")

print("\n" + "=" * 40)
print(f"结论：{sim1:.4f} > {sim2:.4f}")
print("所以「苹果手机」和「iPhone」更相似！")
print("=" * 40)