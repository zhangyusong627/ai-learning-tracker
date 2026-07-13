# Day 6 - FastAPI综合+项目搭建

## 学习时间
2026年6月2日

## 学习目标
- 搭建完整的 AI 聊天助手项目
- 理解项目分层架构
- 实现 LLM 调用服务
- 实现流式聊天接口
- 实现前端打字效果

---

## 一、项目架构

### 分层设计

```
┌─────────────────────────────────────┐
│           前端 (static/)            │
│         index.html + JS            │
└─────────────────────────────────────┘
              ↓ HTTP
┌─────────────────────────────────────┐
│         API 层 (api/)              │
│      路由定义 + 请求处理           │
└─────────────────────────────────────┘
              ↓ 调用
┌─────────────────────────────────────┐
│       服务层 (services/)           │
│      业务逻辑 + LLM 调用           │
└─────────────────────────────────────┘
              ↓ 依赖
┌─────────────────────────────────────┐
│       模型层 (models/)             │
│         数据结构定义               │
└─────────────────────────────────────┘
```

### 目录结构

```
ai-chat/
├── main.py              # FastAPI 主入口
├── config.py            # 配置管理
├── requirements.txt     # 依赖列表
├── .env                 # 环境变量（API Key）
├── api/
│   ├── __init__.py
│   └── chat.py          # 聊天接口
├── services/
│   ├── __init__.py
│   └── llm.py           # LLM 调用服务
├── models/
│   ├── __init__.py
│   └── schemas.py       # 数据模型
└── static/
    └── index.html       # 前端页面
```

---

## 二、配置管理

### 为什么需要配置管理？

| 问题 | 解决方案 |
|------|----------|
| API Key 不能硬编码 | 使用 .env 文件 |
| 不同环境配置不同 | pydantic-settings 自动读取 |
| 配置分散各处 | 统一管理 |

### 实现方式

```python
# config.py
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"
    DEEPSEEK_MODEL: str = "deepseek-chat"

    class Config:
        env_file = ".env"

settings = Settings()
```

### 使用方式

```python
from config import settings

# 直接访问配置
api_key = settings.DEEPSEEK_API_KEY
```

---

## 三、LLM 调用服务

### 封装的好处

| 好处 | 说明 |
|------|------|
| **复用** | 多个接口可以调用同一个服务 |
| **维护** | 修改 API 调用逻辑只需改一处 |
| **测试** | 可以单独测试 LLM 服务 |
| **替换** | 换模型只需改配置，不改代码 |

### 核心代码

```python
class LLMService:
    def __init__(self, api_key: str, base_url: str, model: str):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model

    async def chat(self, messages: list[Message]) -> str:
        """非流式对话"""
        # 构建请求
        headers = {"Authorization": f"Bearer {self.api_key}"}
        data = {
            "model": self.model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "stream": False
        }

        # 发送请求
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data
            )
            return response.json()["choices"][0]["message"]["content"]

    async def chat_stream(self, messages: list[Message]) -> AsyncGenerator[str, None]:
        """流式对话"""
        # 类似上面，但 stream=True
        # 使用 client.stream() 读取流式响应
        async for line in response.aiter_lines():
            if line.startswith("data: "):
                chunk = json.loads(line[6:])
                content = chunk["choices"][0]["delta"].get("content", "")
                if content:
                    yield content
```

---

## 四、聊天接口

### 接口设计

| 路径 | 方法 | 说明 |
|------|------|------|
| `/api/chat` | POST | 聊天接口 |
| `/` | GET | 首页 |
| `/health` | GET | 健康检查 |

### 请求体

```json
{
    "messages": [
        {"role": "user", "content": "你好"}
    ],
    "stream": true
}
```

### 响应（流式）

```
data: 你好
data: ！
data: 我
data: 是
data: AI
data: 助手
data: [DONE]
```

---

## 五、前端实现

### 关键技术

| 技术 | 作用 |
|------|------|
| `fetch()` | 发送 HTTP 请求 |
| `ReadableStream` | 读取流式数据 |
| `TextDecoder` | 解码二进制数据 |
| `textContent` | 更新 DOM 内容 |

### 打字效果实现

```javascript
const reader = response.body.getReader();
const decoder = new TextDecoder();
let fullContent = '';

while (true) {
    const { value, done } = await reader.read();
    if (done) break;

    const text = decoder.decode(value);
    // 解析 SSE 格式
    const lines = text.split('\n');
    for (const line of lines) {
        if (line.startsWith('data: ')) {
            const data = line.slice(6);
            if (data === '[DONE]') break;

            fullContent += data;
            assistantDiv.textContent = fullContent;  // 实时更新
        }
    }
}
```

---

## 六、Python vs Java 对比

| 特性 | Python | Java |
|------|--------|------|
| 配置管理 | pydantic-settings | Spring Boot @Value |
| HTTP 客户端 | httpx | HttpClient / RestTemplate |
| 流式处理 | AsyncGenerator | StreamingResponseBody |
| 依赖注入 | 手动 | @Autowired |
| 项目结构 | 简单分层 | Spring MVC 分层 |

---

## 七、练习题

### 题目 1：项目架构

请描述 AI 聊天助手项目的分层结构和各层职责。

**答案**：
- **API 层**：路由定义，处理 HTTP 请求和响应
- **服务层**：业务逻辑，调用 LLM API
- **模型层**：数据结构定义（请求、响应）
- **配置层**：统一管理环境变量

---

### 题目 2：流式响应

为什么聊天接口要使用流式响应？

**答案**：
- **用户体验**：立即看到回复，不用等待全部生成完
- **打字效果**：逐字显示，像真人打字一样
- **减少超时**：长回复不会因为处理时间过长而超时

---

### 题目 3：代码分析

```python
async def chat_stream(self, messages):
    async with httpx.AsyncClient() as client:
        async with client.stream("POST", url, json=data) as response:
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    yield line[6:]
```

**问题**：
1. 为什么要用 `client.stream()`？
2. `aiter_lines()` 的作用是什么？
3. 为什么只处理 `data: ` 开头的行？

**答案**：
1. `client.stream()` 建立长连接，可以持续接收数据
2. `aiter_lines()` 按行读取流式数据
3. SSE 格式以 `data: ` 开头，其他行是元数据或空行

---

## 八、LLM API 调用原理

### 核心问题

**问**：请求大模型的 API 是怎么实现的？

**答**：调用大模型 API 本质就是**发 HTTP 请求**。

### 请求结构（OpenAI 兼容格式）

```json
POST https://api.deepseek.com/chat/completions

{
    "model": "deepseek-chat",
    "messages": [
        {"role": "user", "content": "你好"}
    ],
    "stream": true
}
```

| 字段 | 说明 |
|------|------|
| `model` | 用哪个模型（deepseek-chat） |
| `messages` | 对话历史（角色+内容） |
| `stream` | 是否流式返回 |

### Python 发送请求

```python
import httpx

# 1. 构建请求头（认证）
headers = {
    "Authorization": "Bearer sk-xxx",
    "Content-Type": "application/json"
}

# 2. 构建请求体
data = {
    "model": "deepseek-chat",
    "messages": [{"role": "user", "content": "你好"}],
    "stream": True
}

# 3. 发送请求
async with httpx.AsyncClient() as client:
    async with client.stream("POST", url, headers=headers, json=data) as response:
        # 4. 读取流式响应
        async for line in response.aiter_lines():
            print(line)
```

### Java 类比

| Python | Java |
|--------|------|
| `httpx.AsyncClient` | `HttpClient` |
| `client.stream()` | `HttpRequest` + `BodyHandlers.ofString()` |
| `async for line in response.aiter_lines()` | `response.bodyHandler()` |

---

## 九、ChatGPT 工作原理

### 核心问题

**问**：在 ChatGPT 上面聊天本质上也是发送的 HTTP 请求吗？

**答**：对，**本质上完全一样**。

### ChatGPT 网页版工作流程

```
你在网页输入消息
    ↓
浏览器发送 HTTP 请求
    ↓
OpenAI 后端服务器
    ↓
调用 GPT 模型
    ↓
流式返回给浏览器
    ↓
网页逐字显示
```

### 对比

| 对比项 | 我们的项目 | ChatGPT |
|--------|------------|---------|
| 前端 | 自己写的 HTML | React/Vue |
| 后端 | 自己写的 FastAPI | Node.js/Python |
| 模型 | DeepSeek API | OpenAI API |
| 协议 | HTTP + SSE | HTTP + SSE |

### 所有 AI 聊天产品都是这个原理

| 产品 | 前端 | 后端 | 模型 |
|------|------|------|------|
| ChatGPT | 网页 | Node.js | GPT-4 |
| DeepSeek | 网页 | Python/Go | DeepSeek |
| 通义千问 | 网页 | Java | Qwen |
| 豆包 | 网页/App | Java | 字节模型 |

**都是**：前端 → HTTP 请求 → 后端 → 调用模型 → 流式返回

---

## 十、90天学习计划核心目标

### 总体目标

学会 **用 Python 构建 AI 应用**。

### 分阶段目标

| 阶段 | 时间 | 核心内容 | 产出 |
|------|------|----------|------|
| **第1-2周** | Day 1-14 | Python 基础 + FastAPI + API 调用 | AI 聊天助手 V1 |
| **第3-4周** | Day 15-28 | Prompt Engineering + Function Calling | 智能客服 |
| **第5-6周** | Day 29-42 | RAG 检索增强生成 | 企业知识库问答 |
| **第7-8周** | Day 43-56 | Agent 智能体 | 自动化助手 |
| **第9-10周** | Day 57-70 | Docker + 云部署 | 生产环境应用 |
| **第11-12周** | Day 71-90 | 综合项目 | 作品集 |

---

## 十一、核心技术详解

### 一、LLM 应用开发（第3-4周）

| 技术 | 说明 |
|------|------|
| **Prompt Engineering** | 怎么写提示词，让 AI 输出你想要的结果 |
| **Function Calling** | 让 AI 调用你的函数（查数据库、发邮件、调接口） |
| **多轮对话** | 管理对话历史，让 AI 记住上下文 |
| **上下文窗口** | 理解 token 限制，控制对话长度 |

**场景**：智能客服、代码生成、文案写作

### 二、RAG 检索增强生成（第5-6周）

| 技术 | 说明 |
|------|------|
| **Embedding** | 把文本转成向量（数字数组） |
| **向量数据库** | 存储和检索向量（Milvus、Pinecone） |
| **文档切片** | 把长文档切成小块，便于检索 |
| **检索+生成** | 先检索相关文档，再让 AI 回答 |

**场景**：企业知识库、文档问答、智能搜索

### 三、Agent 智能体（第7-8周）

| 技术 | 说明 |
|------|------|
| **工具调用** | 让 AI 使用搜索、计算器、API |
| **多步推理** | AI 自己规划步骤，一步步解决问题 |
| **记忆管理** | 短期记忆（对话）+ 长期记忆（数据库） |
| **多 Agent 协作** | 多个 AI 分工合作 |

**场景**：自动化助手、研究分析、复杂任务

### 四、部署上线（第9-10周）

| 技术 | 说明 |
|------|------|
| **Docker** | 容器化打包 |
| **云服务器** | 部署到 AWS/阿里云 |
| **API 网关** | 限流、鉴权、日志 |
| **监控告警** | 监控应用状态 |

**场景**：生产环境部署、运维

---

## 十二、核心公式

```
AI 应用 = 前端 + 后端 + 大模型 API + 业务逻辑
```

**你要掌握的**：

| 层 | 内容 |
|----|------|
| **前端** | HTML/JS，能做简单界面 |
| **后端** | FastAPI，能构建 API |
| **AI** | 调用大模型 API，会写 Prompt |
| **业务** | 把 AI 能力集成到具体场景 |

---

## 十三、学习心得

- 项目分层让代码更清晰，易于维护
- 配置管理很重要，不能把密钥硬编码
- 流式响应需要前后端配合，前端要能解析 SSE 格式
- httpx 比 requests 更现代，原生支持异步
- 项目结构要从一开始就规划好，不要临时拼凑
- 调用大模型 API 本质就是发 HTTP 请求
- 所有 AI 聊天产品的原理都一样：前端 → HTTP → 后端 → 模型 → 流式返回
- 90天计划的核心是学会用 Python 构建 AI 应用

---

## 十四、待复习内容

- [ ] 项目分层架构
- [ ] pydantic-settings 配置管理
- [ ] httpx 异步 HTTP 客户端
- [ ] SSE 流式响应格式
- [ ] ReadableStream 前端流式读取
- [ ] LLM API 调用原理
- [ ] ChatGPT 工作原理
- [ ] 90天学习计划核心目标

---

## 十五、下一步学习

- [ ] Day 7：项目复盘 + GitHub 整理
- [ ] Prompt Engineering（写好提示词）
- [ ] Function Calling（让 AI 调用函数）
- [ ] RAG（让 AI 基于你的数据回答）

---

*笔记创建时间：2026年6月2日*
*学习时长：6小时*
*掌握程度：★★★★☆*

---

*笔记更新时间：2026年6月3日*
*更新内容：添加 LLM API 调用原理、ChatGPT 工作原理、90天学习计划核心目标*
