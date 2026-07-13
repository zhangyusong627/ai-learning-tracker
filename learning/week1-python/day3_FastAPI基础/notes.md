# Day 3 - FastAPI基础

## 学习时间
2026年6月1日

## 学习目标
- 搭建FastAPI项目
- 实现简单接口
- 理解请求响应机制

---

## 一、FastAPI 是什么？

**一句话**：FastAPI 是一个 Python Web 框架，用来构建 API 接口。

**Java 类比**：

| Python | Java |
|--------|------|
| FastAPI | Spring Boot |
| 路由装饰器 | @RestController |
| 请求参数 | @RequestParam |
| 响应数据 | JSON 返回 |

---

## 二、核心概念

### 1. 路由装饰器

```python
from fastapi import FastAPI

app = FastAPI()

# GET 请求：/ 根路径
@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}

# POST 请求：/create-user
@app.post("/create-user")
def create_user(user: User):
    return {"message": f"用户 {user.name} 创建成功"}
```

### 2. 路径参数

```python
# GET 请求：/items/{item_id}
# 从 URL 中获取参数
@app.get("/items/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id, "message": f"这是第 {item_id} 个商品"}

# 访问：http://127.0.0.1:8000/items/5
# 返回：{"item_id": 5, "message": "这是第 5 个商品"}
```

### 3. 查询参数

```python
# GET 请求：/users?name=张三&age=25
# 从 URL 的 ? 后面获取参数
@app.get("/users")
def read_user(name: str, age: int = 18):
    return {
        "name": name,
        "age": age,
        "message": f"你好，{name}，你 {age} 岁了"
    }

# 访问：http://127.0.0.1:8000/users?name=张三&age=25
# 返回：{"name": "张三", "age": 25, "message": "你好，张三，你 25 岁了"}
```

### 4. 请求体（POST）

```python
from pydantic import BaseModel

# 定义请求体的数据结构
class User(BaseModel):
    name: str
    age: int
    email: str = ""  # 可选参数，默认空字符串

# POST 请求：/create-user
# 从请求体中获取 JSON 数据
@app.post("/create-user")
def create_user(user: User):
    return {
        "message": f"用户 {user.name} 创建成功",
        "user": user.dict()
    }
```

---

## 三、Pydantic BaseModel

### 作用

| 功能 | 说明 | Java 类比 |
|------|------|-----------|
| **数据验证** | 自动检查类型是否正确 | `@Valid` + `@NotNull` |
| **数据转换** | 自动转换类型（如字符串→整数） | `@JsonDeserialize` |
| **序列化** | 自动转成 JSON | `@JsonProperty` |
| **反序列化** | JSON 自动转成对象 | `@JsonProperty` |
| **自动文档** | 生成 API 文档 | Swagger 注解 |

### 必填 vs 可选字段

```python
class User(BaseModel):
    name: str      # 必填（没有默认值）
    age: int       # 必填（没有默认值）
    email: str = ""  # 可选（有默认值）
```

**规则**：
- **有默认值** → 可选
- **没有默认值** → 必填

---

## 四、GET vs POST

### HTTP 协议约定

| 方法 | 用途 | 参数位置 | 是否需要请求体 |
|------|------|----------|----------------|
| GET | 查询 | URL 参数 | ❌ 不需要 |
| POST | 创建/修改 | 请求体 | ✅ 需要 |
| PUT | 更新 | 请求体 | ✅ 需要 |
| DELETE | 删除 | URL 参数 | ❌ 不需要 |

### 使用场景

| 场景 | 推荐方法 | 原因 |
|------|----------|------|
| **查询数据** | GET | 幂等（多次请求结果一样）、可缓存 |
| **修改数据** | POST | 非幂等（每次请求可能不同） |
| **删除数据** | DELETE | 语义明确 |
| **敏感数据** | POST | 参数不在 URL 中，更安全 |

### GET 的优点

- 可以被浏览器缓存
- 可以被收藏为书签
- 参数在 URL 中，便于调试
- 幂等性（多次请求结果一样）

### POST 的优点

- 参数不在 URL 中，更安全
- 可以传输大量数据
- 不会被浏览器缓存

---

## 五、完整示例：用户管理 API

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# 内存数据库
users_db = []

# 定义用户模型
class User(BaseModel):
    name: str
    age: int
    email: str = ""

# 创建用户
@app.post("/api/users")
def create_user_api(user: User):
    users_db.append(user.dict())
    return {
        "code": 200,
        "message": "创建成功",
        "data": user.dict()
    }

# 获取所有用户
@app.get("/api/users")
def get_users():
    return {
        "code": 200,
        "message": "获取成功",
        "data": users_db
    }

# 根据 ID 获取用户
@app.get("/api/users/{user_id}")
def get_user_by_id(user_id: int):
    if user_id < len(users_db):
        return {
            "code": 200,
            "message": "获取成功",
            "data": users_db[user_id]
        }
    else:
        return {
            "code": 404,
            "message": "用户不存在",
            "data": None
        }
```

---

## 六、路由匹配规则（重要）

### 问题：路由冲突

```python
# ❌ 错误顺序
@app.get("/api/users/{user_id}")
def get_user_by_id(user_id: int):
    ...

@app.get("/api/users/search")
def search_users(name: str = None, age: int = None):
    ...
```

**访问 `/api/users/search` 时会报错**：
```
Input should be a valid integer, unable to parse string as integer
```

### 原因

`{user_id}` 是**通配符**，可以匹配任何内容：

| URL | 是否匹配 `{user_id}` |
|-----|----------------------|
| `/api/users/0` | ✅ 匹配 |
| `/api/users/123` | ✅ 匹配 |
| `/api/users/search` | ✅ 匹配（把 "search" 当作 user_id） |
| `/api/users/abc` | ✅ 匹配（把 "abc" 当作 user_id） |

**路由匹配是按定义顺序进行的**：
1. 先尝试匹配 `/api/users/{user_id}` → 成功匹配
2. 把 "search" 当作 user_id 传入
3. `user_id: int` 期望整数，但收到字符串 → 报错
4. 永远轮不到 `/api/users/search`

### 解决方案

**精确路由放在通配符路由之前**：

```python
# ✅ 正确顺序
@app.get("/api/users/search")  # 先定义精确路由
def search_users(name: str = None, age: int = None):
    ...

@app.get("/api/users/{user_id}")  # 再定义通配符路由
def get_user_by_id(user_id: int):
    ...
```

### 总结

| 规则 | 说明 |
|------|------|
| **精确路由优先** | 固定路径（如 `/search`）要放在通配符路由（如 `/{user_id}`）之前 |
| **通配符路由** | `{param}` 可以匹配任何内容，包括其他路由的名称 |
| **按定义顺序** | FastAPI 按代码定义顺序逐个尝试匹配 |

---

## 七、常用命令

### 1. 激活虚拟环境

```bash
source venv/bin/activate
```

**作用**：激活虚拟环境，使用项目专属的 Python 和依赖包

**生活类比**：
- 虚拟环境 = 私人工具箱
- 激活 = 打开工具箱，可以使用里面的工具
- 关闭终端后，工具箱自动关闭

**验证**：
```bash
# 激活前
python3 -c "import fastapi"  # 报错：ModuleNotFoundError

# 激活后
source venv/bin/activate
python3 -c "import fastapi"  # 成功
```

### 2. 启动 FastAPI 服务

```bash
uvicorn main:app --reload
```

**参数说明**：

| 部分 | 含义 |
|------|------|
| `uvicorn` | ASGI 服务器（类似 Java 的 Tomcat） |
| `main` | 文件名（main.py，不带 .py 后缀） |
| `app` | FastAPI 实例名（`app = FastAPI()`） |
| `--reload` | 开发模式，代码修改后自动重启 |

**生活类比**：
- uvicorn = 服务员
- main.py = 菜单
- app = 餐厅老板
- --reload = 菜单更新后自动通知服务员

**执行后的输出**：
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 3. 完整流程

```bash
# 1. 进入项目目录
cd learning/week1-python/day3_FastAPI基础/fastapi-demo

# 2. 激活虚拟环境（打开工具箱）
source venv/bin/activate

# 3. 启动服务（开门营业）
uvicorn main:app --reload

# 4. 访问接口（顾客点菜）
# 浏览器打开：http://127.0.0.1:8000/docs

# 5. 停止服务（关门休息）
# 按 Ctrl+C
```

### 4. 常见问题

| 问题 | 原因 | 解决方法 |
|------|------|----------|
| `command not found: uvicorn` | 没有激活虚拟环境 | 先执行 `source venv/bin/activate` |
| `ModuleNotFoundError: No module named 'fastapi'` | 虚拟环境没安装依赖 | 执行 `pip install fastapi uvicorn` |
| `Address already in use` | 端口被占用 | 换个端口：`uvicorn main:app --port 8001` |

### 5. 记忆技巧

```
source venv/bin/activate = 激活环境（类似 Java 的 classpath）
uvicorn main:app --reload = 启动服务（类似 java -jar app.jar）
```

---

## 八、自动文档

FastAPI 自动生成 API 文档：

- **Swagger UI**：http://127.0.0.1:8000/docs
- **ReDoc**：http://127.0.0.1:8000/redoc

文档包含：
- 所有接口列表
- 请求参数说明
- 响应格式
- 可以直接测试接口

---

## 九、Python vs Java 对比

| 特性 | Python (FastAPI) | Java (Spring Boot) |
|------|------------------|---------------------|
| 路由定义 | `@app.get("/")` | `@GetMapping("/")` |
| 路径参数 | `/items/{item_id}` | `@PathVariable` |
| 查询参数 | `name: str` | `@RequestParam` |
| 请求体 | `user: User` | `@RequestBody` |
| 数据验证 | `BaseModel` 自动验证 | `@Valid` + 注解 |
| 响应格式 | 直接返回 dict | `@ResponseBody` |

---

## 十、练习题

### 练习1：路由装饰器

```python
@app.get("/hello")
def say_hello():
    return {"message": "Hello"}

@app.post("/user")
def create_user(user: User):
    return {"message": "创建成功"}
```

**答案**：
1. `@app.get("/hello")` 定义的是 GET 类型请求
2. 访问 `/hello` 接口应该用 GET 方法
3. `@app.post("/user")` 的参数 `user` 从请求体获取

---

### 练习2：路径参数 vs 查询参数

```python
@app.get("/users/{user_id}")
def get_user(user_id: int):
    return {"user_id": user_id}

@app.get("/search")
def search_users(name: str, age: int = 18):
    return {"name": name, "age": age}
```

**答案**：
1. 访问 `/users/5` 时，`user_id` 的值是 5
2. 访问 `/search?name=张三` 时，`age` 的值是 18（默认值）
3. 区别：
   - 路径参数：在 URL 路径中，如 `/users/5`
   - 查询参数：在 URL 的 `?` 后面，如 `/search?name=张三&age=25`

---

### 练习3：BaseModel

```python
class Product(BaseModel):
    name: str
    price: float
    stock: int = 0
```

**答案**：
1. 必填字段：`name`、`price`；可选字段：`stock`（有默认值）
2. 传入 `{"name": "手机", "price": "2999"}` 会正常返回，`stock` 自动取默认值 0
3. 继承 `BaseModel` 的作用：
   - 自动进行入参的非空和格式校验
   - 自动生成 API 文档
   - 自动进行序列化和反序列化操作

---

### 练习4：GET vs POST

**答案**：
1. 查询用户信息用 GET：
   - 简单、幂等、可缓存
2. 创建新用户用 POST：
   - 参数较多，需要放在请求体中
   - 非幂等操作
3. 参数位置：
   - GET 请求参数在 URL 中
   - POST 请求参数在请求体中

---

### 练习5：代码理解

```python
@app.get("/api/users/{user_id}")
def get_user_by_id(user_id: int):
    if user_id < len(users_db):
        return {
            "code": 200,
            "message": "获取成功",
            "data": users_db[user_id]
        }
    else:
        return {
            "code": 404,
            "message": "用户不存在",
            "data": None
        }
```

**答案**：
1. `users_db` 是内存数据库（列表存储用户数据）
2. `user_id < len(users_db)` 判断索引是否有效
3. 返回 `code: 404` 因为传入的值超过了索引的最大值，资源不存在

---

## 十一、学习心得

- FastAPI 比 Spring Boot 更简洁，代码量少
- Pydantic 自动验证数据类型，减少错误
- GET 适合查询（幂等、可缓存），POST 适合创建/修改
- 自动生成 API 文档，便于调试
- Python 的类型提示让代码更易读

---

## 十二、待复习内容

- [ ] 路由装饰器的用法
- [ ] 路径参数和查询参数的区别
- [ ] BaseModel 的作用
- [ ] GET vs POST 的使用场景
- [ ] 幂等性的概念
- [ ] HTTP 状态码（200、404）

---

## 十三、下一步学习

- [ ] 周四：请求响应+流式输出
- [ ] 实践：实现带参数的 API 接口
- [ ] 理解流式输出（Streaming）

---

*笔记创建时间：2026年6月1日*
*学习时长：2小时*
*掌握程度：★★★★☆*
