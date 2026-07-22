# Week 5 - RAG 基础 + 企业知识库 V1

## 学习目标

掌握 RAG 全链路，完成能够检索企业文档、生成回答并标注来源的知识库 V1。

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
    ├── notes.md
    └── practice/
        ├── chunk_comparison.py
        └── retrieval_evaluation.py
└── day32_Embedding接入与向量检索/
    ├── notes.md
    └── practice/
        └── vector_retrieval.py
```

后续每日课程继续使用 `dayNN_主题/`，当天笔记放在 `notes.md`，可执行代码放在 `practice/`。

## 课程安排

| Day | 主题 | 状态 |
|---|---|---|
| Day 29 | RAG 整体流程 | ✅ 已完成 |
| Day 30 | PDF/多格式文档解析 | ✅ 已完成 |
| Day 31 | Chunk 优化+阈值过滤 | ✅ 已完成 |
| Day 32 | Embedding 接入+向量检索 | ✅ 已完成 |
| Day 33 | 检索拼装 Prompt+生成回答 | ⏳ 待学习 |
| Day 34 | 企业知识库 V1+引用标注 | ⏳ 待学习 |
| Day 35 | 阶段复盘+Bad Case 整理 | ⏳ 待学习 |

## 环境

```bash
cd learning/week5
python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

`.env` 只保存在本地，不提交到 Git。
