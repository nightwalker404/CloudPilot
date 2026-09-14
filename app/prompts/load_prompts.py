import json
from pathlib import Path


def load_prompt(version: str = "v1") -> list[dict]:
    """Load system prompt from prompt_{version}.json"""
    prompt_file = Path(__file__).parent / f"prompt_{version}.json"

    if not prompt_file.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_file}")

    with open(prompt_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    return [data]