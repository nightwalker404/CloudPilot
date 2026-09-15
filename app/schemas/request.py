from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class Message(BaseModel):
    role: str
    content: str
    tool_calls: Optional[list] = None
    tool_call_id: Optional[str] = None


class ChatRequest(BaseModel):
    messages: list[Message]
    conversation_id: Optional[str] = None
    model: Optional[str] = None
    stream: bool = False
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=None, ge=1)

