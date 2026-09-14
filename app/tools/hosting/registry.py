from app.tools.hosting import create_vm, VM_SCHEMA

# Combine them
TOOLS_MAP = {
    "create_vm": create_vm,
}

# Combine schemas
TOOLS_SCHEMA = [
    VM_SCHEMA,
]