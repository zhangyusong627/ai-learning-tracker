# ============================================
# Day 1-2 练习（已完成）
# ============================================

# 问题1：定义一个"动物类" Animal，有 name 属性和 speak() 方法。然后定义 Dog 类继承 Animal，重写 speak() 方法输出"汪汪汪"。
class Animal:
    def __init__(self, name):
        self.name = name

    def speak(self):
        print(f"{self.name}发出声音")

class Dog(Animal):
    def speak(self):
        print("汪汪汪！")

dog = Dog("旺财")
dog.speak()

# 问题2：定义一个异步函数，模拟同时下载3个文件，每个文件需要2秒，总共需要多长时间？
import asyncio

async def download_file(filename):
    print(f"开始下载 {filename}")
    await asyncio.sleep(2)
    print(f"{filename} 下载完成")

async def download_files():
    tasks = [download_file("file1.txt"), download_file("file2.txt"), download_file("file3.txt")]
    await asyncio.gather(*tasks)

asyncio.run(download_files())

# ============================================
# Day 3 练习（FastAPI基础）
# ============================================

# 注意：运行 FastAPI 需要先安装依赖：
# pip install fastapi uvicorn

# 问题1：定义一个"商品类" Product，有 name、price、stock 属性
# 问题2：创建一个 POST 接口 /api/products，用于创建商品
# 问题3：创建一个 GET 接口 /api/products/{product_id}，用于查询商品

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# 定义商品模型
class Product(BaseModel):
    name: str
    price: float
    stock: int = 0

# 内存数据库
products_db = []

# 创建商品接口
@app.post("/api/products")
def create_product(product: Product):
    products_db.append(product.dict())
    return {
        "code": 200,
        "message": f"商品 {product.name} 创建成功",
        "data": product.dict()
    }

# 查询商品接口
@app.get("/api/products/{product_id}")
def get_product(product_id: int):
    if product_id < len(products_db):
        return {
            "code": 200,
            "message": "获取成功",
            "data": products_db[product_id]
        }
    else:
        return {
            "code": 404,
            "message": "商品不存在",
            "data": None
        }

# 查询所有商品接口
@app.get("/api/products")
def get_products():
    return {
        "code": 200,
        "message": "获取成功",
        "data": products_db
    }

# 运行方式：
# 1. 命令行：uvicorn self-practice:app --reload
# 2. 浏览器访问：http://127.0.0.1:8000/docs