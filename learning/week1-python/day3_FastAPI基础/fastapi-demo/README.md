# FastAPI 项目示例

## 项目结构

```
fastapi-demo/
├── main.py              # 主程序
├── requirements.txt     # 依赖
└── README.md           # 说明
```

## 启动项目

### 1. 安装依赖

```bash
# 进入项目目录
cd learning/week1-python/day3_FastAPI基础/fastapi-demo

# 创建虚拟环境（如果还没有）
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 启动服务

```bash
uvicorn main:app --reload
```

### 3. 访问接口

- **API 文档（Swagger UI）**：http://127.0.0.1:8000/docs
- **API 文档（ReDoc）**：http://127.0.0.1:8000/redoc
- **根路径**：http://127.0.0.1:8000/

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/` | 根路径，返回欢迎信息 |
| GET | `/api/users` | 获取所有用户 |
| GET | `/api/users/{user_id}` | 根据 ID 获取用户 |
| POST | `/api/users` | 创建用户 |
| PUT | `/api/users/{user_id}` | 更新用户 |
| DELETE | `/api/users/{user_id}` | 删除用户 |
| GET | `/api/users/search` | 搜索用户 |

## 测试接口

### 创建用户

```bash
curl -X POST http://127.0.0.1:8000/api/users \
  -H "Content-Type: application/json" \
  -d '{"name": "张三", "age": 25, "email": "zhangsan@example.com"}'
```

### 获取所有用户

```bash
curl http://127.0.0.1:8000/api/users
```

### 根据 ID 获取用户

```bash
curl http://127.0.0.1:8000/api/users/0
```

### 搜索用户

```bash
curl "http://127.0.0.1:8000/api/users/search?name=张"
```

## 功能特性

- ✅ 完整的 CRUD 操作（增删改查）
- ✅ 数据验证（Pydantic）
- ✅ 自动 API 文档
- ✅ 搜索功能
- ✅ 统一响应格式
