# 作品集一深度拆解：金融机构接入 AI 工程

> 本文档按"总分总"结构，对 financial-institution-integration-skill 项目全部 7 个核心模块做系统讲解。
> 以 RAG 全链路为重点，同时保持与当前 LLM 直写、方法级证据追溯和验证边界一致。
> 配合项目源码 `skill/integrate-financial-institution/scripts/` 和 `evals/` 下的实际文件阅读，效果最佳。

---

## 总（一）：项目整体架构

### 项目定位

本项目解决金融助贷行业中"多资方接入"的两个核心问题：

1. **资方知识库**：将各资方的产品需求文档和 API 文档统一解析、向量化存储，支持按机构/操作/内容类型检索、查询、统计和分析，替代人工翻阅散落的 Word/PDF/Excel。
2. **生成完整 Java SPI 代码包**：基于知识库检索证据，由 LLM 抽取结构化契约，经离线人工审批后生成完整合成 SPI，并执行追溯、编译、契约和 golden 验证。

### 技术架构（离线索引 + 在线检索两阶段）

标准 RAG 系统分为两个阶段，本项目严格遵循这个划分：

> **离线索引**（文档更新时执行一次）：把文档转成可检索的向量索引。建一次，多次复用。
>
> **在线检索 + 抽取**（每次查询都执行）：用查询去向量库里搜相关证据，拼成上下文喂给 LLM，产出结构化结果。

```
══════════════════════ 离线索引阶段（一次性构建） ══════════════════════

输入文档 ─────────▶ ┌──────────────┐
产品需求 + 机构API  │ 1. 文档解析   │ unified_parser.py (429行)
*.md *.docx        │   ParseResult  │ parse_model.py (75行)
*.pdf *.xlsx       └──────┬───────┘
                          │ DocumentBlock[]
                          ▼
                   ┌──────────────┐
                   │ 2. 文本切块   │ rag_model.py::split_text_into_chunks()
                   │   Chunk[]     │ MAX_CHUNK=900字, OVERLAP=120字
                   └──────┬───────┘
                          │ Chunk.content + metadata
                          ▼
                   ┌──────────────┐
                   │ 3. 向量化     │ embedding_provider.py
                   │   embedding   │ bge-small-zh-v1.5, 512维, L2归一化
                   └──────┬───────┘
                          │ 512 维浮点数向量
                          ▼
                   ┌──────────────┐
                   │ 4. 向量持久化 │ rag_pgvector_index.py (189行)
                   │   写入数据库   │ ON CONFLICT 幂等性
                   │   建索引       │ B-tree / GIN / HNSW
                   │   5 张审计表   │ init.sql (77行)
                   └──────┬───────┘
                          │
                          ▼
              ┌─────────────────────┐
              │    向量数据库        │  ← 索引一次构建，可被无数查询复用
              │  pgvector / Chroma  │
              └─────────┬───────────┘
                        │
══════════════════════ 在线检索 + 抽取阶段 ══════════════════════
                        │
           用户查询 ────┘
           "抽取 AURORA_DEMO 接入说明书"
                        │
                        ▼
              ┌─────────────────────────────┐
              │   5. LLM 结构化抽取          │
              │                              │
              │  ┌─ 5a. 向量检索 ──────────┐ │
              │  │ embedding(查询) →        │ │
              │  │ metadata 过滤 →          │ │  ← 检索是 LLM 抽取的
              │  │ pgvector <=> HNSW 索引 → │ │    上下文准备步骤，
              │  │ Top-K → 距离阈值 →       │ │    不是独立的管道层
              │  │ accepted_evidence        │ │
              │  └──────────┬───────────────┘ │
              │             │                 │
              │  ┌──────────▼───────────────┐ │
              │  │ 5a→5b 衔接：             │ │
              │  │ 证据打包为编号上下文       │ │  ← 检索产物 = LLM 输入
              │  │ llm_input_context.md     │ │    (accepted_evidence 打包
              │  └──────────┬───────────────┘ │     成 E1/E2... 编号证据)
              │             ▼                 │
              │  ┌─ 5b. 拼 prompt + 调 LLM ─┐│
              │  │ --input 该文件 →          ││  llm_extract_integration_spec.py
              │  │ system prompt →           ││  (410行), JSON Schema约束,
              │  │ DeepSeek/OpenAI API →     ││  evidence溯源, temperature=0
              │  │ candidate spec            ││
              │  └──────────────────────────┘ │
              └──────────────┬──────────────┘
                             │ integration_spec_candidate.json
                             ▼
                    ┌──────────────┐
                    │ 6. 审批闸门   │ 离线人工复核
                    │  人工逐字段核对│ derive + validate code_model
                    │  candidate →  │ 交叉引用一致性校验
                    │  approved     │
                    └──────┬───────┘
                           │ integration_spec_approved.json
                           ▼
                    ┌──────────────┐
                    │ (下游) Java   │ code_synth_agent.py
                    │ 完整SPI生成   │ 追溯 + Maven/契约/golden
                    └──────────────┘
```

**关键架构决策说明**：

1. **离线索引 vs 在线检索是 RAG 系统的核心分界**。索引阶段（1-4）只在文档更新时执行；检索+抽取阶段（5-6）每次查询都执行。把两者混成一个管道是 demo 的常见错误——它掩盖了"建一次索引可以被无数次检索复用"这个关键生产特性。

2. **向量检索不是独立的管道层**，它是 LLM 抽取的上下文准备步骤。在代码中体现为 `prepare_rag_context()` 函数——它先建索引、再检索、返回 `llm_input_context.md`，然后 `llm_extract_integration_spec.py` 以这个文件为输入进行抽取。检索产出的 `accepted_evidence` 的唯一消费者就是 LLM 抽取环节。

### 核心数据流：从检索到 LLM 输入的完整流转

理解这条数据流转是理解全链路的核心——**检索的产物就是 LLM 的输入，中间通过一份衔接文件 `llm_input_context.md` 连接**：

```
向量库返回 Top-K（不管质量）
        │
        ▼
retrieved_candidates（检索候选）── 距离阈值过滤 ──▶ accepted_evidence（可采纳证据）
        │                                              │
        │                                              ▼
        │                               打包为编号证据上下文：llm_input_context.md
        │                               （每条证据带 E1/E2 编号 + 文档名 + 定位 + 原文）
        │                                              │
        │                                              ▼
        │                               llm_extract_integration_spec.py --input 该文件
        │                                              │
        │                                              ▼
        └──────────────────────────────▶ candidate spec（候选说明书，每条带 evidence 溯源）
```

| 阶段 | 产物 | 含义 | 谁消费 |
|---|---|---|---|
| 检索后 | **retrieved_candidates**（检索候选） | 向量库返回的 Top-K 个最相似 chunk，不管质量好坏 | 阈值过滤环节 |
| 阈值过滤后 | **accepted_evidence**（可采纳证据） | 候选里距离 ≤ 阈值的部分，真正可信的证据 | 打包成 llm_input_context.md |
| 打包后 | **llm_input_context.md**（编号证据上下文） | accepted_evidence 按 E1/E2 编号整理成的 Markdown，带文档名+定位+原文 | **LLM 抽取（--input）** |
| LLM 输出后 | **candidate spec**（候选说明书） | LLM 基于证据抽取的结构化 JSON，每条带 evidence 溯源 | 审批闸门 |

**两个关键区分**：

1. `retrieved_candidates ≠ accepted_evidence`——Top-K 返回的候选里，只有距离 ≤ 阈值的才可信。给 LLM 的必须是过滤后的，否则会把不相关的内容当证据。
2. **LLM 看不到原始文档，只看到 `llm_input_context.md`**——这就是 RAG（检索增强生成）里"增强"的含义：用检索到的真实证据喂给 LLM，而不是让它凭训练数据瞎编。代码上对应 `prepare_rag_context()` 返回该文件、`llm_extract_integration_spec.py --input` 消费它。

### 输入模型

项目输入是两类文档的组合：

| 输入类型 | 典型文件 | 提供什么 |
|---|---|---|
| **产品需求说明书** | `fixtures/*产品接入需求说明书.md` | 接入逻辑（事件流、字段映射方向、跨接口依赖、配置项清单） |
| **机构 API 文档** | `synthetic_aurora_api_spec.md` 等 | 技术接口细节（URL、字段名、数据类型、认证方式） |

多机构文档共存于同一知识库，通过 metadata filter（`--rag-where '{"institution":"AURORA_DEMO"}'`）限定检索范围。

---

## 分：模块逐块拆解

### 第一块：文档解析（unified_parser.py + parse_model.py）

#### 概念
**文档解析（document parsing）** 就是把各种格式（Word/PDF/Excel）的原始文件，统一转成结构化的"文档块列表"，每个块带着定位信息（第几页、第几段、哪个 sheet 第几行）。

#### 核心原理（看源码说话）

**1. ParseState 四状态模型**（`parse_model.py` 第 8-13 行）

```python
class ParseState(str, Enum):
    SUCCESS = "success"         # 完整解析成功
    PARTIAL = "partial"         # 部分成功（比如 PDF 50% 页面有文本）
    FAILURE = "failure"         # 完全失败（格式损坏、库缺失）
    OCR_NEEDED = "ocr_needed"   # 需要 OCR（图片型 PDF，无文字层）
```

这四种状态不是拍脑袋分的。**PARTIAL（部分成功）是关键设计**——它允许"文档解析得不完美但还能用"。比如一份 PDF 里有几页是扫描件没文字，另外几页是正常的文本图层，解析器能告诉你"5/10 页成功、另外 5 页需要 OCR"，而不是直接把整份文档扔掉。

**2. 定位溯源机制**（`parse_model.py` 第 16-28 行）

```python
@dataclass
class DocumentLocator:
    page: Optional[str] = None       # 页码
    section: Optional[str] = None    # 章节编号
    paragraph: Optional[int] = None  # 段落序号
    table_index: Optional[int] = None
    table_row: Optional[int] = None
    sheet: Optional[str] = None      # Excel 工作表名
    row: Optional[int] = None        # Excel 行号
```

每个 `DocumentBlock` 都带着定位信息。为什么重要？因为 LLM 抽取结果里每条字段映射都要带 `evidence`（证据）——引用原始文档的哪一段。没有定位信息，"4.1.1 款"就无法追溯到原文到底在哪。

**3. 按文档顺序交错处理段落和表格**（`unified_parser.py` 第 108-148 行，DOCX 解析核心逻辑）

这是容易被忽略的细节。DOCX 文件内部，段落（`<w:p>`）和表格（`<w:tbl>`）是按 XML 顺序交叉排列的，你不能先读完全部段落再读表格，否则会丢失"这段文字描述的就是下面那个表"的位置关系。

```python
for child in body:
    tag = child.tag.split('}')[-1]
    if tag == 'p' and para_i < total_paras:
        # 处理段落
    elif tag == 'tbl' and table_i < total_tables:
        # 处理表格（同时产出 table_row 和 table_full 两种 block）
```

**4. 表格的双重表示**（`unified_parser.py` 第 130-148 行）

每行既作为独立的 `table_row` block 入库（方便检索到具体某一行），也合并为 `table_full` block 入库（保留完整表格语义）。这是生产 RAG 里常见的"细粒度+粗粒度双索引"策略的简化版。

#### 具体用法

```bash
cd /Users/zhangyusong/Documents/AICoding/financial-institution-integration-skill

# 解析单个 DOCX 文件，输出 JSON
.venv/bin/python skill/integrate-financial-institution/scripts/unified_parser.py \
  fixtures/synthetic_huarong_api_spec.docx \
  --require-complete

# 解析 Excel，允许部分成功
.venv/bin/python skill/integrate-financial-institution/scripts/unified_parser.py \
  fixtures/synthetic_dingcheng_api_spec.xlsx \
  --require-complete
```

#### 生产级使用流程及注意事项

| 事项 | 说明 | 本项目里的体现 |
|---|---|---|
| **格式检测** | 先判断文件后缀是否支持，不支持的立即报错不让入库 | `unified_parser.py:50-55`，`SUPPORTED_FORMATS = {".docx", ".pdf", ".xlsx"}` |
| **部分成功处理** | PARTIAL 状态的解析结果是否允许继续走下游？默认挡掉，`--allow-partial-parse` 放行 | `rag_index.py:69` → 不允许多报错；`--allow-partial-parse` 放行 |
| **空文档检测** | PDF 全是图片（0 文本）→ 标记 OCR_NEEDED，不是 FAILURE | `unified_parser.py:228-232` |
| **版本号自动提取** | 从文档内容里用正则搜版本号（V1.0、v2.3 等），失败标注 unknown | `unified_parser.py:355-383` |
| **依赖库缺失处理** | 如果 `python-docx` / `pypdf` / `openpyxl` 没装，直接返回 FAILURE 而不是崩溃 | 各解析函数开头的 `try/except ImportError` |

> **机构名不推断**：解析器不根据文件名猜测机构名（`_guess_institution` 函数已删除）。机构名由开发者通过产品需求文档或调用方明确指定。文档块中的 `institution` 字段默认值为 `"unknown"`，会在下游 metadata 推断阶段根据文档内容（如在文本中发现 `AURORA_DEMO`）或产品需求文档中的明确定义来修正。

#### 官方知识拓展

**1. 文档解析的本质：非结构化 → 半结构化 → 结构化**

在 RAG 系统里，文档解析不是"读文件"这么简单。原始文档（PDF/Word/Excel）是非结构化的——文本流没有明确的语义边界。解析器的任务是把非结构化的比特流转成半结构化的"文档块列表"（每个块有类型标记、定位信息、元数据），为下游的向量检索提供可索引的语义单元。结构化那一步（提取字段映射、事件流）则留给 LLM 完成。

**2. PDF 解析的三种技术路径**

| 路径 | 原理 | 适用场景 | 局限 |
|---|---|---|---|
| **文本层提取** | PDF 内部有文字图层，pypdf 直接读取字符和位置 | 原生 PDF（Word 导出、LaTeX 生成） | 扫描件无文本层 |
| **OCR（光学字符识别）** | 把 PDF 页面渲染为图片，再用 OCR 引擎（Tesseract/PaddleOCR）识别文字 | 扫描件、纸质文档拍照 | 识别准确率受图片质量影响，中英混排容易出错 |
| **混合模式** | 先尝试文本层提取，失败了自动回退到 OCR | 批量处理不确定格式的文档 | 需要判断"失败"的标准（本项目用 `OCR_NEEDED` 状态标记） |

**3. ParseState.PARTIAL 为什么是"高级设计"而非"偷懒"**

很多 demo 项目只有"成功/失败"两种状态。但真实场景中，一份 20 页的 PDF 里 3 页是图片、17 页有文字层——直接报失败太粗暴（丢了 85% 的信息），假装成功又掩盖了问题。PARTIAL 状态让调用方可以**知情决策**：我到底要不要容忍这 15% 的缺失继续往下走？

#### 产品需求文档在本环节的角色

文档解析面向的是所有输入文件，不分“产品需求”还是“API 文档”。`fixtures/*产品接入需求说明书.md` 是 Markdown，由 `load_text_chunks()` 统一进入切块、向量化和检索；DOCX/XLSX API 文档由统一解析器转成标准块后进入同一链路。

---

### 第二块：文本切块（rag_model.py::split_text_into_chunks）

#### 概念
**文本切块（text chunking / chunking）** 就是把长文档切成一段段合适长度的小块（chunks），每一块是向量检索的最小索引单元。切得太短丢失上下文，切得太长淹没关键信息。这个"合适长度"是 RAG 系统里最影响效果的超参数之一。

#### 核心原理

**1. 滑窗式切分**（`rag_model.py` 第 192-233 行）

```python
MAX_CHUNK_CHARS = 900      # 每块最多 900 字
CHUNK_OVERLAP_CHARS = 120   # 前后重叠 120 字
```

切分过程是一个"滑动窗口"：每次切 900 字，下一次从 `end - 120` 的位置开始。为什么需要 overlap（重叠）？

举个例子：假设文档里有一句话被切在两块之间——

> 块 A 末尾："申请借款时需要传入 applyId，该字段由"
>
> 块 B 开头："授信查询接口的返回中获取。"

如果没有 overlap，检索"applyId 从哪里获取"时，无论命中 A 还是 B，都只能看到半句话。有了 120 字重叠，块 A 可能也带上了 "由授信查询接口的返回中获取"，信息就不会在 chunk 边界丢失。

**2. Chunk ID 的确定性生成**（`rag_model.py:89-90` + `rag_model.py:224-226`）

```python
chunk_seed = f"{document}|{locator}|{index}|{piece}"
chunk_id = f"chunk_{stable_hash(chunk_seed)[:24]}"  # SHA256 前 24 位
```

同一个文档+同一切片位置生成的 chunk_id 不变，这是**幂等索引**的基础——重复建库不会产生重复记录（`rag_index.py:108-125` 的 `uniquify_chunk_ids` 负责去重）。

**3. Metadata 推理**（`rag_model.py:147-189`）

切块时不光切文本，还要推断这次文本块的元数据——机构名、产品编码、操作类型（授信/用信/对账）、内容类型（字段映射/业务流程/配置项）。这些 metadata 不是从文档元数据直接拿的，而是**从内容本身用正则+关键词推断**的：

```python
# rag_model.py:174-175
funder_candidates = re.findall(r"\b[A-Z][A-Z0-9_]{2,}_DEMO\b", merged_text)
# 从文本里搜 "AURORA_DEMO"、"HUARONG_DEMO" 等模式
```

为什么不用文档级别的 metadata？因为一份 DOCX 可能包含多个接口、涉及多个机构——"华融消金 API 文档"的标题是华融，但内部可能引用了 Aurora 的字段命名。**以 chunk 内容为准推断 metadata 更准确**。

#### 具体用法

切块逻辑是被 `rag_index.py` 在索引构建时自动调用的，不需要单独运行。但理解参数含义很重要：

```bash
# 索引构建时切块自动执行
.venv/bin/python skill/integrate-financial-institution/scripts/rag_index.py \
  --input fixtures/synthetic_aurora_api_spec.md \
  --persist-dir generated/rag/chroma \
  --collection fund_demo \
  --output-dir generated/rag \
  --reset
# 输出: generated/rag/chunks.json 可以看到所有 chunk 的内容和 metadata
```

#### 生产级注意事项

| 事项 | 说明 |
|---|---|
| **chunk_size 不是越大越好** | 900 字是中文金融文档的实践经验值。太小（200）语义破碎，太大（2000）检索精度下降、LLM 上下文浪费 |
| **overlap 可调** | 120 字重叠 ≈ 900 字的 13%。如果文档段落结构清晰，可降低到 50；如果文档是流式叙述，可提高到 200 |
| **语义切块优于固定长度切块** | 生产级更好的做法是按段落/章节边界切，而不是硬切 900 字。这里用固定长度是做了"最小可行"选择 |
| **metadata 提取不能完全靠启发式** | 用正则从内容推断机构名/操作类型，虽然准确率还行但会漏。生产级建议用一个小模型专门做 chunk 级别的分类 |
| **重新切块 = 必须重建索引** | 因为 chunk_id 变了，旧向量还在库里；`--reset` 参数清空旧 collection |

#### 官方知识拓展

**1. Chunk 策略的分类（不仅是"大小"问题）**

| 策略 | 做法 | 优点 | 缺点 |
|---|---|---|---|
| **固定长度** | 硬切 N 个字符（如本项目 900 字） | 实现简单、确定性强 | 可能在句子中间切断 |
| **语义切块（Semantic Chunker）** | 计算相邻句子的 embedding 相似度，在"语义断层"处切分 | 保持语义完整 | 需要额外 embedding 计算开销 |
| **递归切块（Recursive Splitter）** | 先按段落分、超过阈值的再按句子分、还超的按字符分 | LangChain 默认策略，平衡性最好 | 对表格/代码块可能不友好 |
| **文档结构感知切块** | 按原文档的章节/标题层级切分 | 最佳的语义保真度 | 需要文档有清晰结构标记 |

**2. Chunk 大小与检索效果的 trade-off（权衡）**

Chunk 太小（200 字）：检索精度高（命中的片段很聚焦），但可能丢失上下文——"applyId 由授信查询接口的返回中获取"这句话如果被切成两块，单块看不到完整信息。

Chunk 太大（2000 字）：上下文完整，但检索精度下降——一块里可能包含授信、用信、对账三个不相关话题，命中"授信查询"时也附带了一大段对账配置的噪音，浪费 LLM 的 token（计费单元）。

**经验规律**：中文金融文档的 sweet spot 通常在 500-1000 字（本项目选 900）。代码类文档要更短（300-500），叙事性文档可以更长（1000-1500）。

**3. 产品需求文档的 chunk 特点**

合成产品需求说明书是结构良好的 Markdown——有标题层级、表格和编号列表。`load_text_chunks()` 优先按标题保留章节边界，仅对超长块继续切分；这比无结构的固定长度硬切更能保持语义边界。

---

### 第三块：向量化（embedding_provider.py）

#### 概念
**文本向量化（text embedding / 向量化）** 就是把一段文本转成一个固定长度的浮点数数组（向量），使得"语义相近的文本，向量在数学空间里的距离也近"。这是 RAG 系统能从海量文档里找到相关内容的核心技术。

#### 核心原理

**1. 单一 Provider 架构**（`embedding_provider.py:18-31`，重构后仅保留 sentence-transformers，已删除 hash 回退 / mock 替代）

```python
class EmbeddingProvider(Protocol):
    provider: str
    model: str
    dimension: int   # 向量维度——关键约束！
    normalize: bool  # 是否做 L2 归一化——索引和检索必须一致！
```

只有一个 provider（提供者）：
- **sentence-transformers**：加载 `BAAI/bge-small-zh-v1.5`，512 维真实语义向量。这是唯一的 embedding 方案，没有 hash 回退或 mock 替代。

**2. 真实 embedding 实现**（`embedding_provider.py:69-101`）

```python
class SentenceTransformersEmbeddingProvider:
    def embed_batch(self, texts):
        vectors = self._model.encode(
            texts,
            normalize_embeddings=self.normalize,   # L2 归一化
            convert_to_numpy=True,
        )
        return [[float(v) for v in row] for row in vectors]
```

这里的关键点：
- `normalize_embeddings=True` → 所有向量被归一化到单位长度，余弦相似度 = 内积距离
- `convert_to_numpy=True` → 返回 numpy 数组，再用 Python 标准 `float()` 转换，保证可序列化
- 在 `__init__` 时就调用 `get_embedding_dimension()` 获取维度，**不信任默认值**

**3. 索引与检索的一致性守卫**（`rag_retrieve.py:67-77`）

```python
if any(
    metadata.get(key) != expected_embedding_meta[key]
    for key in ("embedding_provider", "embedding_model",
                "embedding_dimension", "embedding_normalize")
):
    raise ValueError(
        "retrieved chunk embedding config does not match query embedding config"
    )
```

这是**生产 RAG 体系里最容易踩的坑**：索引阶段用的是 bge-small 512 维 + L2 归一化，查询阶段不小心换了模型或关掉了归一化 → 向量不在同一个空间里 → 距离比较毫无意义。这段代码在检索时就做校验，发现了直接报错而不是默默返回垃圾结果。

#### 具体用法

```bash
# 使用 bge-small 真实 embedding 索引（默认行为）
.venv/bin/python evals/run_rag_pipeline.py

# 禁用归一化（一般不要改，除非你清楚后果）
# --no-normalize-embedding
```

#### 生产级注意事项

| 事项 | 说明 |
|---|---|
| **换模型 = 必须重建索引** | 不同模型维度不同（bge-small 512、bge-large 1024），向量空间完全不一样 |
| **归一化开关必须一致** | 开启归一化后距离在 [0,2] 区间；不归一化距离范围不可控 |
| **embedding 元数据写入每个 chunk** | `embedding_metadata()` 返回的 provider/model/dimension/normalize 四项配置写入每个 chunk（`rag_index.py:168-169`），检索时逐条比对 |
| **512 维是中文场景的经验值** | 维度太小语义表达能力弱，太大计算和存储都贵。BAAI bge 系列 512/768/1024 三档，512 对 demo 够用 |

#### 官方知识拓展

**1. Embedding 模型选型：开源 vs 商业 API**

| 维度 | 开源模型（BGE/M3E/text2vec） | 商业 API（OpenAI text-embedding-3/Cohere） |
|---|---|---|
| **部署** | 本地加载，需要 GPU 或 CPU 推理 | 调用 API，无部署成本 |
| **成本** | 一次硬件投入 + 推理时间 | 按 token 收费，量大时费用高 |
| **可控性** | 完全可控，模型固定不漂移 | 模型可能升级导致向量空间变化 |
| **中文支持** | BGE（智源）/ M3E（Moka）专为中文优化 | OpenAI/Cohere 中文能力不如英文 |
| **适用场景** | 内网、合规要求高、数据不能出域 | 快速原型、小规模、数据不敏感 |

**2. 向量维度与语义表达力的关系**

512 维向量 = 文本的语义被压缩到 512 个浮点数里。这是信息压缩，不是无损编码——维度越小，信息丢失越多。但维度也不是越大越好：BGE-large 的 1024 维在检索精度上比 BGE-small 的 512 维高约 3-5%，但存储和计算成本翻倍。选择维度的经验法则是：在满足检索精度要求的前提下，选最小的维度。

**3. 多语言 Embedding 的坑**

中文 embedding 面临一个特殊问题：中英混合文档。如果 chunk 里既有"授信申请"又有"credit_apply"，embedding 模型需要同时理解中英文。BGE 系列是多语言模型（中英文都训过），但如果你只用中文模型（如 text2vec-base-chinese），英文部分会被当作无意义的 token 处理，检索质量会显著下降。

对于本项目：产品需求文档是纯中文，但机构 API 文档里常见英文字段名（如 `applyId`、`requestNo`）。使用多语言 embedding 模型不是"加分项"而是"必需品"。

---

### 第四块：向量检索（rag_retrieve.py + rag_pgvector_retrieve.py）

#### 概念
**向量检索** 就是用用户的问题（查询文本）去向量数据库里搜"语义最相近"的文档片段。它不是关键词匹配——"借款申请"能搜到"贷款提交"，这不是字符串匹配能做到的，是因为它们的向量在高维空间里靠得近。

但 RAG 检索不是简单的"搜一下"，而是一个**多步骤的管道**：

```
用户查询 → embedding(查询) → metadata 过滤 → 向量距离计算 → Top-K 排序 → 距离阈值过滤 → accepted_evidence
```

#### 核心原理

**1. metadata filter（元数据过滤）在 Top-K 之前**（`rag_retrieve.py:50-56`）

```python
result = collection.query(
    query_embeddings=[query_embedding],
    n_results=top_k,        # 先限定 Top-K
    where=where or None,    # ← metadata filter 在这里，不是事后过滤
    include=["documents", "metadatas", "distances"],
)
```

这是故意的设计决策：**先过滤再检索**。如果反过来——先查全库 Top-K 再按 metadata 过滤——可能发生：如果 `institution=NOT_EXISTS` 这个机构在库里一篇文档都没有，全库 Top-K 返回了 12 条其他机构的内容，你在应用层把它全过滤掉 → 结果为空。但更危险的是，你拿到了 12 条不相关机构的"看起来像"的内容作为证据给了 LLM，LLM 会基于这些"幻觉证据"编造答案。

正确做法的代价是：metadata filter 把搜索范围缩小到某个机构后，如果该机构文档太少，可能 Top-K 返回不足 K 条。但这正是期望行为——"没有找到"比"基于错误的找到编造答案"好得多。

**2. 距离阈值过滤**（`rag_retrieve.py:88-99`）

```python
if distance <= max_distance:
    accepted.append(AcceptedEvidence(...))
```

Top-K 返回的是"最像的 K 条"，但不代表它们都"足够像"。一个距离 1.8 的 chunk 可能跟查询毫无关系，只是因为没有更相关的才被塞进 Top-K。`max_distance`（最大距离）阈值做**二次筛选**，只有距离 ≤ 阈值的才进入 `accepted_evidence`。

**3. 空证据保护**（`rag_retrieve.py:155-157`）

```python
if args.fail_on_empty and not accepted:
    print("ERROR: no accepted evidence after distance threshold filtering")
    return 2  # 特殊退出码，区别于一般错误
```

如果阈值过滤后 `accepted_evidence` 为空 → 意味着没有任何证据支持回答这个问题 → **应该阻断，不应该继续调用 LLM**。这是防止 LLM 在无证据的情况下"凭空编造"（幻觉 / hallucination）的最后一道防线。

**4. pgvector 版本的额外能力**（`rag_pgvector_retrieve.py`）

pgvector 版本比 Chroma 版本多了完整的**检索审计链**：
- `retrieval_runs` 表：记录每次检索的查询文本、过滤条件、embedding 配置（第 87-107 行）
- `retrieved_candidates` 表：记录每条候选的 chunk_id 和距离（第 123-129 行）
- `accepted_evidence` 表：记录通过阈值的证据（第 141-147 行）

这相当于每次检索都有"办案记录"，可以回溯"当时 LLM 看到了什么证据、为什么采纳/拒绝了某条"。

#### 具体用法

```bash
# Chroma 检索
.venv/bin/python skill/integrate-financial-institution/scripts/rag_retrieve.py \
  --persist-dir generated/rag/chroma \
  --collection fund_demo \
  --query "AURORA_DEMO 的授信接口请求字段映射" \
  --where '{"institution":"AURORA_DEMO"}' \
  --top-k 12 \
  --max-distance 0.85 \
  --output-dir generated/retrieve_test \
  --fail-on-empty

# pgvector 检索（需要 PostgreSQL + pgvector 运行中，端口 55432）
.venv/bin/python skill/integrate-financial-institution/scripts/rag_pgvector_retrieve.py \
  --database-url "postgresql://fund_demo:fund_demo_password@localhost:55432/fund_integration" \
  --collection fund_integration_main_pgvector_demo \
  --query "抽取 AURORA_DEMO 配置项和跨接口依赖" \
  --where '{"institution":"AURORA_DEMO"}' \
  --top-k 32 \
  --max-distance 2.0 \
  --output-dir generated/retrieve_pg_test \
  --fail-on-empty
```

#### 生产级注意事项

| 事项 | 说明 |
|---|---|
| **filter 顺序必须正确** | metadata filter 在前（限定搜索空间），Top-K 在后（排序）。反过来会导致过滤掉所有结果或引入污染 |
| **阈值不是固定常数** | 0.85（cosine）适用于 bge-small 归一化后的向量空间。换模型/维度后阈值必须重调 |
| **fail_on_empty 是安全机制** | 生产上无证据时不应调 LLM；可以改为返回预置的"无法回答"模板 |
| **Chroma 适合 demo、pgvector 适合生产** | Chroma 是纯文件级向量库，没有 SQL 审计能力；pgvector 的检索审计表是企业级合规的基础 |
| **Top-K 不是越大越好** | K 越大 → 检索的噪音越多、LLM 上下文越长（可能超限或浪费 token）。一般 8–32 之间调试 |

#### 官方知识拓展

**1. 相似度度量——归一化后的等价关系**

当向量做了 L2 归一化后，三种常见的距离度量在数学上是等价的：
- **余弦相似度（cosine similarity）** = `1 - 余弦距离`，衡量两个向量的方向是否一致
- **欧氏距离（Euclidean distance）** = 两点间的直线距离。归一化后 `||a-b||² = 2(1-cos(a,b))`
- **内积（dot product / inner product）** = 归一化后 `a·b = cos(a,b)`

所以当你在 Chroma 里设置了 `hnsw:space: cosine` 且向量都归一化后，本质上就是在做余弦相似度比较。如果忘了归一化，这三个度量方式就不再等价，出现"cosine 距离近但内积远"的矛盾现象。

**2. 向量索引算法概述**

| 算法 | 原理 | 适用规模 | 本项目使用 |
|---|---|---|---|
| **暴力搜索（Flat）** | 逐个比较所有向量 | < 10 万条 | 无 |
| **IVFFlat** | 先聚类再在最近的几个簇里搜索 | 10 万–100 万 | pgvector 支持 |
| **HNSW** | 多层可导航小世界图，近似最近邻 | 百万级 | **Chroma 默认 HNSW**，pgvector 也支持 |

Chroma 底层用 HNSW（Hierarchical Navigable Small World）。pgvector 不自动建向量索引——必须显式 `CREATE INDEX ... USING hnsw`（或 `USING ivfflat`）选择算法；不建索引则走精确暴力搜索（本项目几千条 chunk 完全够用）。百万级规模时，HNSW 查询快（毫秒级）、建索引慢；IVFFlat 建索引快、查询稍慢于 HNSW。

**3. 混合检索：向量 + 关键词（BM25）的互补**

向量检索擅长"语义相近"（"借款"能搜到"贷款"），但会漏掉精确匹配（搜"AURORA_DEMO"可能找不到这个精确的机构编码，因为 embedding 模型把它当成普通文本而非标识符）。关键词检索（BM25，一种基于词频的全文检索算法）擅长精确匹配但不懂语义。

生产级 RAG 常用**混合检索**：同时做向量检索和关键词检索，把两个结果列表按某种策略合并（RRF 融合 / 加权合并）。本项目没有实现，但如果面试被问到"你的项目有什么可以改进的"，这是一个很好的答案。

#### 产品需求文档在检索中的特殊价值

检索"事件流和跨接口依赖"时，最相关的证据往往来自产品需求文档而非机构 API 文档——因为产品需求文档明确写了"CQRS 事件流：credit_init → query_credit → 保存 applyId → loan_init → apply_loan"。API 文档只提供接口级别的字段描述，不提供"这几个接口之间有什么关系"的全局视角。如果检索时没有命中产品需求文档中的事件流描述，LLM 抽出来的 event_flows 就会缺少跨阶段依赖——这正是很多 RAG demo 看起来"很厉害"但实际不可用的原因。

---

### 第五块：LLM 结构化抽取（llm_extract_integration_spec.py）

#### 概念
把大语言模型（LLM，Large Language Model）当"结构化信息抽取器"用：喂给它一堆经过检索筛选的文档证据，让它按**预定义的 JSON 结构**（JSON Schema）抽取出机构信息、事件流、字段映射、配置项、跨接口依赖等内容，并强制每条结论都要带 `evidence`（证据）——引用原文的文档名、定位和原文摘录。

#### 核心原理

**1. JSON Schema 作为"抽取契约"**（`llm_extract_integration_spec.py:40-234`）

这是一份 200 行的 JSON Schema，定义了抽取结果的**完整结构**。关键设计：

- **status 三态**：每条业务结论的状态只能是 `candidate`（候选）/ `approved`（已批准）/ `unresolved`（未解决）。LLM **不能自己批准自己的判断**，默认全部 `candidate`。这在系统提示词（system prompt）里也强调了一遍（第 275 行）。
- **evidence 溯源**：每个业务对象都嵌入了 `evidence` 子对象（`document` + `locator` + `quote`），强制 LLM 引用原文。
- **strict: true**：拒绝 Schema 之外的字段，防止 LLM 自由发挥加字段。
- **required 字段**：机构、版本、运行时绑定、事件流、操作、变量、映射、跨阶段依赖、待确认问题——10 个顶层字段全部必填。

**2. 系统提示词（system prompt）的精炼设计**（第 254-260 行）

```python
system_prompt = (
    "你是金融机构资金网关 Java SPI 接入分析助手。"
    "你的任务是从产品需求说明书和机构 API 文档中抽取结构化接入说明书。"
    "只能根据输入文档回答；不确定的内容必须标记 unresolved。"
    "所有业务事实必须带 evidence（证据）对象。"
    "生成 Java 代码不是你的职责，你只输出 JSON。"
)
```

这 5 句话每句都有具体作用：
1. **角色定义**：限定专业范围，减少无关发挥
2. **任务明确**：抽取接入说明书，不是写代码/分析/总结
3. **证据约束**：不能基于训练数据"知道"，只能基于输入的文档
4. **溯源要求**：每条事实带证据
5. **边界划定**：你不是代码生成器，不要写 Java

**3. 防止幻觉的三层机制**

| 层 | 做法 | 位置 |
|---|---|---|
| Prompt 层 | "只能根据输入文档回答；不确定的内容必须标记 unresolved" | 第 257 行 |
| Schema 层 | 每条输出都强制带 `evidence`（文档+定位+原文） | JSON Schema `$defs` 里的 `evidence` 对象 |
| 调用层 | temperature=0（不随机），JSON Schema 约束，max_tokens=12000 | 第 314 行 |

**4. 不支持 mock 回退**（`main()` 函数末尾没有 mock 分支）

对比很多 demo 项目：如果 API key 没配就返回一段 mock JSON 继续跑。这个项目故意不这么做——`api_key` 为空时返回退出码 2 并报错（第 371-377 行）：
```python
if not api_key:
    print(f"ERROR: LLM_API_KEY or {api_key_env} is required ...", file=sys.stderr)
    return 2
```

#### 具体用法

```bash
# 需要先设置 DEEPSEEK_API_KEY 环境变量
export DEEPSEEK_API_KEY="sk-xxx"

.venv/bin/python skill/integrate-financial-institution/scripts/llm_extract_integration_spec.py \
  --input generated/v0.1/llm_input_context.md \
  --output generated/v0.1/integration_spec_candidate.json \
  --raw-output generated/v0.1/llm_raw_response.json \
  --provider deepseek
```

**两个输出文件**：
- `integration_spec_candidate.json`：抽取后的结构化 JSON
- `llm_raw_response.json`：LLM 的完整原始响应（含 token 用量、finish_reason 等）。**保留它是为了事后排查**——如果抽取结果有问题，可以回溯是 prompt/上下文导致的，还是 LLM 本身的问题。

#### 生产级注意事项

| 事项 | 说明 |
|---|---|
| **必须保留原始 LLM 响应** | 方便排查"是 prompt 写错了还是模型犯傻了" |
| **temperature=0** | 结构化抽取要确定性，不要创造性。非零温度会导致同一份输入两次抽取结果不同 |
| **上下文长度限制** | `MAX_DOCUMENT_CHARS = 24000`，超过就截断（第 247-249 行）。如果 evidence 太多，需要用更精确的检索减少输入 |
| **evidence.quote 不是可选项** | 它是"人工核对时对照原文"的唯一依据。没有 quote，审批人无法判断 LLM 的结论是否有根据 |
| **两阶段抽取 vs 一阶段** | 生产级更好的做法：先让 LLM 确认哪些字段是必填的、哪些接口存在，再让 LLM 填映射。本项目做了"一阶段"，但因为有 review_question 标记不确定项，算是打了补丁 |

#### 官方知识拓展

**1. LLM 结构化输出的三种技术方案**

| 方案 | 做法 | 本项目 |
|---|---|---|
| **JSON Mode** | prompt 里要求输出 JSON + `response_format: json_object` | ✅ DeepSeek 使用此方案 |
| **Function Calling / Tool Use** | 定义一个"函数"，LLM 输出函数调用的参数 JSON | 未使用 |
| **JSON Schema（严格模式）** | 定义完整的 JSON Schema，LLM 的输出被强制匹配 Schema | ✅ OpenAI 的 `json_schema` 模式（本项目代码里已兼容但实际未用 OpenAI） |

三种方案的控制力递增。JSON Mode 只是"保证输出是合法 JSON"，不保证字段名和类型正确。JSON Schema 模式可以定义 `additionalProperties: false`（拒绝额外字段）和 `required`（必填字段），控制力最强但并非所有模型都支持。

**2. Prompt Engineering 的几条硬原则**

本项目 system prompt（系统提示词，定义 AI 行为的指令）虽然只有 5 句话，但每条都体现了一条 prompt 工程原则：

| Prompt 语句 | 体现的原则 |
|---|---|
| "你是金融机构资金网关 Java SPI 接入分析助手" | **角色限定**：缩小 LLM 的行为范围，减少无关发挥 |
| "只能根据输入文档回答" | **知识边界**：阻止 LLM 使用训练数据中的"常识"代替文档事实 |
| "不确定的内容必须标记 unresolved" | **失败模式定义**：告诉 LLM"你不确定的时候该怎么办"，而不是让它猜 |
| "所有业务事实必须带 evidence 对象" | **输出约束**：强制结构化溯源 |
| "生成 Java 代码不是你的职责，你只输出 JSON" | **边界划定**：防止 LLM 自作主张"顺便写段代码" |

**3. 防止 LLM 幻觉（hallucination，大模型编造事实）的通用方法论**

| 策略 | 说明 | 本项目实现 |
|---|---|---|
| **证据锚定** | 输出必须引用输入文档 | JSON Schema 强制 evidence 字段 |
| **失败模式** | 不确定就说 unresolved | status 三态 + prompt 约束 |
| **低温推理** | temperature=0 减少随机性 | 硬编码 temperature=0 |
| **输出验证** | 抽取后做确定性校验 | validate_mapping.py 字段完整性 + 交叉引用 |
| **阻断机制** | 无证据时不调 LLM | `--fail-on-empty` |

---

### 第六块：审批闸门（当前契约派生 + 历史 M0 校验器）

> `validate_mapping.py --require-approved` 是历史 M0 结构的闸门示例；当前生成主链路使用候选/批准契约、`derive_code_model.py` 和 `validate_code_model.py`。不要用旧校验器证明当前契约可进入代码生成。

#### 概念
**审批闸门（approval gate / human-in-the-loop）** 是 LLM 抽取结果进入代码生成之前的**最后一道人工确认环节**。LLM 产出的 candidate spec（候选说明书）不是直接用的——它必须先通过结构校验，再经过人工签字确认每一项的状态，变成 approved spec（已批准说明书），才能进入 Java 代码生成。

#### 核心原理

**1. 两层验证模式**（`validate_mapping.py:67-71`）

```python
def validate_status(value, prefix, require_approved, errors):
    if value not in ALLOWED_STATUSES:      # 第一层：值是否合法
        errors.append(...)
    if require_approved and value != "approved":  # 第二层：是否需要已批准
        errors.append(f"{prefix}.status must be approved before generation")
```

`--require-approved` 是开关：
- **不传** = 只做结构校验（字段有没有、类型对不对），允许 status=candidate
- **传了** = "闸门落下"——任何 status 不等于 approved 的条目都会报错，阻断生成

这就是整个项目的"人工闸门"机制——不是靠流程文档描述的协议，而是**硬编码在生成代码之前的校验步骤里**。

**2. 确定性校验清单**（`validate_mapping.py:26-60`）

每类业务对象都有 defined（定义的）必填字段集合：

```python
REQUIRED_VARIABLE_FIELDS = {
    "name", "category", "required", "environment_specific",
    "used_by_operations", "validation_rule", "status", "evidence"
}
REQUIRED_MAPPING_FIELDS = {
    "operation", "mapping_direction", "platform_field",
    "institution_field", "transformation", "confidence",
    "status", "evidence", "risk", "review_question"
}
```

这些不是随便列的——它们对应 JSON Schema 里的 `required` 字段，但 **JSON Schema 在 LLM 调用时只是"建议"，LLM 可能产出缺失字段的 JSON**。这一层验证是第二道防线。

**3. 跨引用一致性校验**（`validate_mapping.py:148-149` + `validate_mapping.py:171-172`）

```python
# 变量引用的操作必须存在于 operations 列表中
if any(item not in operation_names for item in used_by_operations):
    errors.append(f"{prefix}.used_by_operations references unknown operation")

# 字段映射引用的操作必须存在
if mapping.get("operation") not in operation_names:
    errors.append(f"{prefix}.operation references unknown operation")
```

这是防止 LLM 自相矛盾：LLM 有时会在 `variables` 里引用一个 `operations` 里不存在的操作名，或者在 `mappings` 里引用不存在的操作。这些交叉引用校验是 AI 生成内容的质量保证。

**4. 禁止自由格式代码字段**（`validate_mapping.py:18-23`）

```python
FORBIDDEN_FREEFORM_CODE_FIELDS = {
    "transformation_code", "java_code", "script", "generated_code"
}
```

如果 LLM 在被要求"只输出 JSON"的情况下仍然忍不住写了代码块，这一条会拦住——确保 JSON 是纯数据描述，不是混入代码片段的"伪结构化"。

**5. 未解决值阻断**（`validate_mapping.py:24` + `validate_mapping.py:111-112`）

```python
UNRESOLVED_ROOT_VALUES = {"unknown", "unresolved", "待确认", "未解决", "n/a", "none"}

if str(document.get(field)).strip().lower() in UNRESOLVED_ROOT_VALUES:
    errors.append(f"{field} must be resolved before validation")
```

如果 `institution` 或 `document_version` 还是 "unknown"，整个文档直接拒绝。顶层字段必须是已解决的，不可能等人工确认时再填空。

#### 具体用法

```bash
# 第一步：结构校验（允许 candidate 状态）
.venv/bin/python skill/integrate-financial-institution/scripts/validate_mapping.py \
  generated/v0.1/integration_spec_candidate.json

# 第二步：历史 M0 的离线人工审批
# apply_review_decisions.py 读取 review_decisions.json，
# 把 status=candidate 的项目改成 approved 或 unresolved

# 第三步：闸门模式校验（拒绝任何非 approved 状态）
.venv/bin/python skill/integrate-financial-institution/scripts/validate_mapping.py \
  generated/v0.1/integration_spec_approved.json \
  --require-approved
```

#### 当前状态：已保留离线评审演进，但没有线上审批系统

当前事实应分三层说明：

- **历史 M0 闸门**：`validate_mapping.py --require-approved` 只校验旧结构，作为早期学习样例保留。
- **当前主链路**：`fixtures/恒誉消金待审核契约.json` 保存完整候选态，`fixtures/恒誉消金已批准契约.json` 保存离线人工修订后的批准态；`derive_code_model.py` 和 `validate_code_model.py` 是当前生成前闸门。
- **尚未实现**：审批 UI、登录身份、权限、通知和不可抵赖签名，因此不能把离线批准文件描述成完整线上审批系统。

**设计意图**：人拿到 candidate 契约后逐字段对照 evidence 原文，确认无误后改为 approved 并记录修订；任何 unresolved 或未批准项都不得派生 `code_model`。

#### 生产级注意事项

| 事项 | 说明 |
|---|---|
| **human-in-the-loop 不是可选项** | 金融场景里错误的字段映射可能导致资金损失，AI 不能自主决策 |
| **审批必须有审计记录** | approved 文件里的 `approval_audit` 对象记录谁在何时审批了什么范围 |
| **evidence.quote 是核定依据** | 审批人核对时，对照的就是 evidence 里的 `document+locator+quote`。没有 quote，审批无法进行 |
| **unresolved 与 candidate 的区别** | candidate 是"机器提议、等人批"；unresolved 是"机器也无法确定"——这两类处理方式完全不同 |
| **不要因为 LLM 自信度高就自动 approved** | 本项目系统提示词要求"默认使用 candidate 或 unresolved"，刻意阻止自动批准 |

#### 官方知识拓展

**1. Human-in-the-Loop 的三种实现模式**

| 模式 | 做法 | 适用场景 | 本项目 |
|---|---|---|---|
| **全自动** | LLM 输出直接进入下游 | 低风险场景（标签、摘要、翻译） | ❌ 不适用 |
| **抽样审核** | 随机抽查 N% 的结果 | 中风险、量大、人工来不及全审 | ❌ 不适用 |
| **全量审批** | 每一项都必须人工签字 | 金融、医疗、法律等高风险场景 | ✅ 设计意图如此 |

全量审批模式在本项目中体现为 `approval_audit` 对象：要记录审批人、审批时间、审批范围。这不仅仅是一个技术设计——在金融行业，如果一笔因映射字段写错导致的资金差错出了问题，审计会追溯"这个字段是谁批的、他对照了什么证据"。`evidence.quote` 就是那份"证据"。

**2. 审批效率与安全性的平衡**

全量审批看似安全，但代价是慢。如果 LLM 输出 200 条字段映射，人工逐条核对原文需要 2-4 小时。业界出现了一些平衡手段：
- **置信度分层**：LLM 自己标注每条结论的 `confidence`（置信度），审批人重点看低置信度的条目
- **规则自动审核**：对确定性规则（如"URL 必须以 https:// 开头"）自动通过，不浪费人力
- **差异对比审批**：如果同一家机构之前接入过，只审"与上次不一样"的部分

本项目在 `validate_mapping.py` 里预留了 `confidence` 字段（第 179-183 行校验它必须在 0.0-1.0 之间），但目前没有利用它做分层审批。这是一个有待开发的功能。

**3. 审批闸门不等于"人工审批"**

严格来说，本项目实现的是**审批闸门技术机制**，而不是完整的**人工审批流程**。差异如下：

- 技术闸门：`--require-approved` 开关 + 状态检查 → 阻止未签字的 spec 进入生成
- 审批流程：审批人拿到 candidate → 逐字段核对 → 填审批意见 → 签字放行

前者是确定性状态校验，后者涉及界面、通知、权限和审计等完整系统。当前项目已保留候选契约到已批准契约的离线人工评审产物，但没有审批 UI、身份认证或不可抵赖签名；不能把离线记录描述成线上审批系统。

---

## 第七块：向量数据库持久化（pgvector 方案）

> 这是之前文档的**重大遗漏**——前面的向量检索章节主要讲了 Chroma（文件级向量库），但项目里还有一套完整的 PostgreSQL + pgvector 持久化方案，包含了 Chroma 不具备的生产级能力：结构化建表、索引优化、检索审计。

### 为什么需要 pgvector？

Chroma 的存储是本地文件（`generated/rag/chroma/`），适合单机 demo，但缺乏：
- **SQL 级别的结构化查询**：无法用 `SELECT institution, COUNT(*) FROM knowledge_chunks GROUP BY institution` 看各机构文档量分布
- **检索审计**：谁在什么时候查了什么、结果是什么——Chroma 没有内置
- **事务一致性**：索引写入和元数据写入不是原子的
- **权限控制**：PostgreSQL 有完整的 RBAC（基于角色的访问控制）
- **持久化可靠性**：pgvector 数据在 PostgreSQL WAL（预写日志）的保护下，崩溃可恢复

### pgvector 方案的数据表设计

项目通过 `infra/pgvector/init.sql`（77行）定义了 5 张表：

#### 1. `rag_collections` —— 向量集合注册表

```sql
CREATE TABLE rag_collections (
    collection_name text PRIMARY KEY,
    embedding_provider text NOT NULL,   -- "sentence-transformers"
    embedding_model text NOT NULL,      -- "BAAI/bge-small-zh-v1.5"
    embedding_dimension integer NOT NULL, -- 512
    embedding_normalize boolean NOT NULL  -- 是否 L2 归一化
);
```

这张表是 pgvector 版的"embedding 一致性守卫"——**在数据库层面记录**每个 collection 的 embedding 配置。检索时（`rag_pgvector_retrieve.py:60-71`），先查这张表拿索引时的配置，和查询时的配置逐项比对，不一致直接报错。

这比 Chroma 版本更强：Chroma 的配置校验是在检索时逐 chunk 比对 metadata（`rag_retrieve.py:67-77`），pgvector 版本是先查 collection 注册表做**一次全局校验**，再做逐 chunk 的二次校验。双重保险。

#### 2. `knowledge_chunks` —— 核心知识块表

```sql
CREATE TABLE knowledge_chunks (
    chunk_id text PRIMARY KEY,
    collection_name text NOT NULL REFERENCES rag_collections(collection_name),
    embedding vector NOT NULL,          -- pgvector 类型，存储 512 维向量
    metadata jsonb NOT NULL,            -- JSONB 格式的完整元数据
    institution text NOT NULL,          -- 机构名（反范式化到独立列，方便建索引）
    operation text NOT NULL,            -- 操作名
    content_type text NOT NULL,         -- 内容类型
    ...
);
```

关键设计决策：

**① `embedding` 列用 pgvector 的 `vector` 类型而非 `double[]`**

pgvector 不是 PostgreSQL 的内置功能，而是一个 C 扩展（extension，数据库的功能插件）。它定义了 `vector` 类型，支持专门的距离运算符：
- `<->`：L2 距离（欧氏距离）
- `<=>`：余弦距离
- `<#>`：负内积（返回值越小，即越接近 -1，越相似）

安装方式：`CREATE EXTENSION vector;`（需要 DBA 权限，见交接文档第 9 节）。

**② 元数据双轨制：`metadata jsonb` + 独立列**

同一个信息存了两份：完整元数据在 `metadata` 列（JSONB 格式，灵活但查询慢），高频过滤字段（institution、operation 等）在独立列上（可以建 B-tree 索引，查询快）。这是典型的**读优化**设计——牺牲一点存储空间换取过滤查询的速度。

```sql
-- 独立列有索引 → 查询快
CREATE INDEX idx_knowledge_chunks_institution ON knowledge_chunks(institution);

-- JSONB 内部字段也有索引 → 灵活性
CREATE INDEX idx_knowledge_chunks_metadata ON knowledge_chunks USING gin(metadata);
```

#### 3. 检索审计三张表

```sql
retrieval_runs       -- 每次检索的完整记录（查询文本、过滤条件、embedding 配置）
retrieved_candidates -- 每条候选 chunk（排名、距离）
accepted_evidence    -- 通过阈值的证据（证据编号、chunk_id）
```

三表关系：`retrieval_runs 1:N retrieved_candidates 1:N accepted_evidence`，通过 `run_id` 外键级联。这意味着任意一次历史检索都可以完全回溯——"当时 LLM 看到的证据是哪几条"。

### 索引写入的幂等性设计

`rag_pgvector_index.py` 第 46-133 行的 `index_chunks()` 使用 `ON CONFLICT ... DO UPDATE`：

```sql
INSERT INTO knowledge_chunks (...) VALUES (...)
ON CONFLICT (chunk_id) DO UPDATE SET  -- 如果 chunk_id 已存在，更新而非报错
    content = EXCLUDED.content,
    embedding = EXCLUDED.embedding,
    ...
```

这意味着**重复建库不会产生重复记录**。同一个文档多次索引，chunk_id 不变（确定性哈希），第二次执行时 SQL 自动更新已有记录而不是插入新行。这是生产环境的必要特性——索引脚本可能因网络抖动重跑，不能产生脏数据。

### pgvector vs Chroma 选型对比

| 维度 | Chroma | pgvector | 本项目使用 |
|---|---|---|---|
| **存储方式** | 本地文件（SQLite + Parquet） | PostgreSQL 表 | 两者兼具 |
| **检索方式** | Python API | SQL + pgvector 运算符 | 两者兼具 |
| **审计能力** | 无内置 | 完整审计表（3张） | pgvector ✅ |
| **SQL 查询** | 无 | 完整 SQL（GROUP BY/JOIN/子查询） | pgvector ✅ |
| **部署复杂度** | pip install 即用 | 需要 PostgreSQL + pgvector 扩展 | pgvector 更复杂 |
| **适用场景** | 快速原型、单机 demo | 生产环境、多用户、需审计 | Chroma=快速验证，pgvector=生产演示 |

---

## 总（二）：测试练习与面试模拟

以下练习题覆盖全部 7 块内容的核心概念、原理分析、实际应用和生产排查。**建议先通读上面"分"部分和源码，再做以下题目，效果最佳。**

### 一、核心概念理解题

#### Q1: 简述 ParseState 四种状态的业务含义，并举例说明每种状态对应的典型场景。

<details>
<summary>参考答案</summary>

- **SUCCESS**：所有内容成功提取。例如一份纯文本 PDF，每页都有文字层。
- **PARTIAL**：部分内容提取失败但仍可用。例如 PDF 里 3/6 页有文本、另外 3 页是扫描件。系统的处理方式是标记 PARTIAL，由用户决定 `--allow-partial-parse` 是否放行。
- **FAILURE**：完全无法解析。例如文件格式损坏、依赖库未安装。
- **OCR_NEEDED**：无文本层，需要 OCR。典型场景是扫描版 PDF 或手机拍摄的文档照片。

</details>

#### Q2: 解释 "retrieved_candidates ≠ accepted_evidence" 的含义，以及为什么不等价是很重要的工程约束。

<details>
<summary>参考答案</summary>

- `retrieved_candidates`：向量库返回的 Top-K 个距离最近的 chunk，无论距离多远。
- `accepted_evidence`：从候选里筛选出距离 ≤ 阈值的部分。

为什么不能等价：如果直接把 Top-K 全部喂给 LLM，可能 K 条里有 8 条与查询无关（只是因为库里没有更相关的内容才被塞进来），这 8 条就是噪音。LLM 基于噪音生成答案 = 幻觉。阈值过滤的作用就是"只说你知道的，你不太确定的别乱说"。

工程意义：如果 accepted_evidence 为空，应该阻断（`--fail-on-empty`），而不是继续调用 LLM 让它凭空编造。

</details>

#### Q3: 项目中 embedding 的 normalization（归一化）为什么要索引和检索阶段保持一致？不一致会有什么后果？

<details>
<summary>参考答案</summary>

归一化 = 把向量的 L2 范数缩放到 1，使所有向量落在同一个超球面上，此时余弦相似度等于内积。

索引归一化但检索不归一化：检索向量的模长不同于索引向量，距离计算不再等于余弦相似度，阈值失去意义。

索引不归一化但检索归一化：同理，空间不对齐。

工程保障：每个 chunk 的 metadata 里都记录了 `embedding_normalize: true/false`，检索时逐条校验，一旦不一致直接报错（`rag_retrieve.py:67-77`）。

</details>

### 二、原理深度分析题

#### Q4: 为什么 metadata filter 必须在 Top-K 检索之前执行，而不是在检索之后过滤结果？设计一个反例说明先检索后过滤的问题。

<details>
<summary>参考答案</summary>

**反例场景**：假设知识库有 5 家机构的文档，用户查询"华融消金的授信接口"，但华融的文档因 chunk 质量差（或索引时没加入），在库里占比很低。

- **先检索后过滤**：全库 Top-K=12 → 返回 12 条（其中大部分是 Aurora 等无关机构的内容）→ 应用层按 `institution=华融` 过滤 → 仅剩 1 条或 0 条。如果剩 1 条，丢了 11 条本来如果有其他华融 chunk 会被召回的；如果剩 0 条，什么都没得到。
- **先过滤后检索**：先限定搜索空间为 `institution=华融` → 在这个子空间里做 Top-K=12 → 如果华融 chunk 不足 12 条，返回实际条数。如果为 0，系统明确知道"没搜到"而不是"搜到了但被过滤掉了"。

更严重的版本：如果应用层忘记过滤，LLM 会收到其他机构的"授信接口"文档作为证据，产出一份**看起来像华融但实际是 Aurora 的授信说明书**——这是生产上不可接受的错误。

</details>

#### Q5: Chunk overlap（文本重叠）设置为 0 会有什么问题？给出一个具体的检索失败案例。

<details>
<summary>参考答案</summary>

假设一段文档为：

> "申请借款时需要传入 applyId 参数。该参数由授信查询接口的返回中获取，存储在跨阶段上下文字段中，在下一次调用借款申请接口时作为必填参数传入。"

overlap=0 时切分为：
- 块 A：`...申请借款时需要传入 applyId 参数。该参数由授信查`
- 块 B：`询接口的返回中获取，存储在跨阶段上下文字段中...`

检索"applyId 从哪里获取"时：
- 命中块 A → 看到 `该参数由授信查`，不完整
- 命中块 B → 看到 `询接口的返回中获取`，不知道主语是 applyId

如果 A 和 B 都没被同时检索到 → 无论命中哪块，都丢失了完整语义。

overlap=120 时：
- 块 A：`...申请借款时需要传入 applyId 参数。该参数由授信查询接口的返回中获取，存储在跨阶段上下文字段中...`（结尾多 120 字）
- 块 B 开头也有 120 字重叠 → 两条都能看到完整句子

</details>

#### Q6: 解释项目中的三层"防幻觉"机制，并说明每一层阻止的是什么类型的幻觉。

<details>
<summary>参考答案</summary>

| 层 | 位置 | 阻止的幻觉类型 |
|---|---|---|
| **Prompt 层** | system prompt 第 3 句："只能根据输入文档回答；不确定的内容必须标记 unresolved" | LLM 基于训练数据的"我知道"幻觉（脱离输入文档自由发挥） |
| **Schema 层** | JSON Schema 强制 `evidence` 字段（document+locator+quote） | LLM 产出无来源的"看起来正确"的结论 |
| **调用层** | temperature=0 + JSON Schema strict 模式 + `--fail-on-empty` | 两次抽取不一致 + 输出包含 Schema 外字段 + 无证据继续生成 |

</details>

### 三、实际应用场景题

#### Q7: 假设你要新增一家合成机构，描述从文档到 approved 契约的完整操作步骤。

<details>
<summary>参考答案</summary>

**需要的输入文档**：
1. 产品需求说明书（描述要对接哪些接口：授信/用信/还款/对账）
2. 合成 API 接口文档（每个接口的请求/响应字段、URL、认证方式）
3. 两者可以合并为一个文档，也可以是独立的

**操作步骤**：
1. 把合成文档放在 `fixtures/` 下，并登记 `fixtures/manifest.yaml`
2. 运行 `rag_index.py` 建索引（切块→embedding→向量入库）
3. 运行 `rag_retrieve.py` 检索，使用与文档元数据一致的机构/产品/版本过滤，拿到 `accepted_evidence`
4. 运行 `llm_extract_integration_spec.py`，输入 `llm_input_context.md`，产出 `integration_spec_candidate.json`
5. 对候选契约做结构和证据引用校验
6. **逐字段核对** candidate spec 里的每个字段映射、必填变量、事件流，对照 evidence.quote 里的原文
7. 所有确认无误的项状态改为 approved，不确定的标 unresolved，填写 `approval_audit` 审批记录
8. 运行 `derive_code_model.py` 和 `validate_code_model.py`，确认所有进入生成的项均已批准且引用一致
9. approved 契约派生并校验 `code_model`，再进入 LLM 直写和方法级追溯验证

</details>

#### Q8: 如果 pgvector 检索时 `accepted_evidence` 始终为空，但你知道库里确实有相关文档，可能的原因有哪些？逐一排查。

<details>
<summary>参考答案</summary>

排查清单（按可能性从高到低）：

1. **max_distance 阈值太严格**：用 `rag_retrieve.py` 不带 `--max-distance` 跑一次，看实际距离值分布，调高阈值
2. **metadata filter 条件错误**：查询里的机构、产品或版本与索引元数据不一致
3. **embedding 模型不匹配**：索引和检索用了不同的 embedding 模型（如 bge-small vs bge-large）→ 维度不同或向量空间不同，报错或距离不可比
4. **归一化不一致**：索引归一化了，检索没归一化 → 距离值无意义
5. **查询文本与文档语言不同**：文档是中文，查询是英文 → embedding 模型的语言理解范围不匹配
6. **chunk 切分过碎**：900 字切成 3 块 300 字 → 语义碎片化，距离值普遍偏高
7. **pgvector extension 未安装或版本不对齐**：`CREATE EXTENSION vector` 失败 → 建库失败但没有明显报错

</details>

### 四、生产环境问题排查题

#### Q9: 某次 LLM 抽取产出的 `integration_spec_candidate.json` 中，所有 `mappings[].mapping_direction` 都写成了 `"platform_to_institution_request"`，但实际上返回报文也应该有映射。这可能是什么问题？如何修复？

<details>
<summary>参考答案</summary>

**可能的原因**：
1. LLM 系统提示词里写了方向要求但没强调"两个方向都要填"
2. 输入的 evidence 中只包含了请求报文的字段信息，没有包含返回报文的字段信息 → LLM 没有证据填写返回映射
3. JSON Schema 定义了三个方向（第 173 行 `platform_to_institution_request` / `institution_to_platform_response` / `institution_to_platform_callback`），但 LLM 倾向于只用第一个

**修复方法**：
1. 检查 `accepted_evidence` → 确认返回报文字段信息是否被检索到
2. 如果没有，调整查询文本或放宽阈值，确保返回报文相关内容也被召回
3. 如果有但在 context 里靠后，调整 `write_llm_context()` 里的排序策略，确保两个方向的证据均匀分布
4. 在 system prompt 里显式强调："请求映射和返回映射都需要抽取，缺失任意方向应标记 unresolved"

</details>

#### Q10: 你发现某次文档解析后，XLSX 文件中的表格数据丢失了包含"密码"、"密钥"相关列的信息。分析这是 bug 还是 feature，并说明正确的处理方式。

<details>
<summary>参考答案</summary>

这不一定是 bug——Excel 解析（`unified_parser.py:246-304`）是逐行读取 `ws.iter_rows(values_only=True)`，理论上不会主动丢弃任何列。

但如果"密码"、"密钥"相关的列内容实际为空（Excel 里合并单元格、空行、或格式问题导致 openpyxl 读到的 value 是 None），解释器跳过了空字符串（第 283-284 行 `if not row_text.replace(" | ", "").strip(): continue`），导致整行被丢弃。

**正确的处理方式**：
1. 空行丢弃是对的（无信息内容不应入库），但表头行不能丢
2. 如果密码列是第 3 列但实际值为空（因为本行属于其他列），这是数据本身的问题不是解析器的问题
3. 对敏感行（密钥、密码、证书）的正确做法是：**应该在脱敏层处理**，而不是在解析层丢弃。当前项目没有实现脱敏层，这是后续可以补的
4. 当前项目使用 synthetic（人造）数据，不存在真实密钥，所以这是合理的设计选择而非 bug

</details>

#### Q11: 如果要在生产环境中上线这个 RAG 链路，你会增加哪些监控指标？

<details>
<summary>参考答案</summary>

| 类别 | 指标 | 含义 |
|---|---|---|
| **检索质量** | retrieved_count (检索到的候选数) | 太低可能阈值太严或库内容不足 |
| **检索质量** | accepted_count (采纳的证据数) | 太低意味着检索到的内容相关性差 |
| **检索质量** | acceptance_rate (采纳率 = accepted/retrieved) | 反映检索精度 |
| **检索质量** | empty_result_rate (空结果率) | 过频=知识库覆盖不足或阈值太高 |
| **LLM 质量** | extraction_duration (抽取耗时) | LLM 调用延迟 |
| **LLM 质量** | token_usage (token 消耗) | 成本追踪 |
| **LLM 质量** | unresolved_rate (未解决率) | 过高=文档质量差或 LLM 能力不足 |
| **系统健康** | parse_failure_rate (解析失败率) | 文档质量监控 |
| **系统健康** | embedding_mismatch_count (向量配置不匹配次数) | 配置漂移告警 |
| **合规** | approval_queue_depth (待审批任务数) | 审批积压 |
| **合规** | human_overwrite_rate (人工改判率 = 审批人改了 LLM 结论的比例) | LLM 准确性监控 |

</details>

### 五、综合面试模拟题

#### Q12: 请用 3-5 分钟时间，概要介绍这个项目的完整技术链路、你在其中的角色、以及你从中学到的三个最重要的工程经验。

<details>
<summary>参考框架（不是标准答案，是思路框架）</summary>

**链路概述**（60 秒）：
这个项目针对金融机构接入时文档格式不一、字段映射易漏的问题，构建了工具链：文档统一解析 → 文本切块 → 向量化入库 → 检索与阈值过滤 → LLM 结构化抽取 → 离线人工审批 → `code_model` 派生 → LLM 直写完整 Java SPI → 方法级证据追溯 → Maven/契约/golden 验证。

**我的角色**（30 秒）：
我是这个项目的设计者和决策者。我定义了整条链路的架构、每层的数据进出格式、以及关键工程约束（如 metadata filter 必须在前、LLM 不能自我批准、candidate ≠ approved）。所有的 Java 背景（SPI 架构、字段映射方向）直接复用了工作经验。

**三个工程经验**（90 秒）：
1. **检索不等于采纳**：向量库返回 Top-K 只是"候选人"，真正给 LLM 的证据必须经过阈值过滤。如果跳过了这一步，LLM 会在不相关的文档片段上"编造"答案。这个不等式是 RAG 工程质量的核心约束。
2. **human-in-the-loop 必须硬编码**：不能靠"我们流程上规定要审批"——必须把审批闸门写成代码里不可绕过的校验步骤。LLM 可以自信，但人必须签字。
3. **embedding 的一致性是不可妥协的**：索引用了 bge-small 512 维+归一化，检索阶段换模型或关归一化，向量空间完全不同。这个项目在每个 chunk 的 metadata 里都写了 embedding 配置四项（provider/model/dimension/normalize），检索时逐条校验，不一致直接报错。

</details>

#### Q13（追问）: 你刚才提到 human-in-the-loop 是硬编码的，具体是哪段代码实现的？如果我现在给你一份 LLM 刚抽出来的 candidate spec，你能带我走一遍审批流程吗？

<details>
<summary>参考框架</summary>

- 当前生成闸门在 `derive_code_model.py` 和 `validate_code_model.py`；历史 M0 另有 `validate_mapping.py --require-approved`
- 流程：candidate 契约 → 逐条核对 evidence → 记录修订和批准元数据 → approved 契约 → 派生并校验 `code_model`
- 当前仓库保留了合成候选契约和离线人工修订后的 approved 契约；没有审批 UI、认证用户或线上签名

</details>

### 六、向量数据库与产品需求专项题

#### Q14: 产品需求文档和机构 API 文档在本项目的 RAG 链路中分别提供什么信息？如果缺少其中一类，对 LLM 抽取结果的影响分别是什么？

<details>
<summary>参考答案</summary>

**产品需求文档**（`fixtures/*产品接入需求说明书.md`）：提供接入逻辑——事件流编排、跨接口依赖、字段映射方向和环境配置项清单。

**机构 API 文档**（`synthetic_aurora_api_spec.md` 等）：提供"技术接口细节"——接口 URL、请求/响应字段名、数据类型、认证方式。

**缺少产品需求文档的影响**：LLM 只能抽出一堆零散的接口描述，不知道按什么顺序调用、哪个返回值要传给下一个接口。产出的 `event_flows` 字段可能是随机顺序或是 LLM 靠"常识"猜测的。

**缺少机构 API 文档的影响**：LLM 知道要做授信+用信+对账，但不知道每个接口的具体字段名和 URL。产出的 `mappings` 里 `institution_field` 可能是编造的——联调时全报 400。

</details>

#### Q15: Chroma 和 pgvector 分别适用于什么场景？本项目为什么同时保留两套实现？

<details>
<summary>参考答案</summary>

Chroma：本地文件级向量库，pip install 即用，零配置。适用于快速原型、单机 demo、不需要 SQL 查询的场景。

pgvector：PostgreSQL 扩展，需要安装 PostgreSQL + pgvector 扩展 + 建表。适用于生产环境、需要 SQL 查询（GROUP BY/JOIN）、需要检索审计、需要权限控制的场景。

**同时保留的原因**：
1. Chroma 跑验证更快（不需要起 PostgreSQL），开发迭代时用 Chroma
2. pgvector 展示生产级能力（审计表、SQL 查询、事务一致性），面试演示时用 pgvector
3. 验证脚本两种都覆盖（`run_rag_pipeline.py` + `run_pgvector_rag_pipeline.py`），确保两套都工作

这不是"做了两个重复的东西"，而是"快速验证用轻量方案，生产演示用重量方案"——和业界"dev 用 SQLite、prod 用 PostgreSQL"同理。

</details>

#### Q16: `knowledge_chunks` 表为什么要把 metadata 既放在 JSONB 列里又抽到独立列（如 institution）？这叫什么设计模式？

<details>
<summary>参考答案</summary>

这叫**反范式化（denormalization）**，是数据库在读性能上的常见优化。

JSONB 列的优点：灵活（任意结构）、不需要修改表结构就能存新字段。缺点：查询慢——`metadata->>'institution'` 需要解析 JSON 结构。

独立列的优点：可以建 B-tree 索引，`WHERE institution = 'AURORA_DEMO'` 走索引查询，毫秒级。缺点：每增加一个过滤维度就要加一列。

本项目的做法是**两全其美**——高频过滤字段（institution、operation、content_type）独立建列+索引，低频或新字段存在 JSONB 里。查询时优先用独立列的索引，JSONB 在需要时也可以走 GIN 索引（`idx_knowledge_chunks_metadata`）。

</details>

#### Q17: `ON CONFLICT (chunk_id) DO UPDATE` 在本项目中解决了什么问题？如果去掉这段逻辑，会发生什么？

<details>
<summary>参考答案</summary>

解决了**索引幂等性**问题——同一个文档多次索引不会产生重复记录。

如果去掉 `ON CONFLICT DO UPDATE`，直接用 `INSERT`：
- 第一次索引：插入 100 个 chunk，成功
- 第二次索引（比如因为参数调整重跑）：尝试插入同样的 100 个 chunk_id → PostgreSQL 报 `duplicate key value violates unique constraint` → 整个事务回滚 → 索引失败

有了 `ON CONFLICT DO UPDATE`：
- 第二次索引：遇到已存在的 chunk_id → 更新 content、embedding、metadata → 相当于"原地刷新"，不会出错

这在生产环境中很关键——索引脚本可能因为网络抖动、参数调整、数据更新而重跑，不能每次都手动 `TRUNCATE`（截断清空）全表。

</details>

---

## 附录：源码阅读索引

| 知识点 | 核心文件 | 行数 | 关键看点 |
|---|---|---|---|
| 文档解析 | `unified_parser.py` | 429 | ParseState 四状态、交错处理段落/表格 |
| 数据模型 | `parse_model.py` | 75 | DocumentBlock / DocumentLocator 定位模型 |
| 文本切块 | `rag_model.py:192-233` | 42 | 滑窗式切分、元数据推断、Chunk ID 确定性 |
| 向量化 | `embedding_provider.py` | 130 | 单一 provider（sentence-transformers）、归一化守卫、维度一致性 |
| 检索(Chroma) | `rag_retrieve.py` | 167 | metadata filter 顺序、阈值过滤、空证据保护 |
| 检索(pgvector) | `rag_pgvector_retrieve.py` | 220 | 检索审计表、embedding 配置校验 |
| pgvector 索引 | `rag_pgvector_index.py` | 189 | ON CONFLICT 幂等性、批量写入 |
| pgvector 建表 | `infra/pgvector/init.sql` | 77 | 5 张表、索引策略、外键级联 |
| pgvector 通用 | `pgvector_common.py` | 66 | vector_literal、过滤 SQL 构建 |
| LLM 抽取 | `llm_extract_integration_spec.py` | 410 | JSON Schema、三层防幻觉、不支持 mock 回退 |
| 生成前闸门 | `derive_code_model.py` + `validate_code_model.py` | — | approved 状态、引用和派生模型一致性 |
| 生成追溯 | `generation_trace.py` + `validate_generation_trace.py` | — | Java 方法、E/chunk、M 编号和源码 hash 一致性 |
| 主样例 | `fixtures/恒誉消金产品接入需求说明书.md` 等 | — | 三家合成机构、三种接入模式 |

---

> 初稿时间：2026-07-31；最近复核：2026-08-05
> 当前实现以项目仓库 `README.md`、`docs/交接文档-给Codex.md` 和实际测试脚本为准，不再固定“最新提交”哈希。
