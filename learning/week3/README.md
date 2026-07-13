# Week 3 - LangChain + 聊天助手V2

## 学习时间
2026年6月15日 - 6月21日

## 学习目标
掌握 LangChain 核心，完成 AI 聊天助手 V2（多轮记忆+工具调用）

---

## 课程安排

| 日期 | 主题 | 时长 | 状态 |
|------|------|------|------|
| 周一 | LangChain基础+PromptTemplate | 2小时 | ✅ 完成 |
| 周二 | LCEL表达式+Chains链路 | 2小时 | ✅ 完成 |
| 周三 | Memory机制 | 2小时 | ✅ 完成 |
| 周四 | OutputParser+Function Calling | 2小时 | ✅ 完成 |
| 周五 | 聊天助手增强+记录持久化 | 2小时 | ✅ 完成 |
| 周六 | Function Calling完整实现 | 6小时 | ✅ 完成 |
| 周日 | 项目部署+GitHub整理 | 6小时 | ⏭️ 跳过（已掌握） |

---

## 学习进度

### 周一：LangChain基础+PromptTemplate ✅

**知识点**：
- [x] LangChain 是什么
- [x] 核心组件（LLM/Prompt/Chains/Memory）
- [x] Runnable 统一接口
- [x] 管道语法 `|`
- [x] PromptTemplate 创建和调用
- [x] ChatPromptTemplate 消息类型
- [x] 实操：编写模板化 Prompt

**掌握程度**：★★★☆☆

**学习笔记**：[day15/notes.md](day15/notes.md)

---

### 周二：LCEL表达式+Chains链路 ✅

**知识点**：
- [x] LCEL 概念和 Chain
- [x] 管道语法 `|`
- [x] 多步 Chain
- [x] RunnableParallel 并行执行
- [x] 数据转换（lambda 函数）
- [x] 调试技巧

**掌握程度**：★★★☆☆

**学习笔记**：[day16/notes.md](day16/notes.md)

---

### 周三：Memory机制 ✅

**知识点**：
- [x] Memory 的本质（笔记本）
- [x] 手动实现 Memory（history 列表）
- [x] LangChain 实现 Memory
- [x] BufferMemory（全部保存）
- [x] SummaryMemory（自动总结）
- [x] BufferWindowMemory（只保留最近 K 轮）
- [x] 三种 Memory 类型对比

**掌握程度**：★★★★☆

**学习笔记**：[day17/notes.md](day17/notes.md)

---

### 周四：OutputParser+Function Calling ✅

**知识点**：
- [x] OutputParser（Str/Json）
- [x] Function Calling 概念和原理
- [x] Function Calling 完整流程
- [x] 概念辨析（Prompt/ContextWindow/Skills/FunctionCalling/MCP）
- [x] Skills vs Function Calling

**掌握程度**：★★★★☆

**学习笔记**：[day18/notes.md](day18/notes.md)

---

### 周五：聊天助手增强+记录持久化 ✅

**知识点**：
- [x] MessagesPlaceholder 消息列表占位符
- [x] 聊天助手完整架构
- [x] _convert_history 格式转换
- [x] JSON 持久化（保存/加载历史）
- [x] 清除历史功能
- [x] 与 httpx 版本对比

**掌握程度**：★★★★★

**学习笔记**：[day19/notes.md](day19/notes.md)

---

## 什么是 LangChain？

**LangChain = 用于构建 LLM 应用的框架**

```
LangChain 的核心价值：
1. 标准化 LLM 调用
2. 提供 Prompt 模板
3. 实现链式调用（Chains）
4. 管理对话记忆（Memory）
5. 集成各种工具（Tools）
```

---

## 本周核心组件

| 组件 | 作用 | 学习内容 |
|------|------|----------|
| **PromptTemplate** | Prompt 模板化 | 变量替换、格式控制 |
| **LCEL** | LangChain 表达式语言 | 链式调用语法 |
| **Chains** | 链式调用 | 串联多个组件 |
| **Memory** | 对话记忆 | 多轮对话上下文 |
| **OutputParser** | 输出解析 | 结构化输出 |
| **Function Calling** | 工具调用 | 调用外部 API |

---

## 目录结构

```
week3/
├── README.md                              # 本文件：周学习计划和进度
├── day15_LangChain基础+PromptTemplate/    # 周一：LangChain基础+PromptTemplate
│   └── notes.md                           # Day 15 学习笔记
├── day16_LCEL表达式+Chains/               # 周二：LCEL表达式+Chains链路
│   └── notes.md                           # Day 16 学习笔记
├── day17_Memory机制/                      # 周三：Memory机制
│   └── notes.md                           # Day 17 学习笔记
├── day18_OutputParser+Function-Calling/   # 周四：OutputParser+Function Calling
│   └── notes.md                           # Day 18 学习笔记
├── day19_聊天助手增强+持久化/              # 周五：聊天助手增强+记录持久化
│   └── notes.md                           # Day 19 学习笔记
├── day20_Function-Calling完整实现/         # 周六：Function Calling完整实现
│   └── notes.md                           # Day 20 学习笔记
└── day21_项目部署+GitHub整理/              # 周日：项目部署+GitHub整理
    └── notes.md                           # Day 21 学习笔记
```

---

## 下一步计划

- [x] 完成周一 LangChain基础+PromptTemplate
- [x] 完成周二 LCEL表达式+Chains链路
- [x] 完成周三 Memory机制
- [x] 完成周四 OutputParser+Function Calling
- [x] 完成周五 聊天助手增强+记录持久化
- [x] 完成周六 Function Calling完整实现
- [x] ~~完成周日 项目部署+GitHub整理~~ ⏭️ 跳过（Git/GitHub已掌握，优先学习新技能）

---

## 学习心得

### 周一
- LangChain 之于 LLM = Spring Boot 之于 Web
- Runnable 是核心接口，所有组件都实现
- 管道语法让代码更简洁
- PromptTemplate 让 Prompt 可模板化、可复用
- invoke() 是调用组件的核心方法
- .text 获取模板输出的文本

### 周二
- LCEL 的管道语法让代码更简洁
- 多步 Chain 可以串联多个 LLM 调用
- RunnableParallel 可以并行执行多个任务
- lambda 函数用于数据转换
- 调试技巧帮助理解数据流动
- OutputParser 提取 LLM 响应中的文本内容

### 周三
- Memory 的本质 = "笔记本"，存历史、查历史
- 手动实现了 Memory（history 列表）
- LangChain 的 Memory 就是封装了手动实现
- 三种 Memory 类型适合不同场景：
  - BufferMemory：短对话
  - SummaryMemory：长对话
  - BufferWindowMemory：客服系统
- 对话越来越长会导致上下文窗口爆炸、Token 消耗高

### 周四
- OutputParser 把 LLM 输出转成你想要的格式
- Function Calling 让 LLM 可以调用外部函数
- Function Calling 完整流程：定义工具 → 绑定工具 → LLM 判断 → 执行工具 → 返回结果 → LLM 回答
- Skills 是 Prompt + 流程编排，给 Claude Code 用
- FunctionCalling 是 LLM 调用外部函数的能力，给你的应用用
- MCP 是标准化协议，统一 LLM 与外部工具的交互

### 周五
- MessagesPlaceholder 是核心，让历史记录可以作为 Prompt 的一部分
- 格式转换很重要，JSON 字典需要转换为 LangChain 消息对象
- 持久化防止丢失，每次对话都保存，保证数据安全
- LangChain 更简洁，相比 httpx 直接调用，代码量少、扩展性高
- 大模型是无状态的，我们通过历史记录让它看起来"有状态"

### 周六
- Function Calling 完整流程：定义工具 → 绑定工具 → LLM 判断 → 执行工具 → 返回结果 → LLM 回答
- 多工具调用：bind_tools() 绑定多个工具，LLM 自动选择
- 错误处理很重要：工具执行可能失败，需要 try-except 包裹
- ToolMessage 是关键：将工具结果返回给 LLM 的桥梁
- 实际应用场景：天气查询、计算器、数据库查询等

---

*最后更新：2026年6月30日*

*Day 15 更新：添加 LangChain基础+PromptTemplate 学习内容和笔记*

*Day 16 更新：添加 LCEL表达式+Chains链路 学习内容和笔记*

*Day 17 更新：添加 Memory机制 学习内容和笔记*

*Day 18 更新：添加 OutputParser+Function Calling 学习内容和笔记*

*Day 19 更新：添加 聊天助手增强+记录持久化 学习内容和笔记*

*Day 20 更新：添加 Function Calling完整实现 学习内容和笔记，标记周六完成*