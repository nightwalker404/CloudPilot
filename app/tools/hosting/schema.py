VM_SCHEMA = {
    "type": "function",
    "function": {
        "name": "create_vm",
        "description": "Create a virtual machine",
        "parameters": {
            "type": "object",
            "properties": {
                "cpu": {"type": "integer", "description": "CPU cores"},
                "memory": {"type": "integer", "description": "Memory in GB"},
                "disk": {"type": "integer", "description": "Disk in GB"}
            },
            "required": ["cpu", "memory", "disk"]
        }
    }
}