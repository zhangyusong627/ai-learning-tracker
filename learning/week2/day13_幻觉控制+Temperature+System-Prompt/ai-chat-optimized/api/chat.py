from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from models.schemas import ChatRequest, ChatResponse, Message
from services.llm import LLMService
from services.security import PromptGuard, load_system_prompt
from config import settings
import json

router = APIRouter()

# 创建 LLM 服务实例
llm_service = LLMService(
    api_key=settings.DEEPSEEK_API_KEY,
    base_url=settings.DEEPSEEK_BASE_URL,
    model=settings.DEEPSEEK_MODEL
)


@router.post("/chat")
async def chat(request: ChatRequest):
    """
    聊天接口

    支持任务类型：
    - general: 通用对话（默认）
    - translate: 翻译
    - code: 代码生成
    - analyze: 数据分析
    """

    # 获取用户最后一条消息
    user_message = request.messages[-1].content if request.messages else ""

    # 1. 检查输入安全
    is_safe, error_msg = PromptGuard.check_input(user_message)
    if not is_safe:
        error_msg = f"⚠️ {error_msg}"
        if request.stream:
            # 流式模式：返回 SSE 格式的错误
            async def error_generate():
                yield f"data: {error_msg}\n\n"
                yield "data: [DONE]\n\n"
            return StreamingResponse(error_generate(), media_type="text/event-stream")
        else:
            return ChatResponse(content=error_msg, model=settings.DEEPSEEK_MODEL)

    # 2. 获取任务类型（默认为 general）
    task = getattr(request, 'task', 'general') or 'general'

    # 3. 加载 System Prompt
    system_prompt = load_system_prompt(task)

    # 4. 构造完整的消息列表（包含 System Prompt）
    full_messages = [Message(role="system", content=system_prompt)]
    full_messages.extend(request.messages)

    # 5. 根据请求类型处理
    if request.stream:
        # 流式响应
        async def generate():
            async for chunk in llm_service.chat_stream(full_messages):
                # 流式输出不做安全检查（性能考虑）
                yield f"data: {chunk}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(
            generate(),
            media_type="text/event-stream"
        )
    else:
        # 非流式响应
        content = await llm_service.chat(full_messages)

        # 6. 检查输出安全
        content = PromptGuard.sanitize_output(content, system_prompt)

        return ChatResponse(
            content=content,
            model=settings.DEEPSEEK_MODEL
        )


@router.post("/chat/structured")
async def chat_structured(request: ChatRequest):
    """
    结构化聊天接口

    返回 JSON 格式的响应，包含：
    - answer: 回答内容
    - confidence: 置信度 (0-1)
    - task: 任务类型
    """

    # 获取用户最后一条消息
    user_message = request.messages[-1].content if request.messages else ""

    # 1. 检查输入安全
    is_safe, error_msg = PromptGuard.check_input(user_message)
    if not is_safe:
        return {
            "answer": f"⚠️ {error_msg}",
            "confidence": 0.0,
            "task": "error"
        }

    # 2. 获取任务类型
    task = getattr(request, 'task', 'general') or 'general'

    # 3. 加载 System Prompt
    system_prompt = load_system_prompt(task)

    # 4. 添加结构化输出要求
    structured_prompt = f"""
{system_prompt}

用户问题：{user_message}

请用 JSON 格式输出，格式如下：
{{
    "answer": "你的回答",
    "confidence": 0.8,
    "task": "{task}"
}}

只输出 JSON，不要添加其他内容。
"""

    # 5. 构造消息列表
    full_messages = [Message(role="system", content=structured_prompt)]

    # 6. 调用 AI
    content = await llm_service.chat(full_messages)

    # 7. 检查输出安全
    content = PromptGuard.sanitize_output(content, system_prompt)

    # 8. 解析 JSON
    try:
        # 尝试提取 JSON
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]

        result = json.loads(content.strip())
        return result
    except:
        # 如果解析失败，返回默认格式
        return {
            "answer": content,
            "confidence": 0.5,
            "task": task
        }