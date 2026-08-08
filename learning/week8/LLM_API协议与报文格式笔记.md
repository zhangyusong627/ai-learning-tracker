# 大模型 API 协议与报文格式（学习笔记）

> 记录时间：2026-08-06
> 对应层级：Layer 2（工具调用）/ Layer 3（范式）的延伸——协议层本质

## 一、核心认知（最重要的一条）

**所谓"兼容 OpenAI 协议""兼容 Anthropic 协议"，说的就是：按照这家厂商自己定义的「输入 JSON 格式」发请求、按照它定义的「输出 JSON 格式」收响应，来跟大模型交流。**

- 不是模型"懂"了什么协议，是**我们（开发者）按厂商规定的报文格式组装请求、解析响应**。
- "兼容 OpenAI" = 你的代码走 OpenAI 那套字段命名（`messages` / `tools` / `tool_calls` / `finish_reason`），DeepSeek、通义、智谱等厂商的接口也认这套，于是你能"换个 base_url 就迁移"。
- 本课程未把任何厂商报文格式视为 ISO / IETF 强制标准。项目采用 OpenAI 兼容格式只是工程适配选择，不代表所有模型服务的原生报文都相同。

## 二、有没有全球统一标准？

**没有正式的，但有事实标准。**

- OpenAI 兼容 = 事实标准，能用 API 调到的模型八成以上都说这套话。
- Anthropic（Claude）、Gemini（Google）是仅有的两个还坚持**原生格式**的大户（但也都补了 OpenAI 兼容 shim 接口）。
- 中国主流大模型（DeepSeek / 通义 / 智谱 / Kimi / 百川 / 豆包 / 混元 / 星火）**对外提供的几乎都是 OpenAI 兼容接口**；真正自己搞一套原生格式的国产模型已很少（文心、星火是典型）。
- 正因为没有统一标准，才需要 **LiteLLM / Vercel AI SDK / LangChain ChatModel 抽象 / OpenRouter** 这类适配层，把各家格式归一化成一套内部形状。

## 三、OpenAI 兼容协议（我们用的 DeepSeek 就是这套）

### 输入
```json
{
  "model": "deepseek-chat",
  "messages": [
    {"role": "system", "content": "你是资金系统异常分析助手..."},
    {"role": "user", "content": "恒誉授信失败率变高了"}
  ],
  "tools": [
    {"type": "function", "function": {"name": "query_metrics", "description": "...", "parameters": {...}}}
  ],
  "tool_choice": "auto",
  "temperature": 0.3,
  "max_tokens": 1024
}
```
- `messages`：角色数组（system / user / assistant / tool）
- `tools`：函数定义（`name` + `description` + `parameters`）
- `tool_choice`：`auto` / `none` / 强制某个工具
- 生成参数：`temperature` / `top_p` / `max_tokens` / `stream` / `stop`

### 输出（真实原始报文样例）
```json
{"id":"f6e11017...","object":"chat.completion","created":1786008496,"model":"deepseek-v4-flash",
 "choices":[{"index":0,"message":{"role":"assistant","content":"我来帮您分析...",
   "tool_calls":[{"index":0,"id":"call_00_..","type":"function","function":{"name":"query_metrics","arguments":"{\"institution\": \"恒誉消金\"}"}}]},
   "finish_reason":"tool_calls"}],
 "usage":{"prompt_tokens":629,"completion_tokens":133,"total_tokens":762,"prompt_tokens_details":{"cached_tokens":512}}}
```
- `choices[].message.tool_calls`：模型"点单纸条"，`arguments` 是**字符串**（内层 JSON 要转义）
- `finish_reason`：在 choice 内
- `usage`：`prompt/completion/total_tokens`；`cached_tokens` 表示系统提示+工具菜单被缓存、不重复计费

### finish_reason 不止 stop / tool_calls
| 值 | 含义 |
|---|---|
| `stop` | 模型自然说完 |
| `tool_calls` | 模型想调工具 |
| `length` | 撞到 `max_tokens` 上限，被截断 |
| `content_filter` | 被内容审核拦截（涉敏/违规） |
| `function_call` | 老版函数调用，已废弃 |

**工程实践**：
- 不要只信 `finish_reason`，要直接查 `message.tool_calls` 是否存在（更稳，能覆盖流式 `null`、个别模型标 `stop` 却带 `tool_calls` 的边界情况）。
- 生产代码必须兜底 `length`（调大 max_tokens）和 `content_filter`（记日志+友好提示），不能只处理两种。

## 四、Anthropic（Claude）原生协议

### 输入差异
- `system` 是**顶层字段**，不在 messages 里
- `messages[].content` 是**内容块数组**（text / tool_use / tool_result），不是纯字符串
- 工具定义用 `input_schema`（不是 `parameters`）
- 工具选择：`tool_choice: {"type":"auto"/"any"/"tool","name":".."}`
- `max_tokens` **必填**，不填直接报错

### 输出差异
```json
{"id":"msg_01..","type":"message","role":"assistant","model":"claude-..",
 "content":[
   {"type":"text","text":"我来帮您分析..."},
   {"type":"tool_use","id":"toolu_01..","name":"query_metrics","input":{"institution":"恒誉消金"}}
 ],
 "stop_reason":"tool_use","stop_sequence":null,
 "usage":{"input_tokens":629,"output_tokens":133,"cache_creation_input_tokens":0,"cache_read_input_tokens":512}}
```
- 工具调用是 `content` 里的 `tool_use` **内容块**，`input` 是**真对象**（不转义）
- `stop_reason`（顶层）值：`end_turn` / `tool_use` / `max_tokens` / `pause_turn`
- token 字段：`input_tokens` / `output_tokens`
- 工具结果回传：把 `tool_result` 块塞进一条 `user` 消息（不是 OpenAI 那种 `role:"tool"`）

## 五、Gemini（Google）原生协议

### 输入差异
- `contents`（不是 `messages`），角色用 `user` / `model`
- `systemInstruction` 单独字段
- `tools` 包在 `functionDeclarations` 里
- 工具开关：`toolConfig.functionCallingConfig.mode`（AUTO/ANY/NONE）
- 生成参数嵌套在 `generationConfig` 下，叫 `maxOutputTokens`（不是 `max_tokens`）

### 输出差异
```json
{"candidates":[{"content":{"role":"model","parts":[
   {"text":"我来帮您分析..."},
   {"functionCall":{"name":"query_metrics","args":{"institution":"恒誉消金"}}}
 ]},"finishReason":"TOOL_CALLS","safetyRatings":[...]}],
 "usageMetadata":{"promptTokenCount":629,"candidatesTokenCount":133,"totalTokenCount":762},
 "modelVersion":"gemini-.."}
```
- `candidates[]`（不是 `choices[]`）
- `finishReason` **全大写**，在 candidate 顶层
- 函数调用叫 `functionCall`，`args` 是**真对象**
- 多了 OpenAI 没有的 `safetyRatings`（安全评级）

## 六、国产原生格式代表（少数）

- **百度文心（ERNIE）旧版**：顶层 `result`（不是 `choices[].message.content`），鉴权用 `access_token` 不是 API key。
- **讯飞星火（Spark）**：走 **WebSocket**，结构为 `{header:{code,message,sid,status}, parameter:{chat:{domain,temperature,max_tokens,tools}}, payload:{messages:[{role,content}]}}`，没有 `choices`/`tool_calls` 嵌套。

## 七、输入比输出更"碎"的几个维度

- 角色体系不同：OpenAI 四种（system/user/assistant/tool）；Anthropic 只剩 user/assistant（工具做成内容块）；Gemini 用 user/model。
- 系统提示位置不同：OpenAI 在 messages 内、Anthropic 顶层 `system`、Gemini `systemInstruction`。
- 多模态传图不同：OpenAI `{type:"image_url"}`；Anthropic `image` 内容块 + base64；Gemini `inline_data` 部分。
- 流式请求不同：OpenAI `stream:true`；Gemini 另一接口 `streamGenerateContent`；Anthropic SSE。

## 八、和后续学习的关系

- **Layer 4（状态管理）的核心就是这个 `messages` 数组**：不管哪家协议，对话历史都是靠一个"消息数组"在输入里来回传——它就是 Agent 的工作记忆。Layer 4 要解决的是数组越来越长怎么管（截断、压缩、落库）。
- **作品集 `funding-gateway-ai-guardian` 的选型**：先用 DeepSeek 的 OpenAI 兼容入口（messages/tools/tool_choice 这套吃透）；若以后想接多家模型，再引入 LiteLLM 做归一化，业务代码不动——面试可讲"模型层抽象，换厂商不改业务"。

## 九、一句话总结

不同模型服务的原生输入输出存在差异；本课程使用 OpenAI 兼容报文作为统一内部形状，并通过适配层隔离厂商差异。“兼容某协议”只表示能按相应报文约定通信，不表示模型能力、参数语义和错误行为完全一致。
