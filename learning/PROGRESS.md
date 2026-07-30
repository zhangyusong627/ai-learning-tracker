# 学习进度总览（Learning Progress Overview）

> 最后更新：2026-07-30
> 说明：本文件为当前真实进度的快照，事实源为 `learning/week*/` 下的每日笔记与作品集仓库的提交记录。学习计划时间表（原 2026-06-01 起）已扩展为 2026-07-27 ～ 2026-09-15，按 `FULL_TIME_AI_CAREER_SPRINT.md` 执行。

## 当前状态

- **当前周次**：Week 6（2026-07-27 ～ 08-02），进行中
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
| Week 6 (week6) | 7.27–8.2 | RAG 全链路 + 结构化抽取 + 最小纵向闭环 | day36 / 41 / 42（3 篇） | 🔵 进行中 |
| Week 7–12 | 8.3–9.15 | Skill V0.1/V1、智能守护、面试冲刺 | 空壳目录 | ⬜ 未开始 |

- 已完成的每日笔记共 **33 篇**（day1–33 + week6 的 day36/41/42）。
- 编号缺口 day7/14/21/34/35 **不是漏写**：day34/35 已被大纲主动删除（"不再保留为独立课程"），day21 从未定义为独立日，day7/14 为周边界空档。
- Week 7–12 目前仅为空目录，尚未开始。

## 作品集进度

### 作品集一：金融机构接入 Skill（financial-institution-integration-skill）

- **核心链路**：文档解析 → chunk → embedding（BAAI/bge-small-zh-v1.5，512 维）→ 向量库（Chroma / PostgreSQL+pgvector）→ metadata 过滤 → Top-K → 相关性阈值 → 可采纳证据 → LLM 结构化抽取 → 人工闸门 → Java SPI 骨架生成 → 编译 + 契约测试。
- **验证**：6/6 全 PASS（Chroma / pgvector / V0.1 真实 DeepSeek LLM / Java 契约测试），源码零改动。
- **Maven 工程化（A 级）**：`generate_fund_manager.py` 支持 `--maven` 产出标准 Maven 工程（pom.xml + src/main + src/test），契约测试改用 JUnit 5；新增 `evals/run_java_maven_test.py`（`mvn test` 验证 PASS）。
- **提交状态**：已提交并推送至 `origin/main`，commit **641aa93**（在 f96617a 之上）。✅ 已在 GitHub 形成真实工程证据。
- **V1 验收线**：6 项中 5 项已达标；唯一未完成项是 **RAG 评估体系**（golden set / 召回率 / 查准率 / 无答案拒答率），按计划排在 **Week 8（8.10–8.16）**。

### 作品集二：AI 智能守护（ai-guardian-agent）

- 尚未创建（计划 Week 9 启动，需等作品集一达到 V1 验收线后开工，避免两个半成品）。

## 下一步（按优先级）

1. **口述演练**：能 3–5 分钟讲清全链路 + 三个关键工程决策（metadata 过滤在 Top-K 之前、高置信不自动 approved、离线/在线 embedding 模型必须一致）。这是 8.12 启动投递前最该练的。
2. **RAG 评估体系 + Maven B 级（强类型 DTO / 双向字段映射）**：留到 Week 8 收尾，勿提前 gold-plate（符合 sprint 计划）。
3. **求职准备**：7.28 起每个工作日 1.5 小时 Java/AI 面试题 + 口述；8.12 启动首批投递。

## 关键原则（贯穿全程）

- 不做"面试叙事"——当正常生产项目做，不写"为面试而做"。
- 回归本质：每学一点回答"它解决作品集里的哪个业务问题，产出什么可验证证据"。
- 英文/缩写必注中文；计划与实现分离，重大改造先对齐。
- 不用真实公司资料；高置信不自动 approved；不绕过人工确认；不擅自 push。
