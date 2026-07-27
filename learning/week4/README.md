# Week 4 - Embedding + 向量数据库 + 文档处理基础

## 学习时间
2026年6月22日 - 6月28日

## 学习目标
历史阶段已完成向量检索、Chroma、文本切分和文档解析。LoRA 只保留概念边界，实操暂缓且不属于后续待办。

---

## 课程安排

| 日期 | 主题 | 时长 | 状态 |
|------|------|------|------|
| 周一 | Embedding原理+语义检索 | 2小时 | ✅ 完成 |
| 周二 | 向量数据库基础CRUD | 2小时 | ✅ 完成 |
| 周三 | Chroma实战+向量存储 | 2小时 | ✅ 完成 |
| 周四 | 模型微调入门：LoRA原理+Hugging Face | 2小时 | ✅ 完成 |
| 周五 | 文本切分策略+优化 | 2小时 | ✅ 完成 |
| 周六 | PDF/Word解析+批量处理 | 6小时 | ✅ 完成 |
| 阶段收口 | LoRA 实战暂缓（非待办） | 0小时 | ⏭️ 仅在满足重新进入条件时评估 |

---

## 学习资源

| 资源 | 链接 | 用途 |
|------|------|------|
| Chroma 文档 | https://docs.trychroma.com/ | 向量数据库 |
| Hugging Face | https://huggingface.co/docs | 模型微调 |
| LoRA 论文 | https://arxiv.org/abs/2106.09685 | 理解原理 |
| PEFT 文档 | https://huggingface.co/docs/peft | 微调实战 |
| BGE 模型 | https://huggingface.co/BAAI/bge-small-zh-v1.5 | 中文Embedding |

---

## 技术栈

```
Embedding 模型：
├── BAAI/bge-small-zh-v1.5（中文，开源，免费）
└── 本地运行，无需 API

向量数据库：
└── Chroma（轻量级，Python 原生）

模型微调：
├── Hugging Face Transformers
├── PEFT（LoRA/QLoRA）
└── Datasets
```

---

## 目录结构

```
week4/
├── README.md                              # 本文件：周学习计划和进度
├── day22_Embedding原理+语义检索/          # 周一：Embedding原理+语义检索
│   └── notes.md                           # Day 22 学习笔记
├── day23_向量数据库基础CRUD/              # 周二：向量数据库基础CRUD
│   └── notes.md                           # Day 23 学习笔记
├── day24_Chroma实战+向量存储/             # 周三：Chroma实战+向量存储
│   └── notes.md                           # Day 24 学习笔记
├── day25_模型微调入门/                    # 周四：模型微调入门
│   └── notes.md                           # Day 25 学习笔记
├── day26_文本切分策略/                    # 周五：文本切分策略
│   └── notes.md                           # Day 26 学习笔记
├── day27_PDF-Word解析/                    # 周六：PDF/Word解析
│   └── notes.md                           # Day 27 学习笔记
└── day28_LoRA微调实战/                    # 周日：LoRA微调实战
    └── notes.md                           # Day 28 学习笔记
```

---

## 本周核心概念

| 概念 | 一句话解释 | 学习状态 |
|------|------------|----------|
| Embedding | 把文字变成向量，保留语义关系 | ✅ 已学习 |
| 余弦相似度 | 计算两个向量的相似程度 | ✅ 已学习 |
| 向量数据库 | 专门存储和检索向量的数据库 | ✅ 已学习 |
| Chroma | 轻量级向量数据库，Python 原生 | ✅ 已学习 |
| LoRA | 参数高效微调方法，只训练少量参数 | ✅ 已学习 |
| Hugging Face | AI 模型生态，提供模型和工具 | ✅ 已学习 |

---

## 学习进度

### 周一：Embedding原理+语义检索 ✅

**知识点**：
- [x] Embedding 概念：文字 → 向量
- [x] 语义相似 → 向量相近
- [x] 余弦相似度：计算向量相似程度
- [x] 使用 BGE 模型生成向量
- [x] 实现语义搜索

**掌握程度**：★★★★☆

**学习笔记**：[day22_Embedding原理+语义检索/notes.md](day22_Embedding原理+语义检索/notes.md)

---

### 周二：向量数据库基础CRUD ✅

**知识点**：
- [x] 为什么需要向量数据库
- [x] Chroma 基础操作
- [x] CRUD：创建、读取、更新、删除
- [x] 元数据添加和筛选
- [x] 混合查询：语义搜索 + 元数据筛选

**掌握程度**：★★★★☆

**学习笔记**：[day23_向量数据库基础CRUD/notes.md](day23_向量数据库基础CRUD/notes.md)

---

### 周三：Chroma实战+向量存储 ✅

**知识点**：
- [x] Chroma 集成 Embedding 模型
- [x] 文本 → 向量 → 入库
- [x] 语义检索实战
- [x] 持久化存储

**学习笔记**：[day24_Chroma实战+向量存储/notes.md](day24_Chroma实战+向量存储/notes.md)

---

### 周四：模型微调入门 ✅

**知识点**：
- [x] 什么是模型微调
- [x] 什么时候需要微调 vs Prompt Engineering
- [x] LoRA 原理：参数高效微调
- [x] Hugging Face 生态介绍

**学习笔记**：[day25_模型微调入门/notes.md](day25_模型微调入门/notes.md)

---

### 周五：文本切分策略 ✅

**知识点**：
- [x] 为什么需要文本切分
- [x] 常见切分策略：固定长度、语义切分
- [x] Chunk 大小选择
- [x] 重叠窗口

**学习笔记**：[day26_文本切分策略/notes.md](day26_文本切分策略/notes.md)

---

### 周六：PDF/Word解析 ✅

**知识点**：
- [x] PDF 解析：PyMuPDF
- [x] Word 解析：python-docx
- [x] Word 段落与表格保序提取
- [x] 统一 LangChain Document
- [x] 批量处理与异常隔离
- [x] 接入 RecursiveCharacterTextSplitter

**掌握程度**：★★★★☆

**学习笔记**：[day27_PDF-Word解析/notes.md](day27_PDF-Word解析/notes.md)

---

### 阶段收口：LoRA 微调实战 ⏭️ 暂缓（非待办）

**决策**：当前学习目标是构建 AI 应用，现阶段 Prompt、RAG、工具调用和 Agent 的投入产出比更高。Day 25 已经覆盖微调与 LoRA 的概念边界，因此不为了完成课表而进行训练实操。

**重新进入条件**：
- Prompt、RAG 和工具调用仍无法稳定满足任务；
- 已积累数量、质量和许可范围都合格的领域训练数据；
- 有可量化的基线、评估集和训练后验收指标；
- 可以承担训练、部署和后续版本维护成本。

**知识点**：
- [ ] 准备微调数据
- [ ] 配置 LoRA 参数
- [ ] 训练模型
- [ ] 评估效果

**学习笔记**：[day28_LoRA微调实战/notes.md](day28_LoRA微调实战/notes.md)

---

## 下一步计划

- [x] 完成周一 Embedding原理+语义检索
- [x] 完成周二 向量数据库基础CRUD
- [x] 完成周三 Chroma实战+向量存储
- [x] 完成周四 模型微调入门
- [x] 完成周五 文本切分策略+优化
- [x] 完成周六 PDF/Word解析+批量处理
- [x] 评估周日 LoRA 微调实战的必要性，决定暂缓

---

## 学习心得

### 周一
- Embedding：文字 → 向量，语义相近 → 向量相近
- 余弦相似度：计算向量相似程度
- Chroma 指定 BGE 模型才能语义搜索

### 周二
- Chroma CRUD：增删改查
- 元数据：添加附加信息，支持筛选查询
- 混合查询：语义搜索 + 元数据筛选

### 周三
- 持久化存储：数据保存到磁盘
- 获取集合：get_collection / get_or_create_collection
- 完整系统：Embedding + Chroma + 元数据

### 周四
- 微调 vs Prompt Engineering 的区别
- LoRA：低成本、效果好的微调方法
- Hugging Face：大模型托管平台

### 周五
- 文本切分的概念和原因
- 三种切分策略：固定长度、按句子、重叠窗口
- 维度固定导致语义稀释
- 重叠窗口防止信息丢失

### 周六
- PDF 固定版式按页解析，Word 流式版式按逻辑结构解析
- Word 段落和表格需要按照底层 XML 顺序遍历
- PDF、Word 统一转换为 LangChain Document
- 解析器注册表消除支持格式的重复配置
- 批处理区分成功、失败、跳过和空内容文件
- 33 个原始 Document 切分为 227 个检索 Chunk

---

*创建时间：2026年6月30日*

*最后更新：2026年7月13日*

*Day 27 更新：完成 PDF/Word 解析、批量加载、统一 Document 和文本切分实操*

*Day 28 更新：基于当前 AI 应用开发目标暂缓 LoRA 微调实操，保留重新进入条件*

*Day 22 更新：开始 Embedding 原理学习*
