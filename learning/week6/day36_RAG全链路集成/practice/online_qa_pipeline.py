"""Day 36：版本和权限过滤 → 检索 → 证据门禁 → 生成 → 校验 → 纠错重试。"""

from __future__ import annotations

import importlib.util
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Callable

import chromadb
from chromadb.utils import embedding_functions


PRACTICE_DIR = Path(__file__).resolve().parent
OFFLINE_PIPELINE_PATH = PRACTICE_DIR / "offline_index_pipeline.py"
MAX_COSINE_DISTANCE = 0.4
TOP_K = 3


def load_practice_module(module_name: str, module_path: Path) -> ModuleType:
    """动态加载同一天的离线代码，避免复制模型和索引逻辑。"""
    module_spec = importlib.util.spec_from_file_location(module_name, module_path)
    if module_spec is None or module_spec.loader is None:
        raise ImportError(f"无法加载课程模块：{module_path}")

    module = importlib.util.module_from_spec(module_spec)
    sys.modules[module_name] = module
    module_spec.loader.exec_module(module)
    return module


offline_pipeline = load_practice_module(
    "day36_offline_index_pipeline",
    OFFLINE_PIPELINE_PATH,
)


@dataclass(frozen=True)
class AccessScope:
    """本次查询允许访问的数据边界。"""

    tenant_id: str
    role: str
    document_version: str


@dataclass
class RetrievalResult:
    """区分向量库候选和真正允许进入提示词的证据。"""

    retrieved_candidates: list[dict]
    accepted_evidence: list[dict]


@dataclass
class OutputValidation:
    """保存输出是否通过以及可用于纠错重试的失败原因。"""

    is_valid: bool
    reason: str


@dataclass
class AnswerResult:
    """保留原始输入、每次原始输出和最终业务结果，便于排错。"""

    status: str
    raw_input: str | None
    raw_outputs: list[str]
    final_output: str


def build_pre_retrieval_filter(access_scope: AccessScope) -> dict:
    """构造必须在前 K 条检索之前生效的版本、租户和角色过滤条件。"""
    return {
        "$and": [
            {"document_version": {"$eq": access_scope.document_version}},
            {"tenant_id": {"$eq": access_scope.tenant_id}},
            {"allowed_role": {"$eq": access_scope.role}},
        ]
    }


def retrieve_evidence(
    collection: chromadb.Collection,
    question: str,
    access_scope: AccessScope,
) -> RetrievalResult:
    """使用与离线阶段完全相同的模型生成问题向量并检索证据。"""
    embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=offline_pipeline.MODEL_NAME,
        normalize_embeddings=True,
    )
    question_vector = embedding_function([question])[0]
    query_result = collection.query(
        query_embeddings=[question_vector],
        n_results=TOP_K,
        where=build_pre_retrieval_filter(access_scope),
        include=["documents", "metadatas", "distances"],
    )

    # zip（并行组合）把向量库分列返回的数据重新合并成一条条候选记录。
    retrieved_candidates = [
        {
            "chunk_id": chunk_id,
            "content": content,
            "metadata": metadata,
            "distance": distance,
        }
        for chunk_id, content, metadata, distance in zip(
            query_result["ids"][0],
            query_result["documents"][0],
            query_result["metadatas"][0],
            query_result["distances"][0],
        )
    ]
    accepted_evidence = [
        candidate
        for candidate in retrieved_candidates
        if candidate["distance"] <= MAX_COSINE_DISTANCE
    ]
    return RetrievalResult(retrieved_candidates, accepted_evidence)


def number_accepted_evidence(accepted_evidence: list[dict]) -> list[dict]:
    """只给通过相关性门禁的证据分配引用编号。"""
    return [
        {**evidence, "citation_id": f"E{index}"}
        for index, evidence in enumerate(accepted_evidence, start=1)
    ]


def validate_llm_input(
    numbered_evidence: list[dict],
    access_scope: AccessScope,
) -> None:
    """在调用大模型前校验证据身份、访问范围和编号。"""
    if not numbered_evidence:
        raise ValueError("没有通过相关性门禁的证据，不允许调用大模型")

    expected_citation_ids = [
        f"E{index}" for index in range(1, len(numbered_evidence) + 1)
    ]
    actual_citation_ids = [
        evidence["citation_id"] for evidence in numbered_evidence
    ]
    if actual_citation_ids != expected_citation_ids:
        raise ValueError("证据编号不连续或顺序错误")

    for evidence in numbered_evidence:
        metadata = evidence["metadata"]
        if metadata["document_version"] != access_scope.document_version:
            raise ValueError("证据版本越界")
        if metadata["tenant_id"] != access_scope.tenant_id:
            raise ValueError("证据租户越界")
        if metadata["allowed_role"] != access_scope.role:
            raise ValueError("证据角色权限越界")
        if not evidence["content"].strip():
            raise ValueError("证据正文为空")


def build_context(numbered_evidence: list[dict]) -> str:
    """组装带引用编号、来源、位置和版本的证据上下文。"""
    context_blocks = []
    for evidence in numbered_evidence:
        metadata = evidence["metadata"]
        source_location = metadata.get(
            "page",
            metadata.get("block_index", "unknown"),
        )
        context_blocks.append(
            f"[{evidence['citation_id']}]\n"
            f"正文：{evidence['content']}\n"
            f"来源：{metadata['source']}\n"
            f"位置：{source_location}\n"
            f"版本：{metadata['document_version']}"
        )
    return "\n\n".join(context_blocks)


def build_initial_input(question: str, context: str) -> str:
    """组装第一次调用大模型的完整原始输入。"""
    return (
        "系统规则：\n"
        "1. 只能根据证据回答，不得补充证据之外的信息。\n"
        "2. 每条独立结论必须引用证据编号，例如 [E1]。\n"
        "3. 证据不足时明确说明无法回答，不得编造证据编号。\n\n"
        f"用户问题：{question}\n\n"
        "<evidence>\n"
        f"{context}\n"
        "</evidence>"
    )


def validate_output(
    raw_output: str,
    numbered_evidence: list[dict],
) -> OutputValidation:
    """校验引用存在性；事实是否被证据支持仍需独立语义校验。"""
    cited_ids = re.findall(r"\[(E\d+)]", raw_output)
    if not cited_ids:
        return OutputValidation(False, "回答没有引用任何证据")

    allowed_ids = {
        evidence["citation_id"] for evidence in numbered_evidence
    }
    invalid_ids = sorted(set(cited_ids) - allowed_ids)
    if invalid_ids:
        return OutputValidation(
            False,
            f"回答引用了不存在的证据编号：{invalid_ids}",
        )

    return OutputValidation(True, "引用编号结构校验通过")


def build_corrective_retry_input(
    original_input: str,
    failed_output: str,
    failure_reason: str,
    numbered_evidence: list[dict],
) -> str:
    """把第一次失败事实和合法编号白名单加入第二次输入。"""
    allowed_ids = [
        evidence["citation_id"] for evidence in numbered_evidence
    ]
    return (
        f"{original_input}\n\n"
        "上一次回答未通过输出校验，请纠正后重新回答。\n"
        f"失败原因：{failure_reason}\n"
        f"合法证据编号白名单：{allowed_ids}\n"
        f"上一次不合格回答：{failed_output}\n"
        "只能引用白名单中的编号；没有证据支持的结论必须删除。"
    )


def answer_question(
    collection: chromadb.Collection,
    question: str,
    access_scope: AccessScope,
    generate: Callable[[str], str],
) -> AnswerResult:
    """执行在线链路，并在第一次输出失败时进行一次纠错重试。"""
    retrieval_result = retrieve_evidence(
        collection,
        question,
        access_scope,
    )
    if not retrieval_result.accepted_evidence:
        return AnswerResult(
            status="no_evidence",
            raw_input=None,
            raw_outputs=[],
            final_output="无法回答：没有足够可靠且有权限访问的证据。",
        )

    numbered_evidence = number_accepted_evidence(
        retrieval_result.accepted_evidence
    )
    validate_llm_input(numbered_evidence, access_scope)
    context = build_context(numbered_evidence)
    raw_input = build_initial_input(question, context)

    first_raw_output = generate(raw_input)
    raw_outputs = [first_raw_output]
    first_validation = validate_output(
        first_raw_output,
        numbered_evidence,
    )
    if first_validation.is_valid:
        return AnswerResult(
            status="answered",
            raw_input=raw_input,
            raw_outputs=raw_outputs,
            final_output=first_raw_output,
        )

    retry_input = build_corrective_retry_input(
        raw_input,
        first_raw_output,
        first_validation.reason,
        numbered_evidence,
    )
    second_raw_output = generate(retry_input)
    raw_outputs.append(second_raw_output)
    second_validation = validate_output(
        second_raw_output,
        numbered_evidence,
    )
    if second_validation.is_valid:
        return AnswerResult(
            status="answered_after_retry",
            raw_input=retry_input,
            raw_outputs=raw_outputs,
            final_output=second_raw_output,
        )

    return AnswerResult(
        status="rejected_after_retry",
        raw_input=retry_input,
        raw_outputs=raw_outputs,
        final_output=(
            "无法回答：两次生成结果均未通过证据引用校验。"
            f"最后失败原因：{second_validation.reason}"
        ),
    )


class ScriptedGenerator:
    """模拟第一次产生非法引用、第二次根据纠错信息修正的大模型。"""

    def __init__(self) -> None:
        self.call_count = 0

    def __call__(self, raw_input: str) -> str:
        # 实例可以像函数一样被调用；每次调用都会执行 __call__。
        self.call_count += 1
        if self.call_count == 1:
            return "系统开发价格为100000元。[E3]"
        return "系统开发价格为100000元。[E1]"


def build_versioned_demo_collection() -> chromadb.Collection:
    """把同一文档的两个版本写入同一集合，验证版本隔离。"""
    fixture_path = (
        offline_pipeline.LEARNING_DIR
        / "week4"
        / "day27_PDF-Word解析"
        / "documents"
        / "sample_contract.docx"
    )
    parse_result = offline_pipeline.load_document(fixture_path)
    offline_pipeline.enforce_parse_gate(
        parse_result,
        require_complete=True,
    )

    collection = chromadb.Client().create_collection(
        name="day36_versioned_online_qa",
        metadata={"hnsw:space": "cosine"},
    )
    for document_version in ["v1", "v2"]:
        batch = offline_pipeline.prepare_index_batch(
            parse_result,
            document_version=document_version,
            tenant_id="tenant-a",
            allowed_role="developer",
        )
        offline_pipeline.write_validated_batch(collection, batch)
    return collection


def main() -> None:
    collection = build_versioned_demo_collection()
    access_scope = AccessScope(
        tenant_id="tenant-a",
        role="developer",
        document_version="v2",
    )
    retrieval_result = retrieve_evidence(
        collection,
        question="系统开发价格是多少？",
        access_scope=access_scope,
    )
    retrieved_versions = {
        candidate["metadata"]["document_version"]
        for candidate in retrieval_result.retrieved_candidates
    }
    if retrieved_versions != {"v2"}:
        raise AssertionError(f"版本过滤失败：{retrieved_versions}")

    answer_result = answer_question(
        collection,
        question="系统开发价格是多少？",
        access_scope=access_scope,
        generate=ScriptedGenerator(),
    )
    print(f"集合记录数：{collection.count()}")
    print(f"检索到的版本：{retrieved_versions}")
    print(f"第一次原始输出：{answer_result.raw_outputs[0]}")
    print(f"第二次原始输出：{answer_result.raw_outputs[1]}")
    print(f"最终状态：{answer_result.status}")
    print(f"最终回答：{answer_result.final_output}")


if __name__ == "__main__":
    main()
