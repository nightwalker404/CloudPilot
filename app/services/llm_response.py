import json
import re


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