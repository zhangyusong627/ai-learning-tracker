# Day 4 - 请求响应+流式输出

## 学习时间
2026年6月2日

## 学习目标
- 理解 HTTP 请求响应完整流程
- 理解序列化的作用
- 掌握流式输出原理
- 了解 async/await 异步处理

---

## 一、HTTP 请求响应流程

### 5个阶段

```
浏览器 → 服务器 → 浏览器
 1. 构建请求
 2. 路由匹配
 3. 参数解析
 4. 业务逻辑
 5. 构建响应
```

### 详细流程

| 阶段 | 操作 | Java 类比 |
|------|------|-----------|
| **1. 构建请求** | 浏览器拼接 URL + 参数 | `new HttpGet(url)` |
| **2. 路由匹配** | 服务器根据 URL 找到对应方法 | `@RequestMapping` |
| **3. 参数解析** | 解析请求参数，校验类型 | `@RequestParam` |
| **4. 业务逻辑** | 查询数据库，处理数据 | Service 层 |
| **5. 构建响应** | 序列化数据，返回给浏览器 | `@ResponseBody` |

### 示例

```
GET /api/users?name=张三 HTTP/1.1

→ 服务器接收请求
→ 路由匹配到 get_users() 方法
→ 解析参数 name = "张三"
→ 查询数据库 users WHERE name = '张三'
→ 序列化为 JSON
→ 返回 {"code": 200, "data": [...]}
```

---

## 二、序列化

### 什么是序列化？

**一句话**：把 Python 对象转换成 JSON 字符串，以便通过 HTTP 传输。

**为什么需要？**

| 阶段 | 数据格式 | 说明 |
|------|----------|------|
| Python 内存 | dict / list / 对象 | 程序内部使用 |
| HTTP 传输 | JSON 字符串 | 网络传输 |
| 浏览器 | JavaScript 对象 | 前端使用 |

**生活类比**：
- 你写了一封中文信（Python 对象）
- 需要翻译成英文（JSON 字符串）才能寄到国外
- 对方收到后再翻译成他们的语言（JavaScript 对象）

### Python 的序列化

```python
import json

# Python dict
user = {"name": "张三", "age": 25}

# 序列化：dict → JSON 字符串
json_str = json.dumps(user, ensure_ascii=False)
print(json_str)  # '{"name": "张三", "age": 25}'

# 反序列化：JSON 字符串 → dict
user_back = json.loads(json_str)
print(user_back)  # {'name': '张三', 'age': 25}
```

### Java 对比

| Python | Java |
|--------|------|
| `json.dumps(obj)` | `JSON.toJSONString(obj)` |
| `json.loads(str)` | `JSON.parseObject(str)` |
| 自动序列化 | 需要手动处理 |

---

## 三、流式输出（Streaming）

### 普通返回 vs 流式返回

| 方式 | 特点 | 用户体验 |
|------|------|----------|
| **普通返回** | 准备好所有数据后一次性返回 | 等待时间长 |
| **流式返回** | 数据准备好一点就返回一点 | 逐字显示，体验好 |

### 生活类比

| 场景 | 普通返回 | 流式返回 |
|------|----------|----------|
| **图书馆借书** | 找齐10本书后一起给你 | 找到一本先给你一本 |
| **餐厅上菜** | 所有菜做好后一起上 | 做好一道上一道 |
| **直播打字** | 打完一段话再发送 | 边打边显示 |

### 技术实现

```python
from fastapi.responses import StreamingResponse

@app.get("/stream")
async def stream():
    async def generate():
        for i in range(5):
            yield f"第{i+1}条数据\n"  # yield 返回一段数据
            await asyncio.sleep(1)     # 模拟处理耗时
    return StreamingResponse(generate(), media_type="text/plain")
```

### 关键点

| 概念 | 说明 |
|------|------|
| `yield` | 每次返回一段数据，不等待全部准备好 |
| `StreamingResponse` | FastAPI 的流式响应类型 |
| `async def` | 异步函数，不阻塞线程 |
| `await asyncio.sleep(1)` | 异步等待，不阻塞其他请求 |

---

## 四、SSE（Server-Sent Events）

### 什么是 SSE？

**一句话**：服务器主动推送数据给浏览器的长连接技术。

### HTTP vs SSE

| 特点 | 普通 HTTP | SSE |
|------|-----------|-----|
| 连接方式 | 短连接（请求-响应后断开） | 长连接（保持连接） |
| 数据流向 | 浏览器 → 服务器 → 浏览器 | 服务器 → 浏览器（主动推送） |
| 适用场景 | 普通查询 | 实时更新、流式输出 |

### 生活类比

| 场景 | 普通 HTTP | SSE |
|------|-----------|-----|
| **问路** | 问一次得到一次回答 | 保持通话，持续告诉你怎么走 |
| **直播** | 每次刷新页面获取新数据 | 服务器持续推送新消息 |
| **天气预报** | 每次手动查询 | 自动推送天气变化 |

### 使用场景

- AI 对话流式输出（ChatGPT 的打字效果）
- 股票实时行情
- 直播弹幕
- 消息通知

---

## 五、async/await 异步处理

### 同步 vs 异步

| 方式 | 特点 | 问题 |
|------|------|------|
| **同步** | 等待操作完成后才继续 | 并发多时线程阻塞 |
| **异步** | 发起操作后立即继续，结果稍后获取 | 不阻塞线程 |

### 生活类比

| 场景 | 同步 | 异步 |
|------|------|------|
| **排队买饭** | 排队等待，不能做其他事 | 排队时可以玩手机 |
| **煮饭** | 盯着锅等饭熟 | 按下开关后去做别的事 |
| **点外卖** | 站在门口等外卖 | 下单后去做别的事，外卖到了自然会通知 |

### 代码示例

```python
import asyncio

# 同步函数
def sync_task():
    print("开始")
    time.sleep(3)  # 阻塞 3 秒
    print("结束")

# 异步函数
async def async_task():
    print("开始")
    await asyncio.sleep(3)  # 异步等待 3 秒
    print("结束")
```

### 并发请求测试

```python
import time
import asyncio
import requests
from fastapi import FastAPI

app = FastAPI()

# 同步接口
@app.get("/sync")
def sync_endpoint():
    time.sleep(3)  # 模拟耗时操作
    return {"message": "同步完成"}

# 异步接口
@app.get("/async")
async def async_endpoint():
    await asyncio.sleep(3)  # 异步等待
    return {"message": "异步完成"}

# 测试并发
def test_concurrent():
    import concurrent.futures

    # 同步：10个请求，每个3秒，总共30秒
    start = time.time()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        urls = ["http://localhost:8000/sync"] * 10
        executor.map(requests.get, urls)
    print(f"同步耗时: {time.time() - start:.1f}秒")

    # 异步：10个请求，每个3秒，总共约3秒
    start = time.time()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        urls = ["http://localhost:8000/async"] * 10
        executor.map(requests.get, urls)
    print(f"异步耗时: {time.time() - start:.1f}秒")
```

---

## 六、StreamingResponse 详解

### 参数说明

```python
StreamingResponse(
    content=generate(),      # 生成器函数，yield 数据
    media_type="text/plain"  # 响应类型
)
```

### 常见媒体类型

| 类型 | 说明 |
|------|------|
| `text/plain` | 纯文本 |
| `text/html` | HTML 页面 |
| `application/json` | JSON 数据 |
| `text/event-stream` | SSE 事件流 |

### 流式输出流程

```
1. 浏览器发起请求
2. 服务器返回 StreamingResponse
3. 浏览器开始接收数据
4. 服务器 yield 第一段数据
5. 浏览器显示第一段数据
6. 服务器 yield 第二段数据
7. 浏览器显示第二段数据
8. ... 重复 6-7 直到完成
```

---

## 七、Demo 程序说明

### 文件位置

```
learning/week1-python/day4_请求响应+流式输出/test_stream.py
```

### 功能

1. **首页**：显示一个按钮，点击触发流式输出
2. **流式接口**：每秒返回一条数据，共 5 条
3. **前端展示**：使用 ReadableStream 读取流式数据并逐字显示

### 运行方式

```bash
cd learning/week1-python/day4_请求响应+流式输出
python3 test_stream.py
# 访问 http://localhost:8000
```

### 关键代码解析

```python
# 后端：流式响应
@app.get("/stream")
async def stream():
    async def generate():
        for i in range(5):
            yield f"第{i+1}条数据: {time.strftime('%H:%M:%S')}\n"
            await asyncio.sleep(1)
    return StreamingResponse(generate(), media_type="text/plain")

# 前端：读取流式数据
const resp = await fetch('/stream');
const reader = resp.body.getReader();
const decoder = new TextDecoder();
while (true) {
    const {value, done} = await reader.read();
    if (done) break;
    document.getElementById('result').innerText += decoder.decode(value);
}
```

---

## 八、Python vs Java 对比

| 特性 | Python (FastAPI) | Java (Spring Boot) |
|------|------------------|---------------------|
| 流式响应 | `StreamingResponse` | `StreamingResponseBody` |
| 异步处理 | `async/await` | `CompletableFuture` |
| 序列化 | 自动（json.dumps） | Jackson 自动 |
| 长连接 | SSE | SSE / WebSocket |

---

## 九、练习题

### 题目 1：HTTP 请求响应流程

请描述从浏览器发起 GET 请求到收到响应的完整过程。

**答案**：
1. **构建请求**：浏览器拼接 URL 和参数
2. **路由匹配**：服务器根据 URL 找到对应方法
3. **参数解析**：解析请求参数，校验类型
4. **业务逻辑**：查询数据库，处理数据
5. **构建响应**：序列化数据，返回给浏览器

---

### 题目 2：流式输出

为什么需要流式输出？它解决了什么问题？

**答案**：
- **问题**：普通返回需要等待所有数据准备好，用户等待时间长
- **解决**：流式输出可以边准备边返回，用户立即看到结果
- **场景**：AI 对话、实时更新、大数据量查询

---

### 题目 3：代码分析

```python
@app.get("/stream")
async def stream():
    async def generate():
        for i in range(3):
            yield f"Hello {i}\n"
            await asyncio.sleep(1)
    return StreamingResponse(generate(), media_type="text/plain")
```

**问题**：
1. 这个接口返回什么？
2. 输出结果是什么？
3. 如果是同步函数，耗时会是多少？

**答案**：
1. 返回 StreamingResponse，流式输出文本
2. 输出：
   ```
   Hello 0
   Hello 1
   Hello 2
   ```
3. 如果是同步函数，耗时 3 秒；异步函数不阻塞，可以处理其他请求

---

### 题目 4：async/await

async/await 的作用是什么？它解决了什么问题？

**答案**：
- **作用**：异步处理耗时操作，不阻塞线程
- **问题**：同步函数在等待 I/O 时会阻塞线程，导致线程池耗尽
- **解决**：异步函数在等待时可以处理其他请求，提高并发能力
- **类比**：排队买饭时玩手机，而不是傻等

---

## 十、学习心得

- HTTP 请求响应是 Web 开发的基础，5 个阶段要牢记
- 序列化是数据传输的关键，Python 自动处理很方便
- 流式输出改善用户体验，但实现更复杂
- async/await 提高并发能力，避免线程阻塞
- SSE 是长连接技术，适合实时推送场景

---

## 十一、待复习内容

- [ ] HTTP 请求响应 5 个阶段
- [ ] 序列化的概念和作用
- [ ] 流式输出 vs 普通返回的区别
- [ ] SSE 长连接原理
- [ ] async/await 异步处理
- [ ] StreamingResponse 的使用

---

## 十二、下一步学习

- [ ] Day 5：第一个真正的 LLM 调用
- [ ] 注册 API 服务商（OpenAI / 通义千问 / 智谱等）
- [ ] 准备 API Key

---

*笔记创建时间：2026年6月2日*
*学习时长：1.5小时*
*掌握程度：★★★★☆*
