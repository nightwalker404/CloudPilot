from fastapi import APIRouter, Request, Depends, HTTPException, status
from app.schemas.reponse import ChatResponse
from app.schemas.request import ChatRequest, Message
from app.services.llm_response import llm_service
from app.services.mongo_conversation import conversation_store

router = APIRouter()


async def get_current_user(request: Request) -> str:
    user_id = request.headers.get("X-User-ID")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-User-ID header"
        )
    return user_id


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: Request,
    payload: ChatRequest,
    user_id: str = Depends(get_current_user)
):
    conversation_id = payload.conversation_id
    
    if conversation_id:
        existing = await conversation_store.get(conversation_id, user_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        messages = existing.messages + payload.messages
    else:
        messages = payload.messages
    
    response_text, all_messages, conv_id = await llm_service(
        request=request,
        messages=messages,
        conversation_id=conversation_id,
        user_id=user_id,
        model=payload.model,
        stream=payload.stream,
        temperature=payload.temperature,
        max_tokens=payload.max_tokens
    )
    
    last_assistant_msg = next((m for m in reversed(all_messages) if m.role == "assistant"), None)
    
    return ChatResponse(
        response=response_text,
        conversation_id=conv_id,
        message=last_assistant_msg or Message(role="assistant", content=response_text),
        tool_calls=last_assistant_msg.tool_calls if last_assistant_msg else None
    )


@router.post("/conversations")
async def create_conversation(
    request: Request,
    user_id: str = Depends(get_current_user)
):
    conv = await conversation_store.create(user_id)
    return {"id": conv.id, "title": conv.title, "created_at": conv.created_at.isoformat()}


@router.get("/conversations")
async def list_conversations(
    user_id: str = Depends(get_current_user)
):
    convs = await conversation_store.list_user_conversations(user_id)
    return [
        {"id": c.id, "title": c.title, "created_at": c.created_at.isoformat(), "updated_at": c.updated_at.isoformat()}
        for c in convs
    ]


@router.get("/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    user_id: str = Depends(get_current_user)
):
    conv = await conversation_store.get(conversation_id, user_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {
        "id": conv.id,
        "title": conv.title,
        "messages": [{"role": m.role, "content": m.content, "tool_calls": m.tool_calls} for m in conv.messages],
        "created_at": conv.created_at.isoformat(),
        "updated_at": conv.updated_at.isoformat()
    }


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    user_id: str = Depends(get_current_user)
):
    success = await conversation_store.delete(conversation_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"deleted": True}