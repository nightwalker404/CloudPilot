import json
import re
from app.tools import dispatcher
from app.prompts import load_prompt
from fastapi import Request
from app.tools import TOOLS_SCHEMA

def extract_tool_call_from_content(content: str) -> dict | None:
    """Fallback parser for models that emit valid tool-call JSON
    without the Ollama <tool_call> wrapper tags.
    """
    if not content:
        return None

    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", content.strip())

    try:
        data = json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return None

    if isinstance(data, dict) and "name" in data and "arguments" in data:
        return data

    return None

def llm_service(prompt: str, request: Request) -> str:
    messages = load_prompt("v2")
    messages.append({
        "role": "user",
        "content": prompt,
    })

    response = request.app.state.llm_client.chat(
        model=request.app.state.settings.model,
        messages=messages,
        stream=False,
        tools=TOOLS_SCHEMA
    )

    assistant_message = response["message"]

    result = dispatcher(assistant_message=assistant_message, messages=messages)

    return result