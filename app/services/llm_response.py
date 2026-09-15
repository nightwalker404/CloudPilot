import json
import re
from typing import Optional
from fastapi import Request
from app.tools.dispatcher import dispatcher
from app.tools.registry import TOOLS_SCHEMA
from app.prompts import load_prompt
from app.schemas.request import Message
from app.services.mongo_conversation import conversation_store


def extract_tool_call_from_content(content: str) -> dict | None:
    """Fallback parser for models that emit valid tool-call JSON
    without the Ollama <tool_call> wrapper tags.
    """
    if not content:
        return None

    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", content.strip())
    text = re.sub(r"//.*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)

    try:
        data = json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return None

    if isinstance(data, dict) and "name" in data and "arguments" in data:
        return data

    return None


def _messages_to_dict(messages: list[Message]) -> list[dict]:
    result = []
    for msg in messages:
        msg_dict = {"role": msg.role, "content": msg.content}
        if msg.tool_calls:
            msg_dict["tool_calls"] = msg.tool_calls
        if msg.tool_call_id:
            msg_dict["tool_call_id"] = msg.tool_call_id
        result.append(msg_dict)
    return result


def _dict_to_message(data: dict) -> Message:
    return Message(
        role=data.get("role", "assistant"),
        content=data.get("content", ""),
        tool_calls=data.get("tool_calls"),
        tool_call_id=data.get("tool_call_id")
    )


async def llm_service(
    request: Request,
    messages: list[Message],
    conversation_id: Optional[str] = None,
    user_id: str = "anonymous",
    model: Optional[str] = None,
    stream: bool = False,
    temperature: float = 0.7,
    max_tokens: Optional[int] = None
) -> tuple[str, list[Message], Optional[str]]:
    """
    Returns: (response_text, all_messages, conversation_id)
    """
    settings = request.app.state.settings
    client = request.app.state.llm_client
    
    target_model = model or settings.model
    
    system_messages = load_prompt("v2")
    full_messages = system_messages + _messages_to_dict(messages)
    
    response = client.chat(
        model=target_model,
        messages=full_messages,
        stream=stream,
        tools=TOOLS_SCHEMA,
        options={"temperature": temperature, "num_predict": max_tokens} if max_tokens else {"temperature": temperature}
    )
    
    assistant_message = response["message"]
    assistant_msg = _dict_to_message(assistant_message)
    
    result = dispatcher(assistant_message=assistant_message, messages=full_messages + [assistant_message])
    
    if isinstance(result, str):
        final_msg = Message(role="assistant", content=result)
        new_messages = messages + [final_msg]
    else:
        new_messages = messages + [_dict_to_message(msg) for msg in result]
    
    # Determine final message history to save
    if conversation_id:
        existing = await conversation_store.get(conversation_id, user_id)
        if existing:
            # Append new messages to existing history
            all_messages = existing.messages + new_messages
        else:
            all_messages = new_messages
    else:
        all_messages = new_messages
    
    # Save conversation
    if conversation_id:
        existing = await conversation_store.get(conversation_id, user_id)
        if existing:
            await conversation_store.replace_messages(conversation_id, user_id, all_messages)
        else:
            conv = await conversation_store.create(user_id, model=target_model)
            await conversation_store.replace_messages(conv.id, user_id, all_messages)
            conversation_id = conv.id
    else:
        conv = await conversation_store.create(user_id, model=target_model)
        await conversation_store.replace_messages(conv.id, user_id, all_messages)
        conversation_id = conv.id
    
    return result if isinstance(result, str) else result[-1].content, all_messages, conversation_id