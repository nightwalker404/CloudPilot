from pydantic import BaseModel, Field
from typing import Optional
from app.schemas.request import Message


class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    message: Message
    tool_calls: Optional[list] = None
    usage: Optional[dict] = None