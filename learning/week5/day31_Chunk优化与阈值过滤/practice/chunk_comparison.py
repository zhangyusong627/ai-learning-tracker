"""Day 31：比较 Chunk 参数对检索结果的影响。"""

import chromadb
from chromadb.utils import embedding_functions
from langchain_text_splitters import RecursiveCharacterTextSplitter


POLICY_TEXT = """员工制度

年假制度
员工每年享有10天带薪年假。年假需要提前3个工作日提交申请。

报销制度
单笔报销超过5000元，需要部门负责人审批。审批通过后由财务部门付款。

远程办公
员工每周可以申请两天远程办公。远程办公期间需要保持在线。
"""

QUERY = "超过5000元的报销由谁审批？"
NO_ANSWER_QUERY = "公司是否提供住房补贴？"
MAX_DISTANCE = 0.5

CONFIGS = [
    {"name": "coarse", "chunk_size": 500, "chunk_overlap": 0},
    {"name": "balanced", "chunk_size": 100, "chunk_overlap": 20},
    {"name": "tiny", "chunk_size": 25, "chunk_overlap": 0},
]

SECTION_TITLES = {"年假制度", "报销制度", "远程办公"}


def split_text(chunk_size: int, chunk_overlap: int) -> list[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", "。", "；", "，", " ", ""],
    )
    return splitter.split_text(POLICY_TEXT)


def split_by_section(text: str) -> list[str]:
    """优先按照业务章节切分，保留章节标题和对应正文。"""
    sections = []
    current_section = []

    for line in (line.strip() for line in text.splitlines()):
        if not line or line == "员工制度":
            continue

        if line in SECTION_TITLES and current_section:
            sections.append("\n".join(current_section))
            current_section = []

        current_section.append(line)

    if current_section:
        sections.append("\n".join(current_section))

    return sections


def create_collection(
    client: chromadb.Client,
    embedding_function,
    config: dict,
    chunks: list[str],
) -> chromadb.Collection:
    collection = client.create_collection(
        name=f"day31_{config['name']}",
        embedding_function=embedding_function,
    )
    collection.add(
        ids=[f"{config['name']}-{index}" for index in range(len(chunks))],
        documents=chunks,
        metadatas=[
            {
                "config": config["name"],
                "chunk_size": config["chunk_size"],
                "chunk_overlap": config["chunk_overlap"],
            }
            for _ in chunks
        ],
    )
    return collection


def query(collection: chromadb.Collection, text: str, top_k: int = 3) -> list[dict]:
    result = collection.query(
        query_texts=[text],
        n_results=min(top_k, collection.count()),
        include=["documents", "distances"],
    )
    return [
        {"content": content, "distance": distance}
        for content, distance in zip(
            result["documents"][0],
            result["distances"][0],
        )
    ]


def print_chunks(config: dict, chunks: list[str]) -> None:
    print("=" * 70)
    print(
        f"配置：{config['name']} | "
        f"chunk_size={config['chunk_size']} | "
        f"overlap={config['chunk_overlap']} | "
        f"Chunk 数量={len(chunks)}"
    )
    for index, chunk in enumerate(chunks, start=1):
        print(f"Chunk {index} ({len(chunk)} 字符)：{chunk!r}")


def print_results(title: str, results: list[dict]) -> None:
    print(f"\n{title}")
    for index, result in enumerate(results, start=1):
        print(
            f"Top {index} | distance={result['distance']:.4f} | "
            f"{result['content']!r}"
        )


def filter_by_distance(results: list[dict], max_distance: float) -> list[dict]:
    """只保留距离不超过阈值的候选证据。"""
    return [
        result
        for result in results
        if result["distance"] <= max_distance
    ]


def print_threshold_decision(
    question: str,
    results: list[dict],
    max_distance: float,
) -> None:
    """展示阈值过滤后的证据准入结果。"""
    accepted_results = filter_by_distance(results, max_distance)
    print("=" * 70)
    print(f"阈值过滤 | 问题：{question}")
    print(f"规则：保留 distance <= {max_distance}")

    if not accepted_results:
        print("决策：拒绝回答，知识库中没有足够相关的证据。")
        return

    print(f"决策：允许回答，共有 {len(accepted_results)} 条证据通过阈值。")
    print_results("通过阈值的证据：", accepted_results)


def main() -> None:
    embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="BAAI/bge-small-zh-v1.5"
    )
    client = chromadb.Client()
    collections = {}

    for config in CONFIGS:
        chunks = split_text(config["chunk_size"], config["chunk_overlap"])
        print_chunks(config, chunks)
        collection = create_collection(client, embedding_function, config, chunks)
        collections[config["name"]] = collection
        print_results(f"有答案问题：{QUERY}", query(collection, QUERY))

    structure_config = {
        "name": "structure",
        "chunk_size": "按章节",
        "chunk_overlap": 0,
    }
    structure_chunks = split_by_section(POLICY_TEXT)
    print_chunks(structure_config, structure_chunks)
    structure_collection = create_collection(
        client,
        embedding_function,
        structure_config,
        structure_chunks,
    )
    print_results(
        f"有答案问题：{QUERY}",
        query(structure_collection, QUERY),
    )

    balanced = collections["balanced"]
    answer_results = query(balanced, QUERY)
    no_answer_results = query(balanced, NO_ANSWER_QUERY)
    print_results(f"无答案问题：{NO_ANSWER_QUERY}", no_answer_results)

    print_threshold_decision(QUERY, answer_results, MAX_DISTANCE)
    print_threshold_decision(NO_ANSWER_QUERY, no_answer_results, MAX_DISTANCE)


if __name__ == "__main__":
    main()
