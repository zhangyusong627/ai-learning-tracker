"""Day 32：Embedding 接入、Chroma 记录结构与 metadata 过滤。"""

import chromadb
import numpy as np
from chromadb.utils import embedding_functions


MODEL_NAME = "BAAI/bge-small-zh-v1.5"
MAX_DISTANCE = 0.4

RECORDS = [
    {
        "id": "leave-v2-001",
        "document": "员工每年享有10天带薪年假。",
        "metadata": {
            "section": "年假制度",
            "version": "V2",
            "status": "published",
            "allowed_role": "employee",
        },
    },
    {
        "id": "remote-v2-001",
        "document": "员工每周可以申请两天远程办公。",
        "metadata": {
            "section": "远程办公",
            "version": "V2",
            "status": "published",
            "allowed_role": "employee",
        },
    },
    {
        "id": "salary-v2-001",
        "document": "2026年薪酬调整方案由人力资源部审批后发布。",
        "metadata": {
            "section": "薪酬制度",
            "version": "V2",
            "status": "published",
            "allowed_role": "hr",
        },
    },
    {
        "id": "leave-v1-001",
        "document": "员工每年享有8天带薪年假。",
        "metadata": {
            "section": "年假制度",
            "version": "V1",
            "status": "archived",
            "allowed_role": "employee",
        },
    },
]


def validate_embedding_batch(
    chunks: list[str],
    vectors: list,
    expected_dimension: int,
) -> tuple[bool, str]:
    """在入库前校验批量 Embedding 结果。"""
    if len(chunks) != len(vectors):
        return False, "输入 Chunk 数量与输出向量数量不一致"

    for index, vector in enumerate(vectors):
        if len(vector) != expected_dimension:
            return (
                False,
                f"第 {index + 1} 个向量维度不一致："
                f"期望 {expected_dimension}，实际 {len(vector)}",
            )

        if not np.isfinite(vector).all():
            return False, f"第 {index + 1} 个向量包含 NaN 或 Infinity"

    return True, f"质量校验通过，共 {len(vectors)} 个向量"


# TODO：由学习者补充，只允许查询 V2、已发布、普通员工可访问的记录。
EMPLOYEE_FILTER = {
    "$and": [
        {"version": {"$eq": "V2"}},
        {"status": {"$eq": "published"}},
        {"allowed_role": {"$eq": "employee"}},
    ]
}

HR_FILTER = {
    "$and": [
        {"version": {"$eq": "V2"}},
        {"status": {"$eq": "published"}},
        {"allowed_role": {"$eq": "hr"}},
    ]
}

TEST_CASES = [
    {
        "name": "普通员工查询有权限的年假制度",
        "question": "员工一年可以休多少天年假？",
        "where": EMPLOYEE_FILTER,
    },
    {
        "name": "普通员工查询无权限的薪酬制度",
        "question": "2026年的薪酬调整规则是什么？",
        "where": EMPLOYEE_FILTER,
    },
    {
        "name": "HR 查询有权限的薪酬制度",
        "question": "2026年的薪酬调整规则是什么？",
        "where": HR_FILTER,
    },
]


def build_collection():
    embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=MODEL_NAME,
        normalize_embeddings=True,
    )
    client = chromadb.Client()
    collection = client.create_collection(
        name="day32_vector_retrieval",
        embedding_function=embedding_function,
        metadata={"hnsw:space": "cosine"},
    )

    documents = [record["document"] for record in RECORDS]
    vectors = embedding_function(documents)
    is_valid, validation_message = validate_embedding_batch(
        chunks=documents,
        vectors=vectors,
        expected_dimension=512,
    )
    if not is_valid:
        raise ValueError(validation_message)

    collection.add(
        ids=[record["id"] for record in RECORDS],
        documents=documents,
        embeddings=vectors,
        metadatas=[record["metadata"] for record in RECORDS],
    )
    return collection, embedding_function, validation_message


def search(collection, question: str, where: dict) -> list[dict]:
    result = collection.query(
        query_texts=[question],
        n_results=3,
        where=where,
        include=["documents", "metadatas", "distances"],
    )
    return [
        {
            "id": record_id,
            "document": document,
            "metadata": metadata,
            "distance": distance,
        }
        for record_id, document, metadata, distance in zip(
            result["ids"][0],
            result["documents"][0],
            result["metadatas"][0],
            result["distances"][0],
        )
    ]


def main() -> None:
    collection, embedding_function, validation_message = build_collection()

    document_vector = embedding_function([RECORDS[0]["document"]])[0]
    question_vector = embedding_function([TEST_CASES[0]["question"]])[0]
    print(f"Embedding 模型：{MODEL_NAME}")
    print(f"文档向量维度：{len(document_vector)}")
    print(f"问题向量维度：{len(question_vector)}")
    print(f"文档向量长度：{np.linalg.norm(document_vector):.6f}")
    print(f"问题向量长度：{np.linalg.norm(question_vector):.6f}")
    print(f"入库前校验：{validation_message}")

    for test_case in TEST_CASES:
        candidates = search(
            collection,
            question=test_case["question"],
            where=test_case["where"],
        )
        accepted = [
            candidate
            for candidate in candidates
            if candidate["distance"] <= MAX_DISTANCE
        ]

        print("\n" + "=" * 70)
        print(f"场景：{test_case['name']}")
        print(f"问题：{test_case['question']}")
        print("metadata 过滤后的候选：")
        for candidate in candidates:
            print(candidate)

        print(f"最终阈值：distance <= {MAX_DISTANCE}")
        if not accepted:
            print("决策：拒绝回答，没有足够相关且有权限的证据。")
            continue

        print("决策：允许回答")
        for candidate in accepted:
            print(candidate)


if __name__ == "__main__":
    main()
