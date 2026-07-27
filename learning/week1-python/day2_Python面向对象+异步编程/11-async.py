# 11 - 异步编程基础
# Python 的 async/await

# ============================================
# 1. 同步 vs 异步
# ============================================

# 同步：按顺序执行，一个任务完成后再做下一个
# 异步：可以同时处理多个任务，不用等待

# 生活例子：
# 同步：煮饭 → 煮饭完成 → 炒菜 → 炒菜完成 → 吃饭
# 异步：煮饭（开始煮，不用等）→ 炒菜（同时进行）→ 饭好了，菜也好了

# ============================================
# 2. 协程（Coroutine）
# ============================================

import asyncio

# 定义一个协程函数（用 async 修饰）
async def say_hello():
    print("Hello")
    await asyncio.sleep(1)  # 模拟耗时操作（1秒）
    print("World")

# 运行协程
# 注意：直接调用不会执行，需要用 asyncio.run()
asyncio.run(say_hello())
# 输出：
# Hello
# （等待1秒）
# World

# ============================================
# 3. await 关键字
# ============================================

async def fetch_data():
    print("开始获取数据...")
    await asyncio.sleep(2)  # 模拟网络请求（2秒）
    print("数据获取完成！")
    return {"name": "张三", "age": 25}

async def main():
    # await 等待协程完成
    result = await fetch_data()
    print(f"结果：{result}")

asyncio.run(main())

# ============================================
# 4. 并发执行多个任务
# ============================================

async def task(name, delay):
    print(f"任务 {name} 开始")
    await asyncio.sleep(delay)
    print(f"任务 {name} 完成")

async def run_concurrent():
    # 同时启动三个任务
    await asyncio.gather(
        task("A", 2),
        task("B", 1),
        task("C", 3),
    )

# 输出（注意顺序）：
# 任务 A 开始
# 任务 B 开始
# 任务 C 开始
# 任务 B 完成（1秒后）
# 任务 A 完成（2秒后）
# 任务 C 完成（3秒后）

asyncio.run(run_concurrent())

# ============================================
# 5. 实际应用：异步HTTP请求
# ============================================

import aiohttp  # 需要安装：pip install aiohttp

async def fetch_url(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()

async def fetch_multiple():
    # 并发请求多个URL
    urls = [
        "https://httpbin.org/delay/1",
        "https://httpbin.org/delay/2",
        "https://httpbin.org/delay/1",
    ]
    tasks = [fetch_url(url) for url in urls]
    results = await asyncio.gather(*tasks)
    return results

# ============================================
# 6. 异步上下文管理器
# ============================================

class AsyncDatabase:
    async def __aenter__(self):
        print("连接数据库")
        await asyncio.sleep(0.5)  # 模拟连接耗时
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        print("关闭数据库连接")
        await asyncio.sleep(0.2)

    async def query(self, sql):
        await asyncio.sleep(0.3)
        return f"执行：{sql}"

async def use_database():
    async with AsyncDatabase() as db:
        result = await db.query("SELECT * FROM users")
        print(result)

asyncio.run(use_database())

# ============================================
# 7. 练习
# ============================================

# 练习1：定义一个异步函数，模拟下载文件
async def download_file(filename):
    print(f"开始下载 {filename}")
    await asyncio.sleep(2)  # 模拟下载耗时2秒
    print(f"{filename} 下载完成")
    return filename

# 练习2：并发下载3个文件
async def download_all():
    files = ["video.mp4", "image.jpg", "document.pdf"]
    tasks = [download_file(f) for f in files]
    results = await asyncio.gather(*tasks)
    print(f"所有文件下载完成：{results}")

asyncio.run(download_all())

# 练习3：异步写入日志
async def write_log(message):
    await asyncio.sleep(0.1)  # 模拟写入耗时
    print(f"日志已写入：{message}")

async def log_multiple():
    messages = ["用户登录", "用户操作", "用户登出"]
    tasks = [write_log(msg) for msg in messages]
    await asyncio.gather(*tasks)

asyncio.run(log_multiple())
