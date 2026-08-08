# Layer 3：Agent 范式（学习笔记）

> 记录时间：2026-08-06（含 8/6 18:28 补充：完整范式清单 + 生产落地现状）
> 修正说明：早期教学中把范式讲成"三种主流（ReAct / Plan-and-Execute / Reflection）"是**过度简化**。那三个只是"单智能体 + 用工具"主线上的三种基础循环，并非全貌。本笔记补齐完整范式地图。

## 一、最重要的一条元区分：Workflow vs Agent

Anthropic 的 [Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents) 把“智能体系统”分成两大类，这个区分比“列十几种范式”更本质：

- **Workflow（工作流）**：路径**写死、确定性强**。模型在固定流程里被调用，不自主决定"下一步干嘛"。← 对应 Layer 1 学的"固定工作流"。
- **Agent（自主智能体）**：模型**自主决定**走哪步、调什么工具、停不停。← 之前见的 ReAct 循环就是。

很多被称为"范式"的东西其实属于 **Workflow**，不是自主 Agent。所以"十几种"里一半是工作流模式，一半才是真正的自主 Agent 范式。

## 二、完整范式 / 模式清单（约 16 种）

### A 类：Workflow（确定性工作流，属 Layer 1 范畴）

| # | 模式 | 一句话 | 典型用途 |
|---|---|---|---|
| 1 | **Prompt Chaining**（提示链） | 顺序固定，A 输出喂 B | 多步固定流水线 |
| 2 | **Routing**（路由） | 先分类，再分给专门处理 | 客服分流、工单分类 |
| 3 | **Parallelization**（并行） | 同任务分片并行 + 投票聚合 | 提速、多视角校验 |
| 4 | **Orchestrator-Worker**（编排者-工人） | 中心 LLM **动态**拆任务，派给工人 | 复杂任务动态分解 |
| 5 | **Evaluator-Optimizer**（评估-优化） | 一个生成、一个评估，循环改进 | 代码/文案反复打磨 |

注意 ④ 和 Plan-and-Execute 易混：Plan 是**一次性列死计划**，Worker 是**每步动态选派**——后者更灵活。

### B 类：自主 Agent 范式（模型自主决策）

| # | 范式 | 一句话 | 来源 / 特点 |
|---|---|---|---|
| 6 | **ReAct** | 推理 + 行动交错循环 | Yao 2022，最基础 |
| 7 | **Plan-and-Execute** | 先计划再执行 | 可控、可审计 |
| 8 | **Reflection / Reflexion** | 自我反思挑毛病 | Reflexion 论文带 verbal 强化 |
| 9 | **ReWOO** | 一次性规划所有工具调用，再统一执行 | 省 token，减少来回 |
| 10 | **Tree of Thoughts（ToT）** | 推理走"树"搜索，多分支试探 | 复杂推理、防走死路 |
| 11 | **Graph of Thoughts（GoT）** | 推理走"图"，支持聚合/回溯 | ToT 升级版 |
| 12 | **LATS** | ToT + MCTS + ReAct + Reflection 合体 | 搜索式最强但最贵 |
| 13 | **Autonomous / AutoGPT 式** | 完全自主目标分解循环 | 早期爆火，实际易跑飞 |
| 14 | **Memory-augmented**（记忆增强） | 接向量库做长期记忆 | 跨会话 / 跨任务记忆 |

### C 类：多智能体（对应 Layer 6）

| # | 范式 | 一句话 |
|---|---|---|
| 15 | **Multi-agent Debate**（辩论） | 多个 Agent 互相辩，收敛答案 |
| 16 | **Role-playing / Generative Agents**（角色扮演/生成式） | 模拟多个"人"（斯坦福小镇），各有记忆 + 计划 + 反思 |
| 17 | **AutoGen / CAMEL 式对话协作** | 多个 Agent 对话分工完成复杂任务 |

## 三、为什么 Layer 3 主线只讲 6/7/8

教学取舍，并非不知其他：
- **A 类 1-5** 是 Layer 1"固定工作流"的延伸，已学过。
- **B 类 9-14**（ToT / GoT / LATS / AutoGPT）是**研究向、搜索式、贵且易跑飞**，生产级异常分析助手基本用不到。
- **C 类 15-17** 是 Layer 6 多智能体，单 Agent 够用时不需要拆。

作品集 `funding-gateway-ai-guardian` 是**单智能体 + 只读工具**场景，真正用得上的是 6/7/8 的组合（计划一次 / 反应到底 / 反思一次）。

## 四、生产环境 / 市场真正落地的范式（重点）

研究论文里的范式（ToT/GoT/LATS/AutoGPT）提供了不同探索方法，但**生产落地要受业务约束**。本项目采用以下保守工程原则：

### 4.1 核心结论：生产偏爱"简单、可控、确定性强"的方案

- 业界吃过自主 Agent 的亏：**完全自主（AutoGPT 式）极易跑飞、烧钱、难调试**，已基本退烧。
- 主流共识（Andrew Ng 提的 "agentic workflows"、Anthropic 的务实建议）：**能用简单工作流解决的，绝不上自主 Agent；必须自主时，也要加满护栏（步数上限、工具白名单、校验、人工闸门）。**
- 真实生产里"Agent"大多 = **受控的 ReAct / Plan-and-Execute + 工具调用 + 人在回路（human-in-the-loop）**，而不是搜索式/多智能体。

### 4.2 生产里真正常见的几种形态

| 形态 | 对应范式 | 真实例子 |
|---|---|---|
| 代码生成-测试闭环 | ReAct + Evaluator-Optimizer + 重工具 | Devin、Cursor、Claude Code、Codex：生成 → 执行 → 观察报错 → 修复循环；提交前人工确认 |
| 客服 / 工单助手 | Routing + RAG + 轻工具调用 | Intercom Fin、Zendesk：先分类 → 检索知识库 → 答；必要时调 CRM 工具 |
| 数据分析助手 | ReAct + SQL/代码工具 | 各种 BI 助手：边想边查库、出图 |
| 深度研究 | Plan + Orchestrator-Worker（并行搜索）+ 反思 | OpenAI Deep Research、Perplexity：先计划 → 并行搜网页 → 综合 → 自检 |
| 企业可控调查 | Plan-and-Execute + 人工审批 | 金融/风控场景：先亮计划给人确认 → 再查 → 给建议前自审 → 人工闸门 |

### 4.3 生产里**少见 / 慎用**的

- **ToT / GoT / LATS**：搜索式，token 成本和延迟太高，非极高价值推理任务不用。
- **AutoGPT 式完全自主**：不可控，已基本被弃用。
- **多智能体辩论**：少数高价值决策场景用，多数业务单 Agent + 工作流更稳、更省、更好排查。多智能体真正站得住的落地是**编码场景**（编排者拆任务给子 Agent）和**极端高 stakes 的双人互审**。

### 4.4 主流框架（落地工具，非范式）

- **LangGraph**：状态图（节点 + 边），把工作流和循环都变成可视化图，生产最常用之一。
- **LlamaIndex**：RAG + Agent 工具编排。
- **AutoGen / CrewAI**：多智能体对话（CrewAI 角色扮演），但很多人觉得过度设计。
- 不同平台的产品名称与封装方式会变化；本课程只保留“复杂度必须由业务收益证明、Agent 必须有确定性护栏”这一项目原则。

## 五、对作品集的启示（对齐生产实践）

- 用户的 `funding-gateway-ai-guardian` 设计（合成指标 → Agent 选只读工具 → 生成建议+证据 → 确定性安全校验 → **人工审批** → 模拟执行+审计+回滚）**正好踩中生产主流**：受控 ReAct/Plan + 人在回路 + 确定性安全闸门。不是研究花活，是真能讲的生产级设计。
- 面试叙事可强调："我没用花哨的搜索式/多智能体范式，因为对异常分析场景过重；我用受控的单 Agent + 计划 + 反思 + 人工闸门，这是生产里验证过的务实路线。"
- 可加的 A 类组合：调查前先 **Routing** 判断异常类型（限流异常 vs 对账异常 vs 接口超时），再进 Agent 主线——体现"工作流 + Agent 组合"的工程思维。

## 六、一句话总结

Agent 范式不止三种：约 16 种，分 Workflow（A 类 1-5，确定性）、自主 Agent（B 类 6-14）、多智能体（C 类 15-17）三大类。**生产落地偏爱简单可控的受控 Agent（ReAct/Plan + 工具 + 人在回路）+ 确定性工作流，慎用搜索式（ToT/LATS）和完全自主（AutoGPT）范式。** 用户的作品集设计天然对齐生产主流。

## 七、什么是 Agentic Workflow（补充，8/6 18:31）

Reflection（反思）让模型检查并修正自己的结果，但会增加调用次数、延迟和成本，因此只在有明确质量收益时使用。

### 7.1 定义
**Agentic Workflow = 结构化工作流（有大致固定流水线）+ 嵌入"智能体能力"**：让大模型不是一次交卷，而是能迭代、用工具、计划、自我反思。一句话：**有框架的反复打磨**。

### 7.2 在图谱里的位置（介于纯 Workflow 与自主 Agent 之间）
```
纯 Workflow（Layer 1）  →  Agentic Workflow  →  自主 Agent（ReAct 式）
固定路径，模型不自主        结构化 + 嵌入智能体能力     模型完全自主决定走哪步
```
- 比纯工作流多了迭代/工具/反思
- 比完全自主 Agent 多了结构约束（不会无限跑飞）

### 7.3 四个"智能体设计模式"（Ng）—— 即 Agentic Workflow 里嵌的能力
1. **Reflection（反思）**：生成完自审自改（= Layer 3 ⑧）
2. **Tool Use（工具调用）**：调外部工具拿真实数据（= Layer 2）
3. **Planning（计划）**：先列步骤再执行（= Layer 3 ⑦）
4. **Multi-agent Collaboration（多智能体协作）**：多模型分工/互审（= Layer 6）

### 7.4 关键实证结论
**弱模型 + Agentic Workflow 常干得过强模型的一次性调用**。例：HumanEval 上 GPT-3.5 + 反思/工具循环 > GPT-4 零样本。因为迭代和工具能弥补模型本身不足——"允许改错"比"要求一次写对"现实得多。这也是生产偏爱它的原因：不用等最强模型，现有模型套迭代循环就能提一大截。

### 7.5 真实例子
- 编码助手（Cursor/Claude Code/Devin）：生成→跑测试→看报错→改 = 反思+工具+迭代
- 深度研究（OpenAI Deep Research）：计划→并行搜→综合→自检 = 计划+工具+多智能体
- **本作品集** `funding-gateway-ai-guardian`：合成指标→选工具查→生成建议→确定性校验→人工审批 = 典型 Agentic Workflow（有结构、有工具、有计划反思、有人闸，非完全自主）

### 7.6 面试提醒
- **"Agentic Workflow" ≠ "Autonomous Agent"**，面试别混：前者是生产主流（可控），后者是 research 酷炫（易跑飞）。
- 用户作品集本质就是 Agentic Workflow，对齐生产务实路线。
