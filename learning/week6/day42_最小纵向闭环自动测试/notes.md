# Day 42：最小纵向闭环 + 自动测试

## 学习日期

2026-07-29

## 学习目标与边界

目标：把结构化抽取契约落成最小可运行链路，证明 approved 契约可以生成 FundManagerImpl 风格骨架，candidate 或包含自由代码的契约会被生成闸门拒绝。

不学习：

- 不实现生产级 Java 工程和真实资方业务逻辑；
- 不接真实资方；
- 不生成可上线业务代码；
- 不引入 Agent 编排；
- 不提交 `generated/` 运行产物。

## 最小纵向闭环

```text
synthetic_mapping.json
→ validate_mapping.py 校验 approved 契约
→ generate_fund_manager.py 渲染 Java 模板
→ generated/java-adapter 输出骨架和生成清单
→ invalid_candidate_mapping.json 验证未批准候选被拒绝
→ invalid_freeform_code_mapping.json 验证自由 Java 代码字段被拒绝
→ run_minimal_vertical_slice.py 自动化整条验证链路
```

## 本次新增产物

作品集仓库：

```text
/Users/zhangyusong/Documents/AICoding/financial-institution-integration-skill
```

新增：

- `skill/integrate-financial-institution/scripts/generate_fund_manager.py`
- `evals/run_minimal_vertical_slice.py`
- `fixtures/invalid_candidate_mapping.json`
- `fixtures/invalid_freeform_code_mapping.json`

生成产物位于 `generated/`，该目录被 Git 忽略。

## 验证命令

```bash
python3 evals/run_minimal_vertical_slice.py
```

验证结果：

```text
PASS: minimal vertical slice
GENERATED: .../generated/minimal-vertical-slice/java-adapter/FundManagerImpl.java
GENERATED: .../generated/minimal-vertical-slice/java-adapter/FundVariables.java
GENERATED: .../generated/minimal-vertical-slice/java-adapter/FundManagerImplContractTest.java
GENERATED: .../generated/minimal-vertical-slice/java-adapter/generation_manifest.json
```

## 安全闸门

正向样例：

- `fixtures/synthetic_mapping.json`
- 所有 `operation`、`variable`、`mapping`、`stage_dependency` 均为 `approved`
- 允许生成 Java 骨架

负向样例 1：

- `fixtures/invalid_candidate_mapping.json`
- 存在 `status = candidate`
- 生成器拒绝，错误包含 `must be approved before generation`

负向样例 2：

- `fixtures/invalid_freeform_code_mapping.json`
- 存在 `transformation_code`
- 生成器拒绝，错误包含 `forbidden free-form code fields`

## 核心理解

这次闭环证明的是：

- 生成器不是直接相信 AI 输出；
- 生成器复用确定性校验；
- 只有 approved 契约能进入 Java 骨架生成；
- 自由 Java 转换代码不能进入生成链路；
- 生成产物与源仓库隔离，避免把运行结果提交到 Git。

## 尚未完成

- 生成的 Java 仍是骨架，不包含真实资方业务实现；
- 当前已补充 `javac/java` 编译和最小契约测试，但还不是完整 Maven 工程；
- 尚未根据 `operations` 动态生成完整方法列表；
- 尚未生成字段级映射代码，只生成骨架和变量校验；
- 尚未接入 JSON Schema 或更完整的 golden set。

## 2026-07-30 进度修正

作品集仓库后续已继续推进到生产风格 RAG demo：

```text
Chroma RAG
→ PostgreSQL + pgvector
→ 真实开源 embedding 模型验证
→ pgvector + RAG + DeepSeek 主链路
→ Java SPI 骨架生成
→ javac/java 编译和最小契约测试
```

最新已推送提交：

```text
f96617a feat: add production-style pgvector rag pipeline
```

新增验证结果：

```text
PASS: local Chroma RAG pipeline
PASS: PostgreSQL + pgvector RAG pipeline
PASS: V0.1 pipeline (real_llm)
PASS: FundManagerImpl contract test
PASS: Java skeleton compile and contract test
```

因此 Week 6 实际学习状态应修正为已完成，下一步进入 Week 7。

## 下一步

下一步应进入 Week 7：

```text
标准字段映射
→ 差异、冲突与待确认项
→ 带范围过滤的 RAG 证据检索
→ 证据编号 + 人工确认状态流
→ Java 适配器骨架生成
→ Maven 编译 + 契约测试
```

进入 Week 7 前，建议同步页面/数据库进度，并提交本仓库学习记录。
