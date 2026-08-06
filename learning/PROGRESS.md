# 学习进度总览（Learning Progress Overview）

> 最后更新：2026-08-06
> 说明：本文件为当前真实进度的快照，事实源为 `learning/week*/` 下的每日笔记与作品集仓库的提交记录。学习计划时间表（原 2026-06-01 起）已扩展为 2026-07-27 ～ 2026-09-15，按 `FULL_TIME_AI_CAREER_SPRINT.md` 执行。

## 当前状态

- **当前周次**：Week 7（2026-08-03 ～ 08-09），作品集一已按 RAG 工程学习 Demo 完成收尾验证，待审核提交
- **定位**：以 Java 工程经验为根基的 AI 大模型应用工程师（AI Application Engineer，大模型落地而非算法研究）
- **三条主线**：学习（高）／作品集（最高）／求职（高）

## 学习计划进度（按周）

| 周次 | 日期 | 主题 | 笔记 | 状态 |
|------|------|------|------|------|
| Week 1 (week1-python) | — | Python + FastAPI + AI API | day1–6（6 篇） | ✅ 完成 |
| Week 2 (week2) | — | LLM 基础 + Prompt Engineering | day8–13（6 篇） | ✅ 完成 |
| Week 3 (week3) | — | LangChain + Memory + Function Calling | day15–20（6 篇） | ✅ 完成 |
| Week 4 (week4) | — | Embedding + 向量数据库 + 微调入门 | day22–28（7 篇） | ✅ 完成 |
| Week 5 (week5) | — | RAG 基础 + 企业知识库 V1 | day29–33（5 篇） | ✅ 完成 |
| Week 6 (week6) | 7.27–8.2 | RAG 全链路 + 结构化抽取 + 最小纵向闭环 | day36 / 41 / 42（3 篇） | ✅ 完成 |
| Week 7 (week7) | 8.3–8.9 | 作品集一：RAG 量化评测、混合检索、证据追溯与如实收尾 | Day 45 笔记；作品集当前改动已验证、待审核提交 | ✅ 完成 |
| Week 8 (week8) | 8.10–8.16 | Agent 最小闭环 + 首批投递（8.12） | 线上 0/7 topics | 🔵 已提前激活，课程任务未完成 |
| Week 9–12 | 8.17–9.15 | 智能守护、面试冲刺、Offer 冲刺 | 空壳目录 | ⬜ 未开始 |

- 已完成的每日笔记共 **34 篇**（day1–33 + week6 的 day36/41/42 + week7 的 day45）。
- 编号缺口 day7/14/21/34/35 **不是漏写**：day34/35 已被大纲主动删除（"不再保留为独立课程"），day21 从未定义为独立日，day7/14 为周边界空档。
- **Week 7 当前结论**：RAG 主链路、量化评测、文档核验与全量验证均已完成；Java 部分只是复制已知合成范例工程并逐方法改写实现体的实验，不能描述为全新机构完整 SPI 自动生成。

## 作品集进度

### 作品集一：金融机构接入 Skill（financial-institution-integration-skill）

- **核心链路**：PDF / DOCX / XLSX / Markdown 文档解析 → chunk → embedding（BAAI/bge-small-zh-v1.5，512 维）→ Chroma → metadata 过滤 → 向量 + BM25 召回 → RRF 融合排序 → 距离阈值与事实锚点 → 可采纳证据 → LLM 结构化抽取 → 人工闸门 → 评测与追溯。
- **生成实验边界**：现有脚本复制已知合成范例工程，只逐方法改写 `FundManagerImpl` 的实现体；DTO、Constants、Client、异常、枚举、EventFlow 和测试均来自范例，不证明能从零生成全新机构完整 SPI。
- **确定性验证**：已知范例实验保留方法级 Evidence、Mapping、稳定 chunk ID、文档定位和源码 hash，并使用编译、契约测试和 golden 回归约束输出。
- **RAG 评估提前落地**：15 条 query golden set、Hit@K/Precision@K/Recall@K、MRR、可采纳证据精度与召回率、无答案拒答率和机构范围过滤指标已实现；多粒度切块 + BM25 + RRF + 事实锚点后，Hit@5/Recall@5 为 100%，可采纳证据召回率 91.67%，无答案拒答率 100%，质量闸门 PASS。
- **当前缺口**：15 条黄金集参与过调试，需要独立保留集验证泛化；Precision@5 仍为 25%。OCR、通用 SPI 架构生成、线上审批身份审计和生产部署属于未来迭代。向量存储已收敛为 Chroma 单链路。

### 作品集二：AI 智能守护（funding-gateway-ai-guardian）

- 尚未创建。Week 8 先用小型合成场景学习 Agent 最小闭环，Week 9 再决定是否创建独立仓库。

## 下一步（按优先级）

1. **开始 Agent 学习**：先学 Agent 与 Workflow 的边界、Tool Calling、显式状态和终止条件，再实现最小闭环。
2. **求职准备**：每个工作日保留 1.5 小时 Java/AI 面试题与口述；8.12 启动首批投递，不等待第二个作品集。
3. **RAG 后续边界**：OCR、独立保留集和通用 SPI 生成均进入未来迭代，不再阻塞当前学习路线。
4. **数据库边界**：本轮只同步本地 `COURSE_DATA`、周计划和 `seed.sql` 快照，不执行 Supabase 更新或破坏性重置。

## 关键原则（贯穿全程）

- 不做"面试叙事"——当正常生产项目做，不写"为面试而做"。
- 回归本质：每学一点回答"它解决作品集里的哪个业务问题，产出什么可验证证据"。
- 英文/缩写必注中文；计划与实现分离，重大改造先对齐。
- 不用真实公司资料；高置信不自动 approved；不绕过人工确认；不擅自 push。
