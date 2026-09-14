from core import get_logger, setup_logging

from ollama import Client

from core import get_settings
from prompts import load_prompt
from tools import TOOLS_MAP, TOOLS_SCHEMA, execute_tool
from services import extract_tool_call_from_content

setup_logging()
logger = get_logger(__name__)

settings = get_settings()
client = Client(host=settings.llm_base_url)


def main():
    messages = load_prompt("v2")

    while True:
        user_input = input("User: ")

        if user_input.lower() in ["exit", "quit"]:
            print("Exiting...")
            break

        messages.append({
            "role": "user",
            "content": user_input,
        })

        response = client.chat(
            model=settings.model,
            messages=messages,
            stream=False,
            tools=TOOLS_SCHEMA
        )

        assistant_message = response["message"]

        if assistant_message.get("tool_calls"):
            messages.append(assistant_message)
            for tool_call in assistant_message["tool_calls"]:
                tool_name = tool_call["function"]["name"]
                tool_args = tool_call["function"]["arguments"]
                result = execute_tool(tool_name, tool_args)
                messages.append({"role": "tool", "content": str(result)})
        else:
            content = assistant_message["content"]
            parsed = extract_tool_call_from_content(content)
            if parsed:
                messages.append({"role": "assistant", "content": content})
                result = execute_tool(parsed["name"], parsed["arguments"])
                messages.append({"role": "tool", "content": str(result)})
            else:
                result = content
                messages.append({"role": "assistant", "content": content})

        print(f"AI: {result}")

if __name__ == "__main__":
    main()