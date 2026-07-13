from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from models.schemas import ChatRequest, ChatResponse
from services.llm import LLMService
from config import settings

router = APIRouter()

# 创建 LLM 服务实例
llm_service = LLMService(
    api_key=settings.DEEPSEEK_API_KEY,
    base_url=settings.DEEPSEEK_BASE_URL,
    model=settings.DEEPSEEK_MODEL
)


@router.post("/chat")
async def chat(request: ChatRequest):
    """聊天接口"""
    if request.stream:
        # 流式响应
        async def generate():
            async for chunk in llm_service.chat_stream(request.messages):
                yield f"data: {chunk}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(
            generate(),
            media_type="text/event-stream"
        )
    else:
        # 非流式响应
        content = await llm_service.chat(request.messages)
        return ChatResponse(
            content=content,
            model=settings.DEEPSEEK_MODEL
        )