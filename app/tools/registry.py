from app.tools.hosting import create_vm, VM_SCHEMA

# Combine them
TOOLS_MAP = {
    "create_vm": create_vm,
}

# Combine schemas
TOOLS_SCHEMA = [
    VM_SCHEMA,
]

def execute_tool(tool_name: str, tool_args: dict):
    """Execute a tool by name"""
    if tool_name not in TOOLS_MAP:
        return f"Error: Unknown tool {tool_name}"
    
    try:
        tool_func = TOOLS_MAP[tool_name]
        result = tool_func(**tool_args)
        return result
    except Exception as e:
        return f"Error executing {tool_name}: {str(e)}"