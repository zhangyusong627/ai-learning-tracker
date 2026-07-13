# Week 2 - LLM基础 + Prompt Engineering

## 学习时间
2026年6月8日 - 6月13日

## 学习目标
理解大模型原理，掌握Prompt工程，完成Prompt体系搭建

---

## 课程安排

| 日期 | 主题 | 时长 | 状态 |
|------|------|------|------|
| 周一 | Token/Embedding/语义向量 | 2小时 | ✅ 完成 |
| 周二 | Transformer+Attention机制 | 2小时 | ✅ 完成 |
| 周三 | Prompt基础：Role/Task/Context/Output | 2小时 | ✅ 完成 |
| 周四 | Few-shot/CoT/防御Prompt注入 | 2小时 | ✅ 完成 |
| 周五 | Structured Output+稳定JSON | 2小时 | ✅ 完成 |
| 周六 | 幻觉控制+Temperature+System Prompt | 6小时 | ✅ 完成 |
| 周日 | Prompt库整理+项目集成 | 6小时 | ⏳ 待学习 |

---

## 目录结构

```
week2/
├── README.md                              # 本文件：周学习计划和进度
├── day8_Token-Embedding-语义向量/          # 周一：Token/Embedding/语义向量
│   └── notes.md                           # Day 8 学习笔记
├── day9_Transformer+Attention机制/         # 周二：Transformer+Attention机制
│   └── notes.md                           # Day 9 学习笔记
├── day10_Prompt基础/                      # 周三：Prompt基础
│   └── notes.md                           # Day 10 学习笔记
├── day11_Few-shot-CoT-防御注入/           # 周四：Few-shot/CoT/防御Prompt注入
│   └── notes.md                           # Day 11 学习笔记
├── day12_Structured-Output+JSON/          # 周五：Structured Output+稳定JSON
│   └── notes.md                           # Day 12 学习笔记
├── day13_幻觉控制+Temperature+System-Prompt/  # 周六：幻觉控制+Temperature+System Prompt
│   └── notes.md                           # Day 13 学习笔记
└── day14_Prompt库整理+项目集成/            # 周日：Prompt库整理+项目集成
    └── notes.md                           # Day 14 学习笔记
```

---

## 学习进度

### 周一：Token/Embedding/语义向量 ✅

**知识点**：
- [x] Token 的概念和作用
- [x] Token 划分规则
- [x] Token 计费和限制
- [x] Embedding 的定义和作用
- [x] Embedding 与简单编码的区别
- [x] 语义相似度计算（余弦相似度）
- [x] Embedding 的训练原理（猜词游戏）
- [x] 每个维度的值是怎么算出来的

**掌握程度**：★★★☆☆

**学习笔记**：[day8/notes.md](day8/notes.md)

---

## 核心概念速查

| 概念 | 一句话解释 |
|------|------------|
| **Token** | 大模型处理文本的最小单位 |
| **Embedding** | 把文本转换成固定维度的向量 |
| **语义向量** | 保留语义关系的数字数组 |
| **余弦相似度** | 计算两个向量的相似程度 |
| **训练** | 通过大量文本学习语义关系 |
| **Prompt** | 给大模型的指令 |
| **Role** | 定义模型的身份 |
| **Task** | 明确要做什么 |
| **Context** | 提供背景信息 |
| **Output** | 指定返回格式 |
| **Prompt 工程** | 设计和优化 Prompt 的技术 |
| **Few-shot** | 给 AI 几个例子，让它学会格式 |
| **CoT** | 让 AI 分步思考，展示思考过程 |
| **Prompt 注入** | 用户输入恶意内容，试图让 AI 做不该做的事 |
| **System Prompt 保护** | 保护给 AI 的底层指令，防止泄露或篡改 |
| **多层防御** | 输入层、Prompt 层、输出层、架构层、监控层 |
| **Structured Output** | 让 AI 按固定格式输出 |
| **JSON** | JavaScript Object Notation，通用数据格式 |
| **JSON Schema** | 定义 JSON 结构的规范 |
| **Temperature** | 控制输出随机性的参数 |
| **AI 幻觉** | AI 自信地说假话，但自己不知道是假的 |
| **Temperature Scaling** | scaled_logit = logit / temperature |
| **Top-p** | 核采样，限制采样范围 |

---

## 学习心得

### 周一
- Token 是大模型处理文本的最小单位，不是字也不是词
- Embedding 不仅是转换，更重要的是保留语义关系
- 通过训练，语义相似的词在向量空间中距离更近
- 可以通过向量运算发现语义关系（如 king - man + woman ≈ queen）

### 周三
- Prompt 是给大模型的指令
- 四要素：Role, Task, Context, Output
- 好的 Prompt 要明确、完整、有格式
- Prompt 工程是设计和优化 Prompt 的技术
- Prompt 工程师这个职业可能被 AI 自动化
- 真正的价值是理解业务 + 技术实现
- 四要素框架是社区共识，不是唯一标准
- 框架是工具，不是教条
- 先有框架，再打破框架

### 周四
- Few-shot 是给 AI 几个例子，让它学会格式
- CoT 是让 AI 分步思考，展示思考过程
- Prompt 注入类似 SQL 注入，需要多层防御
- System Prompt 保护的核心是明确边界、角色锁定、分隔符保护
- 防御 Prompt 注入需要 5 层防御：输入层、Prompt 层、输出层、架构层、监控层
- 最小权限原则：只给必要的权限
- 深度防御原则：不依赖单点，多层保护
- CoT 论文证明了 Prompt 设计的重要性
- Few-shot + CoT 结合使用效果更好
- 安全性和用户体验需要权衡

### 周五
- Structured Output 是让 AI 按固定格式输出，便于程序处理
- JSON = JavaScript Object Notation，是通用的数据格式
- 让 JSON 稳定的方法：明确格式、给示例、使用 Schema、降低温度、重试机制
- Temperature 控制输出随机性，0 最稳定，1.0 最随机
- 实际应用中，Structured Output 非常重要，可以让 AI 输出直接被程序使用
- 后处理可以修复一些格式问题，但最好让 AI 直接输出正确格式
- Structured Output 适合程序处理，自由文本适合人类阅读

### 周六
- AI 幻觉是 AI 自信地说假话，自己不知道是假的
- 控制幻觉需要 System Prompt 明确规则、要求引用来源、限制回答范围
- Temperature 越低，幻觉风险越低
- System Prompt 是预设的系统级指令，优先级最高
- System Prompt 的技术层级：角色定义、行为约束、输出格式、异常处理
- Temperature 的数学原理：scaled_logit = logit / temperature
- Top-p 控制采样范围，与 Temperature 配合使用
- 不同任务需要不同的 Temperature 设置
- System Prompt 与 Temperature 需要协同使用

---

### 周二：Transformer+Attention机制 ✅

**知识点**：
- [x] Transformer 的架构和作用
- [x] Attention 机制的核心思想
- [x] Self-Attention 的工作原理
- [x] 多头注意力的作用和实现
- [x] 位置编码的作用
- [x] 残差连接和 Layer Normalization
- [x] Feed-Forward Network 的作用
- [x] 编码器 vs 解码器

**掌握程度**：★★★☆☆

**学习笔记**：[day9/notes.md](day9/notes.md)

---

### 周三：Prompt基础：Role/Task/Context/Output ✅

**知识点**：
- [x] Prompt 的定义和作用
- [x] Prompt 的四个核心要素：Role, Task, Context, Output
- [x] 写 Prompt 的常见问题和改进方法
- [x] Prompt 工程的定义
- [x] Prompt 工程师的工作内容和前景
- [x] AI 如何自己写 Prompt（自动优化、Prompt 链、元提示、进化算法）
- [x] 四要素框架的来源和局限性

**掌握程度**：★★★★☆

**学习笔记**：[day10/notes.md](day10/notes.md)

---

### 周四：Few-shot/CoT/防御Prompt注入 ✅

**知识点**：
- [x] Few-shot Prompting 的原理和用法
- [x] Chain-of-Thought (CoT) 的原理和用法
- [x] Prompt 注入攻击和防御方法
- [x] System Prompt 保护的最佳实践
- [x] 防御 Prompt 注入的 5 层防御
- [x] CoT 论文的核心发现
- [x] Few-shot + CoT 结合使用

**掌握程度**：★★★★☆

**学习笔记**：[day11/notes.md](day11/notes.md)

---

### 周五：Structured Output+稳定JSON ✅

**知识点**：
- [x] Structured Output 的概念和作用
- [x] JSON 的基本语法和用途
- [x] 让 AI 输出稳定 JSON 的方法
- [x] Temperature 对输出稳定性的影响
- [x] 重试机制和后处理修复
- [x] Java 中处理 JSON 的常用库
- [x] Structured Output 的实际应用场景

**掌握程度**：★★★★☆

**学习笔记**：[day12/notes.md](day12/notes.md)

---

### 周六：幻觉控制+Temperature+System Prompt ✅

**知识点**：
- [x] AI 幻觉的概念和危害
- [x] 控制幻觉的方法
- [x] System Prompt 的专业原理
- [x] Temperature 的数学原理
- [x] System Prompt 的最佳实践
- [x] Temperature 与其他参数的关系
- [x] System Prompt 与 Temperature 的协同

**掌握程度**：★★★★☆

**学习笔记**：[day13/notes.md](day13/notes.md)

---

## 下一步计划

- [x] 完成周一 Token/Embedding/语义向量
- [x] 完成周二 Transformer+Attention机制
- [x] 完成周三 Prompt基础
- [x] 完成周四 Few-shot/CoT/防御Prompt注入
- [x] 完成周五 Structured Output+稳定JSON
- [x] 完成周六 幻觉控制+Temperature+System Prompt
- [ ] 完成周日 Prompt库整理+项目集成

---

*最后更新：2026年6月10日*

*Day 11 更新：添加 Few-shot/CoT/防御Prompt注入 学习内容和笔记*

*Day 12 更新：添加 Structured Output+稳定JSON 学习内容和笔记*

*Day 13 更新：添加 幻觉控制+Temperature+System Prompt 学习内容和笔记*
