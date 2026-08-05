# 学习进度总览（Learning Progress Overview）

> 最后更新：2026-08-05
> 说明：本文件为当前真实进度的快照，事实源为 `learning/week*/` 下的每日笔记与作品集仓库的提交记录。学习计划时间表（原 2026-06-01 起）已扩展为 2026-07-27 ～ 2026-09-15，按 `FULL_TIME_AI_CAREER_SPRINT.md` 执行。

## 当前状态

- **当前周次**：Week 7（2026-08-03 ～ 08-09），作品集一已超前完成
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
| Week 7 (week7) | 8.3–8.9 | 作品集一：三模式 AI 直写 + 方法级追溯 | 作品集仓库 commit 45c7f5e / 0d752f0 / 617dcb1 / fb19ea9 | ✅ 超前完成 |
| Week 8 (week8) | 8.10–8.16 | Skill V1 发布 + 首批投递（8.12） | 线上 0/7 topics | 🔵 已提前激活，课程任务未完成 |
| Week 9–12 | 8.17–9.15 | 智能守护、面试冲刺、Offer 冲刺 | 空壳目录 | ⬜ 未开始 |

- 已完成的每日笔记共 **33 篇**（day1–33 + week6 的 day36/41/42）。
- 编号缺口 day7/14/21/34/35 **不是漏写**：day34/35 已被大纲主动删除（"不再保留为独立课程"），day21 从未定义为独立日，day7/14 为周边界空档。
- **Week 7 超前完成说明**：计划中的字段映射、差异识别、RAG 证据、离线人工确认、三模式 Java 生成、编译/契约/golden 验证均已落地；8.5 又补充了方法级 `Evidence/Mapping`、稳定 `chunk_id` 和 `generation_trace.json` 追溯校验。

## 作品集进度

### 作品集一：金融机构接入 Skill（financial-institution-integration-skill）

- **核心链路**：文档解析 → chunk → embedding（BAAI/bge-small-zh-v1.5，512 维）→ 向量库（Chroma / PostgreSQL+pgvector）→ metadata 过滤 → Top-K → 距离阈值 → 可采纳证据 → LLM 结构化抽取 → 人工闸门 → **LLM 直写完整 SPI 代码包** → 方法级证据追溯 → 编译 + 契约测试 + golden 评估。
- **M2 完成**：恒誉（直连）11 操作 AI 直写闭环，契约转 approved（11 ops/70 mappings/10 errors，人工审核），`mvn test` 9/9 PASS（commit 45c7f5e）。
- **M3 完成**：云腾（断直连）10 操作 + 衡丰（混合）11 操作 AI 直写 PASS（commit 62e830b → 0d752f0）；golden 评估三家全绿——恒誉 18 / 云腾 14 / 衡丰 16 测试（`evals/run_golden_codegen_eval.py`）。
- **M3 收尾**：skill 安装说明（docs/安装与使用说明.md）、人工复核清单（workflow.md 三层）、golden 评估、Codex 交接文档（docs/交接文档-给Codex.md，commit 617dcb1 + bc25078）。
- **追溯增强**：commit `fb19ea9` 已推送；Java 方法绑定 Evidence、Mapping、稳定 chunk ID、文档定位和源码 hash，6 个追溯/派生单测通过。
- **RAG 评估提前落地**：15 条 query golden set、Hit@K/Precision@K/Recall@K、MRR、可采纳证据精度与召回率、无答案拒答率和机构范围过滤指标已实现；840 个 chunk 的机构元数据完整，`unknown=0`。当前 Chroma 基线未通过：Hit@5 50%、Recall@5 50%、无答案拒答率 0%，单一全局距离阈值无法兼顾召回与拒答。
- **当前缺口**：优先修复精确字段/阶段依赖召回和无答案伪相关，候选方向为向量 + 关键词混合召回、合并排序和证据支持校验；OCR、线上审批身份审计和统一端到端 runner 属于后续增强。

### 作品集二：AI 智能守护（funding-gateway-ai-guardian）

- 尚未创建（计划 Week 9 启动，需等作品集一达到 V1 验收线后开工，避免两个半成品）。

## 下一步（按优先级）

1. **RAG Bad Case 修复**（Week 8 提前项）：基于现有 15 条黄金集补精确字段关键词召回、合并排序和证据支持校验，再用同一评测集复测，不靠修改标注或挑选单条查询制造 PASS。
2. **数据库事实**（2026-08-05 只读核验）：Supabase week 6/7 为 done 且各 7/7 topics 完成，week 8 为 active 且 0/7；Week 7 数据库旧标题仍由 `applyLocalCoursePlan()` 本地覆盖，未执行额外数据更新。
3. **求职准备**：7.28 起每个工作日 1.5 小时 Java/AI 面试题 + 口述；8.12 启动首批投递；week11 面试题库（38 题）已备好。

## 关键原则（贯穿全程）

- 不做"面试叙事"——当正常生产项目做，不写"为面试而做"。
- 回归本质：每学一点回答"它解决作品集里的哪个业务问题，产出什么可验证证据"。
- 英文/缩写必注中文；计划与实现分离，重大改造先对齐。
- 不用真实公司资料；高置信不自动 approved；不绕过人工确认；不擅自 push。
