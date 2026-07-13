# FastAPI 项目示例
# 运行方式：uvicorn main:app --reload

from fastapi import FastAPI
from pydantic import BaseModel

# 创建 FastAPI 实例
app = FastAPI(title="用户管理API", version="1.0.0")

# ============================================
# 数据模型
# ============================================

class User(BaseModel):
    name: str
    age: int
    email: str = ""

class UserResponse(BaseModel):
    code: int
    message: str
    data: dict | None = None

# ============================================
# 内存数据库
# ============================================

users_db = []

# ============================================
# API 接口
# ============================================

# 根路径
@app.get("/")
def read_root():
    return {"message": "欢迎使用用户管理API", "version": "1.0.0"}

# 获取所有用户
@app.get("/api/users")
def get_users():
    return {
        "code": 200,
        "message": "获取成功",
        "data": users_db
    }

# 搜索用户（必须在通配符路由之前定义）
@app.get("/api/users/search")
def search_users(name: str = None, age: int = None):
    result = users_db
    if name:
        result = [u for u in result if name in u.get("name", "")]
    if age:
        result = [u for u in result if u.get("age") == age]
    return {
        "code": 200,
        "message": "搜索成功",
        "data": result
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

# 创建用户
@app.post("/api/users")
def create_user(user: User):
    users_db.append(user.dict())
    return {
        "code": 200,
        "message": f"用户 {user.name} 创建成功",
        "data": user.dict()
    }

# 更新用户
@app.put("/api/users/{user_id}")
def update_user(user_id: int, user: User):
    if user_id < len(users_db):
        users_db[user_id] = user.dict()
        return {
            "code": 200,
            "message": f"用户 {user.name} 更新成功",
            "data": user.dict()
        }
    else:
        return {
            "code": 404,
            "message": "用户不存在",
            "data": None
        }

# 删除用户
@app.delete("/api/users/{user_id}")
def delete_user(user_id: int):
    if user_id < len(users_db):
        deleted_user = users_db.pop(user_id)
        return {
            "code": 200,
            "message": f"用户 {deleted_user['name']} 删除成功",
            "data": deleted_user
        }
    else:
        return {
            "code": 404,
            "message": "用户不存在",
            "data": None
        }
