from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from api.chat import router as chat_router
import uvicorn

app = FastAPI(title="AI Chat Assistant", version="1.0.0")

# 注册路由
app.include_router(chat_router, prefix="/api")

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def index():
    """首页"""
    return FileResponse("static/index.html")


@app.get("/health")
async def health():
    """健康检查"""
    return {"status": "ok"}


if __name__ == "__main__":
    print("访问: http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
