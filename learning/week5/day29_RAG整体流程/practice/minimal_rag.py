"""Day 29：显式展示 RAG 的索引、检索、Prompt 和生成数据流。"""

import os
from pathlib import Path

import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_deepseek import ChatDeepSeek


WEEK_DIR = Path(__file__).resolve().parents[2]
load_dotenv(WEEK_DIR / ".env")


KNOWLEDGE_CHUNKS = [
    {
        "id": "policy-annual-leave",
        "content": "员工每年享有10天带薪年假。",
        "metadata": {"source": "employee_policy.md", "section": "年假制度"},
    },
    {
        "id": "policy-reimbursement",
        "content": "单笔报销超过5000元需要部门负责人审批。",
        "metadata": {"source": "finance_policy.md", "section": "报销审批"},
    },
    {
        "id": "policy-remote-work",
        "content": "员工每周可以申请两天远程办公。",
        "metadata": {"source": "employee_policy.md", "section": "远程办公"},
    },
]


def build_vector_store() -> chromadb.Collection:
    """离线索引：Chunk → Embedding → 向量数据库。"""
    embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="BAAI/bge-small-zh-v1.5"
    )
    client = chromadb.Client()
    collection = client.create_collection(
        name="day29_company_policies",
        embedding_function=embedding_function,
    )
    collection.add(
        ids=[chunk["id"] for chunk in KNOWLEDGE_CHUNKS],
        documents=[chunk["content"] for chunk in KNOWLEDGE_CHUNKS],
        metadatas=[chunk["metadata"] for chunk in KNOWLEDGE_CHUNKS],
    )
    return collection


def retrieve(collection: chromadb.Collection, question: str, top_k: int = 2) -> list[dict]:
    """在线检索：问题 → 问题向量 → Top K Chunk。"""
    result = collection.query(
        query_texts=[question],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    return [
        {
            "content": content,
            "metadata": metadata,
            "distance": distance,
        }
        for content, metadata, distance in zip(
            result["documents"][0],
            result["metadatas"][0],
            result["distances"][0],
        )
    ]


def build_context(retrieved_chunks: list[dict]) -> str:
    """把检索结果转换为带来源编号的上下文。"""
    context_parts = []
    for index, chunk in enumerate(retrieved_chunks, start=1):
        metadata = chunk["metadata"]
        context_parts.append(
            f"[{index}] {chunk['content']}\n"
            f"来源：{metadata['source']}，章节：{metadata['section']}"
        )
    return "\n\n".join(context_parts)


def generate_answer(question: str, context: str) -> str:
    """生成阶段：问题 + 证据 → LLM 答案。"""
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        raise RuntimeError("缺少 DEEPSEEK_API_KEY，请在 learning/week5/.env 中配置。")

    llm = ChatDeepSeek(
        model=os.environ.get("DEEPSEEK_MODEL", "deepseek-chat"),
        api_key=api_key,
        temperature=0,
    )
    response = llm.invoke(
        [
            SystemMessage(
                content=(
                    "你是企业制度问答助手。只能根据提供的资料回答；"
                    "资料不足时明确回答无法确定；答案末尾标注引用编号。"
                )
            ),
            HumanMessage(content=f"资料：\n{context}\n\n问题：{question}"),
        ]
    )
    return response.content


def main() -> None:
    question = "员工一年可以休多少天年假？"

    print("\n=== 1. 离线索引 ===")
    collection = build_vector_store()
    print(f"已索引 Chunk 数量：{collection.count()}")

    print("\n=== 2. 在线检索 ===")
    print(f"用户问题：{question}")
    retrieved_chunks = retrieve(collection, question)
    for index, chunk in enumerate(retrieved_chunks, start=1):
        print(f"Top {index}: {chunk['content']}")
        print(f"metadata: {chunk['metadata']}")
        print(f"distance: {chunk['distance']:.4f}")

    print("\n=== 3. Prompt 上下文 ===")
    context = build_context(retrieved_chunks)
    print(context)

    print("\n=== 4. LLM 生成 ===")
    answer = generate_answer(question, context)
    print(answer)


if __name__ == "__main__":
    main()
