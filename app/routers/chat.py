from fastapi import APIRouter
from app.schemas.reponse import ChatResponse
from app.schemas.request import ChatRequest
from app.services.llm_response import llm_service

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat(prompt: ChatRequest):
    result: str = llm_service(prompt)
    ChatResponse.response = result
    return ChatResponse