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
                "disk": {"type": "integer", "description": "Disk in GB"},
                "vm_name": {"type": "string", "description": "Name for the VM (optional, auto-generated if omitted)"},
                "os": {"type": "string", "description": "Base OS image alias (validated separately before this is called)"}
            },
            "required": ["cpu", "memory", "disk"]
        }
    }
}