from pydantic import BaseModel
from typing import List, Optional


class Message(BaseModel):
    """单条消息"""
    role: str  # "user" 或 "assistant"
    content: str


class ChatRequest(BaseModel):
    """聊天请求"""
    messages: List[Message]
    stream: bool = True
    task: Optional[str] = "general"  # general, translate, code, analyze


class ChatResponse(BaseModel):
    """聊天响应（非流式）"""
    content: str
    model: str
    usage: Optional[dict] = None
