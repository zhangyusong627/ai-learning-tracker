# Week 1 - Python基础 + FastAPI + AI环境搭建

## 学习时间
2026年6月1日 - 6月7日

## 学习目标
掌握Python核心、FastAPI后端、AI API调用，完成AI聊天助手V1

---

## 课程安排

| 日期 | 主题 | 时长 | 状态 |
|------|------|------|------|
| 周一 | Python核心语法 | 2小时 | ✅ 完成 |
| 周二 | Python面向对象+异步编程 | 2小时 | ✅ 完成 |
| 周三 | FastAPI基础 | 2小时 | ✅ 完成 |
| 周四 | 请求响应+流式输出 | 2小时 | ✅ 完成 |
| 周五 | AI API调用 | 2小时 | ✅ 完成 |
| 周六 | FastAPI综合+项目搭建 | 6小时 | ✅ 完成 |
| 周日 | 项目复盘+GitHub整理 | 6小时 | ⏳ 待学习 |

---

## 目录结构

```
week1-python/
├── README.md                              # 本文件：周学习计划和进度
├── self-practice.py                       # 练习文件
├── 01_api_call.py                         # AI API 调用示例
├── 02_stream.py                           # 流式输出示例
├── 03_multi_turn.py                       # 多轮对话示例
├── day1_Python核心语法/                    # 周一：Python核心语法
│   ├── 01-variables.py                    # 变量和数据类型
│   ├── 02-strings.py                      # 字符串操作
│   ├── 03-list.py                         # 列表
│   ├── 04-dict.py                         # 字典
│   ├── 05-control.py                      # 控制流
│   ├── 06-loop.py                         # 循环
│   ├── 07-function.py                     # 函数
│   ├── 08-file.py                         # 文件读写
│   └── notes.md                           # 周一学习笔记
├── day2_Python面向对象+异步编程/            # 周二：Python面向对象+异步编程
│   ├── 09-class.py                        # 类和对象
│   ├── 10-inheritance.py                  # 继承
│   ├── 11-async.py                        # 异步编程
│   └── notes.md                           # 周二学习笔记
├── day3_FastAPI基础/                       # 周三：FastAPI基础
│   ├── 12-fastapi-basic.py                # FastAPI基础
│   ├── fastapi-demo/                      # FastAPI演示项目
│   └── notes.md                           # 周三学习笔记
├── day4_请求响应+流式输出/                  # 周四：请求响应+流式输出
│   ├── test_stream.py                     # 流式输出演示程序
│   └── notes.md                           # 周四学习笔记
├── day5_AI-API调用/                        # 周五：AI API 调用
│   ├── 01_api_call.py                     # 最简单的 API 调用
│   ├── 02_stream.py                       # 流式输出
│   ├── 03_multi_turn.py                   # 多轮对话
│   └── notes.md                           # 周五学习笔记
└── day6_FastAPI综合+项目搭建/              # 周六：FastAPI综合+项目搭建
    ├── ai-chat/                           # AI 聊天助手项目
    │   ├── main.py                        # FastAPI 主入口
    │   ├── config.py                      # 配置管理
    │   ├── api/                           # API 层
    │   ├── services/                      # 服务层
    │   ├── models/                        # 数据模型
    │   └── static/                        # 前端页面
    └── notes.md                           # 周六学习笔记
```

---

## 学习进度

### 周一：Python核心语法 ✅

**知识点**：
- [x] 变量和数据类型
- [x] 字符串操作
- [x] 列表
- [x] 字典
- [x] 控制流
- [x] 循环
- [x] 函数
- [x] 文件读写

**掌握程度**：★★★★☆

**学习笔记**：[day1/notes.md](day1/notes.md)

---

### 周二：Python面向对象+异步编程 ✅

**知识点**：
- [x] 类和对象
- [x] 类属性 vs 实例属性
- [x] self 的作用
- [x] 继承
- [x] 方法重写
- [x] super() 调用父类方法
- [x] 多态
- [x] 同步 vs 异步
- [x] async/await
- [x] asyncio.gather()

**掌握程度**：★★★★☆

**学习笔记**：[day2/notes.md](day2/notes.md)

---

### 周三：FastAPI基础 ✅

**知识点**：
- [x] FastAPI 是什么（Python Web 框架）
- [x] 路由装饰器（@app.get、@app.post）
- [x] 路径参数（/items/{item_id}）
- [x] 查询参数（/users?name=张三）
- [x] 请求体（BaseModel）
- [x] 数据验证（自动类型检查）
- [x] GET vs POST 的使用场景
- [x] 幂等性和缓存

**掌握程度**：★★★★☆

**学习笔记**：[day3/notes.md](day3/notes.md)

---

### 周四：请求响应+流式输出 ✅

**知识点**：
- [x] HTTP 请求响应 5 个阶段
- [x] 序列化（Python 对象 → JSON）
- [x] 流式输出原理
- [x] SSE 长连接
- [x] async/await 异步处理
- [x] StreamingResponse 使用
- [x] Demo 程序验证

**掌握程度**：★★★★☆

**学习笔记**：[day4/notes.md](day4/notes.md)

---

### 周五：AI API 调用 ✅

**知识点**：
- [x] API 调用的本质（餐厅点餐类比）
- [x] DeepSeek API 配置和使用
- [x] 请求结构（model、messages、temperature）
- [x] 响应结构（choices[0]['message']['content']）
- [x] 流式输出（stream=True + iter_lines）
- [x] 多轮对话（messages 列表）
- [x] temperature 参数控制随机性
- [x] delta 和 message 的区别

**掌握程度**：★★★★☆

**学习笔记**：[day5/notes.md](day5/notes.md)

---

### 周六：FastAPI综合+项目搭建 ✅

**知识点**：
- [x] 项目分层架构（API/服务/模型/配置）
- [x] pydantic-settings 配置管理
- [x] LLM 调用服务封装
- [x] 流式聊天接口
- [x] 前端打字效果实现
- [x] SSE 协议解析

**掌握程度**：★★★★☆

**学习笔记**：[day6/notes.md](day6/notes.md)

---

## Python vs Java 对比速查

| 特性 | Python | Java |
|------|--------|------|
| 变量声明 | 不需要类型 | 必须声明类型 |
| 类定义 | `class Animal:` | `public class Animal {}` |
| 构造方法 | `def __init__(self, name):` | `public Animal(String name)` |
| 继承 | `class Dog(Animal):` | `class Dog extends Animal` |
| 异步编程 | `async/await` | `CompletableFuture` |
| 文件操作 | `with open()` | `try-with-resources` |
| Web框架 | FastAPI | Spring Boot |
| 路由定义 | `@app.get("/")` | `@GetMapping("/")` |
| 数据验证 | `BaseModel` | `@Valid` + 注解 |

---

## 学习资源

- [Python官方文档](https://docs.python.org/3/)
- [廖雪峰Python教程](https://www.liaoxuefeng.com/wiki/1016959663602400)
- [FastAPI官方文档](https://fastapi.tiangolo.com/)

---

## 学习心得

### 周一
- Python 语法简洁，比 Java 更易上手
- 列表和字典是最常用的数据结构
- `with` 语句让文件操作更安全

### 周二
- Python 的类比 Java 更简洁，不需要声明属性类型
- `self` 类似 Java 的 `this`，但必须显式写出来
- 异步编程是 Python 的强大特性，Java 没有直接对应

### 周三
- FastAPI 比 Spring Boot 更简洁，代码量少
- Pydantic 自动验证数据类型，减少错误
- GET 适合查询（幂等、可缓存），POST 适合创建/修改

### 周四
- HTTP 请求响应是 Web 开发的基础，5 个阶段要牢记
- 序列化是数据传输的关键，Python 自动处理很方便
- 流式输出改善用户体验，但实现更复杂
- async/await 提高并发能力，避免线程阻塞

### 周五
- API 调用就是发 HTTP 请求，和 Java 的 HttpClient 类似
- 流式输出改善用户体验，但实现更复杂
- 多轮对话的关键是 messages 列表，AI 本身没有记忆
- temperature 参数控制输出的稳定性
- DeepSeek API 是 OpenAI 兼容格式，学会一个就都会了

### 周六
- 项目分层让代码更清晰，易于维护
- 配置管理很重要，不能把密钥硬编码
- 流式响应需要前后端配合，前端要能解析 SSE 格式
- httpx 比 requests 更现代，原生支持异步

---

## 下一步计划

- [x] 完成周三 FastAPI 基础学习
- [x] 完成周四 请求响应+流式输出
- [x] 完成周五 AI API 调用
- [x] 完成周六 FastAPI综合+项目搭建
- [ ] Day 7：项目复盘 + GitHub 整理

---

*最后更新：2026年6月3日*
