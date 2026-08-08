# Agent Demo 目录约定

本目录保存 Week 8 Layer 2–7 的最小可运行示例。代码只使用合成机构、指标和规则，不连接任何生产系统。

## 文件分组

- `layer2_*`：OpenAI 兼容协议、Tool Calling（工具调用）与原始报文观察。
- `layer3_*`：ReAct、Plan-and-Execute 等 Agent 范式及失败案例。
- `layer4_*`：显式状态、短期记忆、上下文增长与压缩。
- `layer5_*`：错误处理、人工闸门、可观测性和成本控制。
- `layer6_*`：单 Agent 与多 Agent 的选型对比。
- `layer7_*`：提示注入、信任边界与安全校验。

## 运行边界

- Layer 5–7 的确定性 Demo 只依赖 Python 标准库，可直接运行。
- 调用真实模型的 Demo 从 `LLM_API_KEY` 或 `DEEPSEEK_API_KEY` 读取密钥；密钥不得写入代码、日志或提交。
- `raw_response_sample.json` 是本地运行产物，可能包含服务商响应元数据，已通过 `.gitignore` 排除。
- 人工闸门 Demo 默认从终端读取审批结果；测试时可注入 `approval_provider` 覆盖批准与拒绝路径。
- 新 Demo 必须有明确输入、输出、终止条件和失败路径；仅“能跑”不能作为掌握证据。
