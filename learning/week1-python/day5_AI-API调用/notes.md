# Day 5 - AI API 调用

## 学习时间
2026年6月2日

## 学习目标
- 理解 API 调用的本质
- 掌握 DeepSeek API 的使用方法
- 实现流式输出
- 实现多轮对话

---

## 一、API 调用是什么？

### 生活类比：餐厅点餐

| 餐厅 | API |
|------|-----|
| 菜单 | API 文档（告诉你能调什么接口） |
| 你 | 你的 Python 代码 |
| 服务员 | HTTP 请求 |
| 厨房 | 大模型服务器 |
| 宫保鸡丁 | 你发送的消息 |
| 菜端上来 | 模型的回复 |

### 技术解释

API（Application Programming Interface）是程序之间通信的接口。调用大模型 API 就是：

1. 你的程序发送 HTTP 请求到大模型服务器
2. 服务器处理请求，生成回复
3. 服务器返回 HTTP 响应

---

## 二、DeepSeek API 调用

### 基础配置

```python
import requests

API_KEY = "sk-xxx"  # 你的 API Key
BASE_URL = "https://api.deepseek.com"
```

### 请求结构

```python
resp = requests.post(
    f"{BASE_URL}/v1/chat/completions",
    headers={
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    },
    json={
        "model": "deepseek-chat",  # 模型名称
        "messages": [
            {"role": "user", "content": "你好"}
        ]
    }
)
```

### 关键参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `model` | 模型名称 | `deepseek-chat`, `deepseek-v4-flash` |
| `messages` | 对话历史 | `[{"role": "user", "content": "..."}]` |
| `temperature` | 随机性（0-1） | 0=稳定，1=有创意 |
| `stream` | 是否流式输出 | `True`/`False` |

### 响应结构

```python
data = resp.json()
content = data['choices'][0]['message']['content']
```

---

## 三、流式输出

### 为什么需要流式输出？

| 方式 | 特点 | 用户体验 |
|------|------|----------|
| **普通返回** | 憋一句完整的再给你 | 等待时间长，体验差 |
| **流式返回** | 边想边说，逐字显示 | 像打字一样，体验好 |

### 代码实现

```python
# 1. 开启流式
resp = requests.post(..., json={"stream": True}, stream=True)

# 2. 逐行读取
for line in resp.iter_lines():
    if line:
        line = line.decode('utf-8')
        if line.startswith('data: '):
            line = line[6:]
        if line == '[DONE]':
            break
        data = json.loads(line)
        delta = data['choices'][0]['delta']
        if 'content' in delta:
            print(delta['content'], end='', flush=True)
```

### 关键区别

| 类型 | 普通请求 | 流式请求 |
|------|----------|----------|
| 响应内容 | `choices[0]['message']['content']` | `choices[0]['delta']['content']` |
| 含义 | 完整消息 | 增量内容（delta = 增量） |
| 结束标志 | 无 | `data: [DONE]` |

---

## 四、多轮对话

### 问题：AI 没有记忆

AI 本身没有记忆，每次请求都是独立的。要让它"记住"，需要把对话历史发给它。

### 解决方案：messages 列表

```python
# 对话历史
messages = []

# 每次对话都往里加
messages.append({"role": "user", "content": "我叫小明"})
messages.append({"role": "assistant", "content": "你好小明"})
messages.append({"role": "user", "content": "我叫什么"})
messages.append({"role": "assistant", "content": "你叫小明"})

# 发给 AI 的是整个列表
resp = requests.post(..., json={"messages": messages})
```

### AI 看到的对话历史

```json
[
  {"role": "user", "content": "我叫小明"},
  {"role": "assistant", "content": "你好小明"},
  {"role": "user", "content": "我叫什么"}
]
```

### 实际应用

| 场景 | 做法 |
|------|------|
| ChatGPT 网页版 | 浏览器本地存 messages，每次发给 API |
| 客服机器人 | 数据库存对话历史，每次取出发给 API |
| 你写的代码 | 就是这个 `messages` 列表 |

---

## 五、代码示例

### 01_api_call.py - 最简单的调用

```python
import requests

API_KEY = "sk-xxx"
BASE_URL = "https://api.deepseek.com"

resp = requests.post(
    f"{BASE_URL}/v1/chat/completions",
    headers={
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    },
    json={
        "model": "deepseek-chat",
        "messages": [
            {"role": "user", "content": "你好，请用一句话介绍你自己"}
        ]
    }
)

data = resp.json()
print("状态码:", resp.status_code)
print("回复:", data['choices'][0]['message']['content'])
```

### 02_stream.py - 流式输出

```python
import requests
import json

API_KEY = "sk-xxx"
BASE_URL = "https://api.deepseek.com"

resp = requests.post(
    f"{BASE_URL}/v1/chat/completions",
    headers={
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    },
    json={
        "model": "deepseek-chat",
        "temperature": 0,
        "stream": True,
        "messages": [
            {"role": "user", "content": "用一句话解释什么是 API"}
        ]
    },
    stream=True
)

print("AI 回答: ", end="")
for line in resp.iter_lines():
    if line:
        line = line.decode('utf-8')
        if line.startswith('data: '):
            line = line[6:]
        if line == '[DONE]':
            break
        data = json.loads(line)
        delta = data['choices'][0]['delta']
        if 'content' in delta:
            print(delta['content'], end='', flush=True)
print()
```

### 03_multi_turn.py - 多轮对话

```python
import requests

API_KEY = "sk-xxx"
BASE_URL = "https://api.deepseek.com"

messages = []

def chat(user_input):
    messages.append({"role": "user", "content": user_input})

    resp = requests.post(
        f"{BASE_URL}/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "deepseek-chat",
            "temperature": 0,
            "messages": messages
        }
    )

    data = resp.json()
    assistant_reply = data['choices'][0]['message']['content']
    messages.append({"role": "assistant", "content": assistant_reply})

    return assistant_reply

# 测试对话
print("你: 我叫小明")
print("AI:", chat("我叫小明"))

print("\n你: 我叫什么名字？")
print("AI:", chat("我叫什么名字？"))
```

---

## 六、Python vs Java 对比

| 特性 | Python | Java |
|------|--------|------|
| HTTP 请求 | `requests.post()` | `HttpClient` |
| JSON 处理 | `json.loads()` | `JSON.parseObject()` |
| 流式处理 | `iter_lines()` | `InputStream` |
| 异步处理 | `async/await` | `CompletableFuture` |

---

## 七、练习题

### 题目 1：API 调用

请描述调用大模型 API 的完整流程。

**答案**：
1. 准备 API Key 和请求地址
2. 构建请求头（Authorization）
3. 构建请求体（model、messages）
4. 发送 HTTP POST 请求
5. 解析响应 JSON
6. 提取回复内容

---

### 题目 2：流式输出

为什么流式输出需要设置两个 `stream=True`？

**答案**：
- 第一个：`json={"stream": True}` — 告诉服务器要流式响应
- 第二个：`requests.post(..., stream=True)` — 告诉 requests 库要流式读取

---

### 题目 3：多轮对话

为什么 AI 本身没有记忆？多轮对话是怎么实现的？

**答案**：
- AI 本身是无状态的，每次请求都是独立的
- 多轮对话是客户端把整个对话历史（messages 列表）发给服务器
- 服务器根据对话历史生成下一句话
- 这就是为什么 ChatGPT 会限制对话长度——太长了发不完

---

## 八、学习心得

- API 调用就是发 HTTP 请求，和 Java 的 HttpClient 类似
- 流式输出改善用户体验，但实现更复杂
- 多轮对话的关键是 messages 列表，AI 本身没有记忆
- temperature 参数控制输出的稳定性
- DeepSeek API 是 OpenAI 兼容格式，学会一个就都会了

---

## 九、待复习内容

- [ ] API 调用的请求结构
- [ ] 流式输出的实现原理
- [ ] 多轮对话的 messages 列表
- [ ] temperature 参数的作用
- [ ] delta 和 message 的区别

---

## 十、下一步学习

- [ ] Day 6：Prompt Engineering 基础
- [ ] 学习如何写好 Prompt
- [ ] 实践 Few-shot、CoT 等技巧

---

*笔记创建时间：2026年6月2日*
*学习时长：1.5小时*
*掌握程度：★★★★☆*
