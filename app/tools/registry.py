from tools.hosting import TOOLS_MAP as HOSTING_TOOLS_MAP, TOOLS_SCHEMA as HOSTING_TOOLS_SCHEMA

TOOLS_MAP: dict = {}
TOOLS_MAP.update(HOSTING_TOOLS_MAP)

TOOLS_SCHEMA: dict = {}
TOOLS_SCHEMA.update(HOSTING_TOOLS_SCHEMA)


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