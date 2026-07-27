# Week 5 - RAG 工程基础（已完成）

## 学习目标

Day 29～33 完成 RAG 分段实践，Day 36 完成全链路集成与阶段验收。原 Day 34、Day 35 不再作为独立待办，已经掌握的内容在正式作品集中按业务需要复用。

## 目录结构

```text
week5/
├── README.md
├── requirements.txt
├── .env.example
├── day29_RAG整体流程/
│   ├── notes.md
│   └── practice/
│       └── minimal_rag.py
├── day30_多格式文档解析/
│   ├── notes.md
│   └── practice/
│       └── unified_loader.py
├── day31_Chunk优化与阈值过滤/
│   ├── notes.md
│   └── practice/
│       ├── chunk_comparison.py
│       └── retrieval_evaluation.py
├── day32_Embedding接入与向量检索/
│   ├── notes.md
│   └── practice/
│       └── vector_retrieval.py
└── day33_检索拼装Prompt与生成回答/
    ├── notes.md
    └── practice/
        └── rag_generation.py
```

Day 36 的全链路集成材料位于 `learning/week6/day36_RAG全链路集成/`。

## 课程安排

| Day | 主题 | 状态 |
|---|---|---|
| Day 29 | RAG 整体流程 | ✅ 已完成 |
| Day 30 | PDF/多格式文档解析 | ✅ 已完成 |
| Day 31 | Chunk 优化+阈值过滤 | ✅ 已完成 |
| Day 32 | Embedding 接入+向量检索 | ✅ 已完成 |
| Day 33 | 检索拼装 Prompt+生成回答 | ✅ 已完成 |
| Day 36 | RAG 全链路集成、引用校验与纠错重试 | ✅ 已完成 |

## 阶段决策

- 不再安排整天的“端到端检索”或重复 RAG 复习；
- Day +1、Day +7、Day +30 复习压缩到每日 30 分钟；
- 解析、检索、阈值、证据和生成能力改在金融机构接入作品集中接受真实任务验收。

## 环境

```bash
cd learning/week5
python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

`.env` 只保存在本地，不提交到 Git。
