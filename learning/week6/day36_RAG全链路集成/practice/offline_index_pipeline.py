"""Day 36：把文档解析、质量门禁、Chunk、Embedding 校验和写入串成一条链路。"""

from __future__ import annotations

import hashlib
import importlib.util
import sys
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType

import chromadb
import numpy as np
from chromadb.utils import embedding_functions
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


LEARNING_DIR = Path(__file__).resolve().parents[3]
LOADER_PATH = (
    LEARNING_DIR
    / "week5"
    / "day30_多格式文档解析"
    / "practice"
    / "unified_loader.py"
)
MODEL_NAME = "BAAI/bge-small-zh-v1.5"
EXPECTED_VECTOR_DIMENSION = 512


def load_practice_module(module_name: str, module_path: Path) -> ModuleType:
    """从既有课程文件加载代码，避免复制 Day 30 的解析实现。"""
    module_spec = importlib.util.spec_from_file_location(module_name, module_path)
    if module_spec is None or module_spec.loader is None:
        raise ImportError(f"无法加载课程模块：{module_path}")

    module = importlib.util.module_from_spec(module_spec)
    sys.modules[module_name] = module
    module_spec.loader.exec_module(module)
    return module


unified_loader = load_practice_module("day30_unified_loader", LOADER_PATH)
ParseResult = unified_loader.ParseResult
load_document = unified_loader.load_document


@dataclass
class PreparedIndexBatch:
    """已经通过解析门禁并完成切分、但尚未写入数据库的批次。"""

    ids: list[str]
    chunks: list[Document]
    vectors: list


@dataclass
class IndexBuildReport:
    """离线索引构建结果，用于验证每个阶段的数量变化。"""

    file_name: str
    parse_status: str
    document_count: int
    chunk_count: int
    vector_count: int
    stored_count: int


def enforce_parse_gate(
    parse_result: ParseResult,
    require_complete: bool,
) -> None:
    """根据解析事实和业务完整性策略决定是否允许继续。"""
    if parse_result.status == "success":
        return

    if parse_result.status == "partial" and not require_complete:
        return

    raise ValueError(
        "解析质量门禁拒绝："
        f"status={parse_result.status}, "
        f"require_complete={require_complete}, "
        f"warnings={parse_result.warnings}"
    )


def create_stable_chunk_id(chunk: Document, chunk_index: int) -> str:
    """用来源、文档版本、结构位置、序号和正文生成稳定 ID。"""
    metadata = chunk.metadata
    identity_text = "|".join(
        [
            str(metadata.get("source", "unknown")),
            str(metadata.get("document_version", "unknown")),
            str(metadata.get("page", metadata.get("block_index", "unknown"))),
            str(chunk_index),
            chunk.page_content,
        ]
    )
    return hashlib.sha256(identity_text.encode("utf-8")).hexdigest()[:24]


def split_documents(
    parse_result: ParseResult,
    document_version: str,
    tenant_id: str,
    allowed_role: str,
) -> list[Document]:
    """切分正文，并把文件级质量信息传播到每一个 Chunk。"""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", "。", "；", "，", " ", ""],
    )
    chunks = splitter.split_documents(parse_result.documents)

    for chunk_index, chunk in enumerate(chunks, start=1):
        chunk.metadata.update(
            {
                "chunk_index": chunk_index,
                "document_version": document_version,
                "tenant_id": tenant_id,
                "allowed_role": allowed_role,
                "parse_status": parse_result.status,
                "parse_warnings": " | ".join(parse_result.warnings),
            }
        )
    return chunks


def validate_prepared_batch(batch: PreparedIndexBatch) -> None:
    """写入前验证 ID、Chunk、metadata 和 Vector 的一一对应关系。"""
    chunk_count = len(batch.chunks)
    if chunk_count == 0:
        raise ValueError("索引批次为空")

    if len(batch.ids) != chunk_count:
        raise ValueError("Chunk ID 数量与 Chunk 数量不一致")

    if len(set(batch.ids)) != len(batch.ids):
        raise ValueError("Chunk ID 存在重复")

    if len(batch.vectors) != chunk_count:
        raise ValueError("Vector 数量与 Chunk 数量不一致，拒绝整个批次")

    for vector_index, vector in enumerate(batch.vectors, start=1):
        if len(vector) != EXPECTED_VECTOR_DIMENSION:
            raise ValueError(
                f"第 {vector_index} 个 Vector 维度错误："
                f"期望 {EXPECTED_VECTOR_DIMENSION}，实际 {len(vector)}"
            )
        if not np.isfinite(vector).all():
            raise ValueError(f"第 {vector_index} 个 Vector 包含 NaN 或 Infinity")

    for chunk_index, chunk in enumerate(batch.chunks, start=1):
        required_metadata = {
            "source",
            "file_type",
            "chunk_index",
            "document_version",
            "tenant_id",
            "allowed_role",
            "parse_status",
        }
        missing_metadata = required_metadata - chunk.metadata.keys()
        if missing_metadata:
            raise ValueError(
                f"第 {chunk_index} 个 Chunk 缺少 metadata："
                f"{sorted(missing_metadata)}"
            )


def prepare_index_batch(
    parse_result: ParseResult,
    document_version: str,
    tenant_id: str,
    allowed_role: str,
) -> PreparedIndexBatch:
    """在内存中完成 Chunk 和 Embedding，校验通过前不写数据库。"""
    chunks = split_documents(
        parse_result,
        document_version,
        tenant_id,
        allowed_role,
    )
    chunk_ids = [
        create_stable_chunk_id(chunk, chunk_index)
        for chunk_index, chunk in enumerate(chunks, start=1)
    ]

    embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=MODEL_NAME,
        normalize_embeddings=True,
    )
    vectors = embedding_function(
        [chunk.page_content for chunk in chunks]
    )

    batch = PreparedIndexBatch(
        ids=chunk_ids,
        chunks=chunks,
        vectors=vectors,
    )
    validate_prepared_batch(batch)
    return batch


def write_validated_batch(
    collection: chromadb.Collection,
    batch: PreparedIndexBatch,
) -> None:
    """只对完整通过校验的批次执行一次写入。"""
    stored_count_before_write = collection.count()
    collection.add(
        ids=batch.ids,
        documents=[chunk.page_content for chunk in batch.chunks],
        metadatas=[chunk.metadata for chunk in batch.chunks],
        embeddings=batch.vectors,
    )

    expected_count_after_write = stored_count_before_write + len(batch.chunks)
    if collection.count() != expected_count_after_write:
        raise RuntimeError("写入后记录数量与预期不一致")


def build_offline_index(
    file_path: Path,
    document_version: str,
    tenant_id: str,
    allowed_role: str,
    require_complete: bool,
) -> tuple[chromadb.Collection, IndexBuildReport]:
    """执行完整的离线索引数据流。"""
    parse_result = load_document(file_path)
    enforce_parse_gate(parse_result, require_complete)
    batch = prepare_index_batch(
        parse_result,
        document_version,
        tenant_id,
        allowed_role,
    )

    client = chromadb.Client()
    collection = client.create_collection(
        name="day36_integrated_offline_index",
        metadata={"hnsw:space": "cosine"},
    )
    write_validated_batch(collection, batch)

    report = IndexBuildReport(
        file_name=parse_result.file_name,
        parse_status=parse_result.status,
        document_count=len(parse_result.documents),
        chunk_count=len(batch.chunks),
        vector_count=len(batch.vectors),
        stored_count=collection.count(),
    )
    return collection, report


def demonstrate_strict_partial_rejection() -> str:
    """构造部分解析结果，证明高风险策略会在 Embedding 前拒绝。"""
    synthetic_partial_result = ParseResult(
        file_name="synthetic_repayment_spec.docx",
        file_type="docx",
        status="partial",
        documents=[
            Document(
                page_content="还款回调说明。关键字段表位于未解析图片中。",
                metadata={
                    "source": "synthetic_repayment_spec.docx",
                    "file_type": "docx",
                    "block_index": 1,
                },
            )
        ],
        warnings=["关键回调字段表未解析，需要 OCR"],
    )

    try:
        enforce_parse_gate(
            synthetic_partial_result,
            require_complete=True,
        )
    except ValueError as error:
        return str(error)

    raise AssertionError("高风险 partial 文档不应通过解析质量门禁")


def demonstrate_vector_count_rejection() -> str:
    """构造数量错配，证明不会把不完整 Vector 批次写入数据库。"""
    chunks = [
        Document(
            page_content=f"Chunk {index}",
        metadata={
            "source": "synthetic.docx",
            "file_type": "docx",
            "chunk_index": index,
            "document_version": "v1",
            "tenant_id": "tenant-a",
            "allowed_role": "developer",
            "parse_status": "success",
            },
        )
        for index in range(1, 4)
    ]
    mismatched_batch = PreparedIndexBatch(
        ids=["chunk-1", "chunk-2", "chunk-3"],
        chunks=chunks,
        vectors=[
            np.zeros(EXPECTED_VECTOR_DIMENSION),
            np.zeros(EXPECTED_VECTOR_DIMENSION),
        ],
    )

    try:
        validate_prepared_batch(mismatched_batch)
    except ValueError as error:
        return str(error)

    raise AssertionError("Vector 数量错配不应通过批次校验")


def demonstrate_versioned_chunk_ids() -> str:
    """证明同位置、同正文的不同文档版本不会产生 Chunk ID 碰撞。"""
    common_metadata = {
        "source": "synthetic.docx",
        "file_type": "docx",
        "block_index": 1,
        "chunk_index": 1,
        "parse_status": "success",
    }
    version_1_chunk = Document(
        page_content="相同位置、相同正文。",
        metadata={**common_metadata, "document_version": "v1"},
    )
    version_2_chunk = Document(
        page_content="相同位置、相同正文。",
        metadata={**common_metadata, "document_version": "v2"},
    )

    version_1_id = create_stable_chunk_id(version_1_chunk, chunk_index=1)
    version_2_id = create_stable_chunk_id(version_2_chunk, chunk_index=1)
    if version_1_id == version_2_id:
        raise AssertionError("不同文档版本不应生成相同 Chunk ID")

    return f"v1={version_1_id}, v2={version_2_id}, collision=False"


def main() -> None:
    fixture_path = (
        LEARNING_DIR
        / "week4"
        / "day27_PDF-Word解析"
        / "documents"
        / "sample_contract.docx"
    )
    _, report = build_offline_index(
        file_path=fixture_path,
        document_version="synthetic-v1",
        tenant_id="tenant-a",
        allowed_role="developer",
        require_complete=True,
    )

    print("=== 完整文档索引 ===")
    print(report)
    print("\n=== partial 门禁故障注入 ===")
    print(demonstrate_strict_partial_rejection())
    print("\n=== Vector 数量故障注入 ===")
    print(demonstrate_vector_count_rejection())
    print("\n=== 文档版本 Chunk ID 隔离 ===")
    print(demonstrate_versioned_chunk_ids())


if __name__ == "__main__":
    main()
