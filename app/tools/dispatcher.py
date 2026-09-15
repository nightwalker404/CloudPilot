from app.tools.registry import execute_tool 

def dispatcher(assistant_message, messages):
    from app.services.llm_response import extract_tool_call_from_content
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
    return result