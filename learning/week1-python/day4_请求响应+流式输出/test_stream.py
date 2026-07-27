"""
简单的流式输出测试
"""
import time
import asyncio
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, StreamingResponse
import uvicorn

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
def index():
    html = """
<!DOCTYPE html>
<html>
<head><title>Stream Test</title></head>
<body>
<h1>流式输出测试</h1>
<button onclick="testStream()">点击测试流式输出</button>
<pre id="result"></pre>
<script>
async function testStream() {
    document.getElementById('result').innerText = '连接中...\\n';
    const resp = await fetch('/stream');
    const reader = resp.body.getReader();
    const decoder = new TextDecoder();
    while (true) {
        const {value, done} = await reader.read();
        if (done) break;
        document.getElementById('result').innerText += decoder.decode(value);
    }
}
</script>
</body>
</html>
"""
    return html

@app.get("/stream")
async def stream():
    async def generate():
        for i in range(10):
            yield f"第{i+1}条数据: {time.strftime('%H:%M:%S')}\n"
            await asyncio.sleep(1)
    return StreamingResponse(generate(), media_type="text/plain")

if __name__ == "__main__":
    print("访问: http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
