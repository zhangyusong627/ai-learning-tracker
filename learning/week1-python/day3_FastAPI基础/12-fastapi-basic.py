# 12 - FastAPI 基础
# Python Web 框架，用于构建 API 接口

# ============================================
# 1. 安装 FastAPI
# ============================================
# pip install fastapi uvicorn

# ============================================
# 2. 最简单的 FastAPI 应用
# ============================================

from fastapi import FastAPI

# 创建 FastAPI 实例
app = FastAPI()

# 定义路由（接口）
# GET 请求：/ 根路径
@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}

# 运行方式：
# 1. 命令行：uvicorn 12-fastapi-basic:app --reload
# 2. 浏览器访问：http://127.0.0.1:8000

# ============================================
# 3. 路径参数
# ============================================

# GET 请求：/items/{item_id}
# 从 URL 中获取参数
@app.get("/items/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id, "message": f"这是第 {item_id} 个商品"}

# 访问：http://127.0.0.1:8000/items/5
# 返回：{"item_id": 5, "message": "这是第 5 个商品"}

# ============================================
# 4. 查询参数
# ============================================

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

# ============================================
# 5. 请求体（POST）
# ============================================

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

# 使用 curl 测试：
# curl -X POST http://127.0.0.1:8000/create-user \
#   -H "Content-Type: application/json" \
#   -d '{"name": "张三", "age": 25, "email": "zhangsan@example.com"}'

# ============================================
# 6. 响应模型
# ============================================

# 定义响应数据的结构
class UserResponse(BaseModel):
    name: str
    age: int
    message: str

# 使用 response_model 指定响应格式
@app.get("/user/{user_id}", response_model=UserResponse)
def get_user(user_id: int):
    return {
        "name": "张三",
        "age": 25,
        "message": f"获取用户 {user_id} 成功"
    }

# ============================================
# 7. 完整示例：简单的用户管理 API
# ============================================

# 内存数据库（生产环境用真实数据库）
users_db = []

@app.post("/api/users")
def create_user_api(user: User):
    """创建用户"""
    users_db.append(user.dict())
    return {
        "code": 200,
        "message": "创建成功",
        "data": user.dict()
    }

@app.get("/api/users")
def get_users():
    """获取所有用户"""
    return {
        "code": 200,
        "message": "获取成功",
        "data": users_db
    }

@app.get("/api/users/{user_id}")
def get_user_by_id(user_id: int):
    """根据 ID 获取用户"""
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

# ============================================
# 8. 自动文档
# ============================================

# FastAPI 自动生成 API 文档：
# - Swagger UI：http://127.0.0.1:8000/docs
# - ReDoc：http://127.0.0.1:8000/redoc

# 文档包含：
# - 所有接口列表
# - 请求参数说明
# - 响应格式
# - 可以直接测试接口
