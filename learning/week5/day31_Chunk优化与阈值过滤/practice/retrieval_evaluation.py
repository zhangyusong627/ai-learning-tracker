"""Day 31：使用标注评测集比较不同距离阈值。"""

import chromadb
from chromadb.utils import embedding_functions

from chunk_comparison import POLICY_TEXT, split_by_section


EVALUATION_CASES = [
    {
        "question": "员工每年有多少天年假？",
        "expected_section": "年假制度",
    },
    {
        "question": "超过5000元的报销由谁审批？",
        "expected_section": "报销制度",
    },
    {
        "question": "员工每周可以远程办公几天？",
        "expected_section": "远程办公",
    },
    {
        "question": "公司是否提供住房补贴？",
        "expected_section": None,
    },
]

MAX_DISTANCE_CANDIDATES = [0.3, 0.4, 0.5, 0.6]
TOP_K_CANDIDATES = [1, 2, 3]


def build_collection() -> chromadb.Collection:
    embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="BAAI/bge-small-zh-v1.5"
    )
    client = chromadb.Client()
    collection = client.create_collection(
        name="day31_structure_evaluation",
        embedding_function=embedding_function,
    )

    chunks = split_by_section(POLICY_TEXT)
    collection.add(
        ids=[f"section-{index}" for index in range(len(chunks))],
        documents=chunks,
        metadatas=[{"section": chunk.splitlines()[0]} for chunk in chunks],
    )
    return collection


def retrieve(
    collection: chromadb.Collection,
    question: str,
    top_k: int,
) -> list[dict]:
    result = collection.query(
        query_texts=[question],
        n_results=min(top_k, collection.count()),
        include=["documents", "distances", "metadatas"],
    )
    return [
        {
            "content": content,
            "distance": distance,
            "section": metadata["section"],
        }
        for content, distance, metadata in zip(
            result["documents"][0],
            result["distances"][0],
            result["metadatas"][0],
        )
    ]


def evaluate(
    collection: chromadb.Collection,
    top_k: int,
    max_distance: float,
) -> None:
    answer_case_count = 0
    candidate_hit_count = 0
    answer_hit_count = 0
    no_answer_case_count = 0
    no_answer_rejection_count = 0
    accepted_count = 0
    relevant_accepted_count = 0

    print("=" * 72)
    print(f"生产配置：Top K = {top_k}，distance <= {max_distance}")

    for case in EVALUATION_CASES:
        results = retrieve(collection, case["question"], top_k)
        accepted = [
            result for result in results if result["distance"] <= max_distance
        ]
        expected_section = case["expected_section"]

        if expected_section is None:
            no_answer_case_count += 1
            passed = not accepted
            if passed:
                no_answer_rejection_count += 1
        else:
            answer_case_count += 1
            candidate_hit = any(
                result["section"] == expected_section for result in results
            )
            if candidate_hit:
                candidate_hit_count += 1
            passed = any(
                result["section"] == expected_section for result in accepted
            )
            if passed:
                answer_hit_count += 1

        for result in accepted:
            accepted_count += 1
            if expected_section is not None and result["section"] == expected_section:
                relevant_accepted_count += 1

        closest = results[0]
        accepted_sections = [result["section"] for result in accepted]
        print(
            f"{'通过' if passed else '失败'} | {case['question']}\n"
            f"  预期章节：{expected_section or '无答案'}\n"
            f"  最相近：{closest['section']} ({closest['distance']:.4f})\n"
            f"  通过阈值：{accepted_sections or '无'}"
        )

    candidate_hit_rate = candidate_hit_count / answer_case_count
    accepted_evidence_hit_rate = answer_hit_count / answer_case_count
    rejection_rate = no_answer_rejection_count / no_answer_case_count
    precision = (
        relevant_accepted_count / accepted_count if accepted_count else 0.0
    )

    print("评测汇总：")
    print(f"  候选阶段命中率：{candidate_hit_rate:.2%}")
    print(f"  证据准入阶段命中率：{accepted_evidence_hit_rate:.2%}")
    print(f"  查准率：{precision:.2%}")
    print(f"  无答案拒答率：{rejection_rate:.2%}")


def main() -> None:
    collection = build_collection()
    for top_k in TOP_K_CANDIDATES:
        for max_distance in MAX_DISTANCE_CANDIDATES:
            evaluate(collection, top_k, max_distance)


if __name__ == "__main__":
    main()
