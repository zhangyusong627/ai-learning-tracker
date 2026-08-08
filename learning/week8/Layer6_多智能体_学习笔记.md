# Layer 6 多智能体（Multi-Agent）学习笔记

> 教学纪律：标准技术名词，不自造比喻词。本层采用总分总：先全景，再分 5 个子概念逐个拆解，最后收口挂钩作品集。

---

## 总（全景认知）

### 1. 定义

回顾 Layer 1 地基：**一个 Agent = 一个 LLM（推理引擎） + 一套 Harness（agent loop 智能体循环 + 工具 + 状态管理）**。

**多智能体**：系统中同时存在**多个**这样的 Agent，它们之间通过某种**通信协议**协作，共同完成单 Agent 难以胜任的任务。

关键区分：
- **单 Agent**：一个 Harness 驱动一个 LLM，靠工具扩展能力（你作品集 `funding-gateway-ai-guardian` 当前就是此形态）。
- **多 Agent**：多个独立 Harness+LLM 实体，彼此发消息、交接上下文、分工或辩论。

### 2. 为什么需要（三类动机）

| 动机 | 说明 |
|---|---|
| 上下文窗口膨胀 | 一个 Agent 同时管工具、记忆、推理，messages 越滚越大（Layer 4 亲眼见过 2→14 条）。拆成多 Agent，每个只装自己职责相关上下文，各自瘦身。 |
| 职责混杂降低质量 | 让一个模型同时当"分析师""校验员""执行员"，角色冲突会拉低输出质量。按角色拆成专用 Agent，每个只精通一件事。 |
| 可并行 | 多个子任务彼此独立时，多 Agent 可并发执行；单 Agent 只能串行。 |

### 3. 反模式（什么时候不该用）

多智能体有**协调开销**：Agent 间通信消耗 token、上下文交接会丢信息、一个 Agent 出错会传染下游。

本项目默认选择**单 Agent + 工具**；只有在“子任务真能解耦、且解耦收益 > 协调成本”时才升级为多智能体。这一取舍与 Anthropic [Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents) 所强调的逐步增加复杂度一致，但它是项目决策，不冒充所有团队的统一结论。

### 4. 本层 drill 顺序

1. 拓扑结构（Topology）
2. Agent 间通信协议（Communication Protocol）
3. 编排与路由（Orchestration & Routing）
4. 代表框架（Frameworks）
5. 陷阱与成本（Pitfalls & Cost）

---

## 分 1：拓扑结构（Topology）

拓扑描述多个 Agent 之间**如何组织、谁驱动谁**。以下为标准命名拓扑：

### 1.1 编排者-工作者（Orchestrator-Worker）
- 结构：一个**编排者（Orchestrator）** 接收任务 → 拆分子任务 → 分发给多个**工作者（Worker）** → 汇总结果。
- 注意与 Layer 3 同名 Workflow 范式的区别：Layer 3 的 Orchestrator-Worker 是**代码写死**分解逻辑（确定性工作流）；多智能体版的编排者用 **LLM 自主分解**任务、动态决定派给哪个 Worker，分解逻辑不在代码里写死。
- 适用：任务可并行、子任务相对独立（如"分析 3 家机构，各自跑一遍分析 Agent，最后汇总"）。

### 1.2 主管-下属（Supervisor / Manager）
- 结构：一个**主管（Supervisor）** 持有主对话，按需把子任务委托给多个**专职 Agent（Specialist）**，专职 Agent 不直接面向用户。
- 与编排者的细微差别：主管通常**保留对话主导权**并做最终决策，工作者更偏"无状态执行单元"；实践中两者常混用，统称"manager pattern"。
- 适用：有明确专职分工（如"翻译 Agent""检索 Agent""校验 Agent"围绕一个主管）。

### 1.3 顺序流水线 / 交接（Sequential Pipeline / Handoff）
- 结构：Agent A 的输出作为 Agent B 的输入，链式传递（A → B → C）。
- 每个节点职责单一，下游依赖上游产物。
- 适用：强串行的加工链路（如"抽取 → 清洗 → 结构化"）。

### 1.4 辩论式（Debate）
- 结构：多个 Agent 持**不同立场或视角**就同一问题互相论证、反驳，最终收敛到更稳健的结论。
- 价值：缓解单一模型的确认偏差（confirmation bias）和幻觉；通过交叉检验提升可靠性。
- 适用：高风险决策、需要多角度论证（如"该不该调整熔断阈值"让正方/反方 Agent 辩论）。

### 1.5 角色扮演（Role-playing）
- 结构：给不同 Agent 分配**专业角色**（如"资深风控专家""合规专家"），按角色协作产出。
- 与辩论式的区别：角色扮演强调**互补协作**，辩论式强调**对立检验**。
- 代表实现理念：CrewAI 的 Role/Goal/Backstory 设计即源于此。

### 1.6 黑板（Blackboard）
- 结构：多个 Agent 读写同一块**共享状态（黑板）**，谁需要谁取，不直接点对点通信。
- 适用：子任务间无明确顺序、需要共享中间产物的场景。
- 代价：共享状态需一致性与并发控制，工程复杂。

---

## 分 2：Agent 间通信协议（Communication Protocol）

多个 Agent 要协作，必须定义"怎么说话、怎么传上下文"。三类标准机制：

### 2.1 消息传递（Message Passing）
- 通过**结构化消息**在 Agent 间传递，消息含 `sender` / `recipient` / `content` / 可选 `metadata`（如任务 ID、优先级）。
- 点对点或经消息总线（message bus）路由。
- 标准协议层：Google 于 2025-04-09 [发布 A2A（Agent2Agent Protocol）](https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/)，用于不同 Agent 之间安全交换信息和协同行动。

### 2.2 共享状态（Shared State）
- 多个 Agent 读写**同一外部存储**（数据库、共享内存、黑板），通过读写状态间接通信。
- 优点：解耦发送/接收时序；缺点：需处理一致性与并发竞态。

### 2.3 工具中介（Tool-mediated）
- 把一个 Agent **封装成另一个 Agent 可调用的工具**（暴露 `name` / `description` / `parameters`），调用方通过标准 function calling 触发，拿回 `tool` 消息。
- 这是把多 Agent 复用 Layer 2 工具调用机制的自然做法——下游 Agent 对上游而言就是一个"会思考的工具"。

### 2.4 上下文交接（Context Handoff）
- 核心难题：**把必要上下文传给下游而不丢信息**。两种策略：
  - **全量传递**：把上游完整 messages/状态原样交接——保真但膨胀，触碰窗口上限。
  - **摘要传递**：上游先压缩成摘要再交下游（复用 Layer 4 压缩技术）——省 token 但可能丢细节。
- 工程取舍：按下游需要的"最小必要上下文"决定传什么，必要时保留可回溯的原始引用（ID/指针）而非正文。

> 协议层澄清（避免混淆）：
> - **MCP（Model Context Protocol）**：官方定义为连接 AI 应用与外部系统的[开放标准](https://modelcontextprotocol.io/docs/getting-started/intro)，覆盖数据源、工具和工作流；它不是专门为 Agent 间委派设计的协议。
> - **A2A（Agent2Agent）**：面向 **Agent 与 Agent 之间**的互操作与协作。
> - 二者互补：MCP 解决"Agent 怎么用工具"，A2A 解决"Agent 怎么找别的 Agent、怎么委派任务"。

---

## 分 3：编排与路由（Orchestration & Routing）

决定"任务交给哪个 Agent、谁来驱动流转"。两种路由范式：

### 3.1 确定性路由（Deterministic Routing）
- 由**代码 / 状态机 / 规则**决定下一步交给哪个 Agent。
- 特点：可控、可预测、便宜（不消耗 LLM 调用做路由决策）；但不够灵活，无法应对训练时没见过的分支。
- 典型实现：if-else / 正则表达式匹配意图 / 有限状态机（FSM）。

### 3.2 LLM 自主路由（LLM-based Routing）
- 由**模型根据输入语义**判断转给哪个 Agent（模型输出一个"目标 Agent"标签或 tool_call）。
- 特点：灵活、能处理模糊/未见过的输入；代价是每次路由消耗 token、且模型可能路由错（不稳定）。
- 风险：路由本身也是一次 LLM 决策，会引入错误传播（路由错→整个链路错）。

### 3.3 混合路由（Hybrid）
- 生产主流做法：**确定性骨架 + LLM 在分支内决策**。
- 例：代码先判断"这是风控类请求"（确定性），再让 LLM 在风控分支内决定调哪个工具（自主）。

### 3.4 交接机制（Handoff）
- 概念来源：OpenAI Agents SDK 的 **handoff**——一个 Agent 可**主动把对话控制权交给另一个 Agent**，后者接管后续交互。
- 与"工具中介"区别：handoff 是**控制权转移**（下游成为对话主体），工具中介是**调用-返回**（上游仍是主体）。

---

## 分 4：代表框架（Frameworks）

以下为业界主流多智能体编排框架，各自设计取向不同：

### 4.1 AutoGen（Microsoft）
- 核心抽象：**Conversable Agent（可对话 Agent）**——每个 Agent 能收发消息、能执行代码、能调用 LLM。
- 特点：原生支持**多 Agent 群聊（Group Chat）**、内置 **Human-in-the-loop**（人类作为一种特殊 Agent 介入）。
- 适用：研究型多 Agent 对话、需要人在回路的实验。

### 4.2 CrewAI
- 核心抽象：**Crew（团队）+ Agent（角色）+ Task（任务）+ Flow（流程）**。
- 特点：强调**角色扮演**（每个 Agent 有 Role/Goal/Backstory），Flow 提供确定性的流程编排（弥补纯角色扮演不可控）。
- 适用：按"专家团队"隐喻组织的业务流水线。

### 4.3 LangGraph
- 核心抽象：**图（Graph）**——节点（node）是 Agent 或工具，边（edge）定义流转条件，配**状态（State）** 在节点间传递。
- 特点：显式控制流、支持**状态持久化与 checkpoint**（可中断/恢复）、天然适合单 Agent 与多 Agent 统一编排。
- 适用：需要精确控制流转、要可观测/可恢复的生产系统。

### 4.4 协议层（与框架正交）
- **A2A**：跨框架、跨厂商的 Agent 互操作标准（谁暴露能力、怎么委派）。
- **MCP**：Agent 连接工具/数据的标准（已在 Layer 2 讲）。
- 框架负责"怎么编排"，协议负责"怎么互通"，两者不在同一层。

---

## 分 5：陷阱与成本（Pitfalls & Cost）

### 5.1 协调开销（Coordination Overhead）
- 每个 Agent 间消息都消耗 token 与延迟；Agent 越多，通信成本线性甚至超线性增长。
- 缓解：尽量用确定性路由减少不必要的 LLM 中转；合并相邻步骤。

### 5.2 错误传播（Error Propagation / Cascading Failure）
- 上游 Agent 输出错误或幻觉 → 下游据此继续，错误被放大且难溯源。
- 缓解：在关键交接点加**确定性校验**（呼应 Layer 5 人工闸门 / 预校验）；对上游产物做 schema 校验。

### 5.3 上下文丢失（Context Attenuation）
- 交接（handoff）时若只传摘要，下游可能缺关键细节，做出错误决策。
- 缓解：明确"最小必要上下文"；保留原始引用而非正文（见 2.4）。

### 5.4 可观测性更难（Observability）
- 多 Agent 的 trace 包含更多 span（每个 Agent 一步），定位"哪一步错/慢"更复杂（呼应 Layer 5 可观测性三支柱）。

### 5.5 决策指南：该不该用多 Agent？

```
任务能否拆成独立子任务？
  ├─ 否 → 单 Agent + 工具 即可（不要拆）
  └─ 是 → 解耦收益 > 协调成本吗？
            ├─ 否 → 单 Agent + 工具
            └─ 是 → 子任务需要并行 / 多角度检验吗？
                      ├─ 并行 → Orchestrator-Worker
                      ├─ 多角度检验 → Debate / Role-playing
                      └─ 串行加工 → Sequential Pipeline / Handoff
```

**核心原则**：默认单 Agent；只有当"单 Agent 上下文爆了 / 质量因职责混杂下降 / 真能并行"三者之一成立，且收益明显大于协调成本时，才升级为多 Agent。

---

## 总（收口）

### 三层回扣

| 维度 | 单 Agent（你作品集现状） | 多 Agent（本层） |
|---|---|---|
| 上下文 | 一个 messages 数组，会膨胀（Layer 4） | 每个 Agent 各自瘦身 |
| 职责 | 一个模型身兼多职 | 按角色拆，各司其职 |
| 成本/风险 | 协调成本为零 | 协调开销 + 错误传播 |

### 与作品集 `funding-gateway-ai-guardian` 的关系

- 当前设计是**单 Agent 架构**（一个 Agent 选只读工具 → 生成建议 → 过确定性闸门 → 人工审批），这是**正确选择**：它的链路强串行、任务连贯、上下文本就不大，拆多 Agent 只会增加协调成本和出错面。
- 本层对作品集的价值**不是改架构**，而是面试时能清晰论证：
  1. **为什么选单 Agent**（决策指南的反向运用）；
  2. **如果扩展可以怎么拆**——例如把"治理规则校验"独立成一个**校验 Agent**（主管-下属拓扑），或把"多机构并行分析"用 **Orchestrator-Worker** 提速；
  3. 能准确区分 **MCP（工具协议）vs A2A（Agent 协议）**，不至于在面试中混为一谈。

### 2026-08-08 验证记录

- 已补 `agent-demos/layer6_multi_agent_demo.py`，对比单 Agent 与 Orchestrator-Worker（编排者-工作者）路径。
- 用户能根据“100 份合同可独立处理”判断该场景适合并行 Worker，并能说明当前智能守护链路强串行、无需强拆多 Agent。
- Layer 6 判定完成；代码跑通仅是证据之一，核心证据是能独立解释选型收益与协调成本。
