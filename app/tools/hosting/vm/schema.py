CREATE_VM_SCHEMA = {
    "type": "function",
    "function": {
        "name": "create_vm",
        "description": "Create a virtual machine",
        "parameters": {
            "type": "object",
            "properties": {
                "cpu": {"type": "integer", "description": "CPU cores (1-64)"},
                "memory": {"type": "integer", "description": "Memory in GB (1-512)"},
                "disk": {"type": "integer", "description": "Disk in GB (10-2000)"},
                "vm_name": {"type": "string", "description": "Name for the VM (optional, auto-generated if omitted)"},
                "os": {"type": "string", "description": "Base OS image alias (ubuntu or debian)"}
            },
            "required": ["cpu", "memory", "disk"]
        }
    }
}

LIST_VMS_SCHEMA = {
    "type": "function",
    "function": {
        "name": "list_vms",
        "description": "List all virtual machines",
        "parameters": {"type": "object", "properties": {}}
    }
}

GET_VM_SCHEMA = {
    "type": "function",
    "function": {
        "name": "get_vm",
        "description": "Get details of a specific VM",
        "parameters": {
            "type": "object",
            "properties": {
                "vm_name": {"type": "string", "description": "Name of the VM"}
            },
            "required": ["vm_name"]
        }
    }
}

DELETE_VM_SCHEMA = {
    "type": "function",
    "function": {
        "name": "delete_vm",
        "description": "Delete a virtual machine",
        "parameters": {
            "type": "object",
            "properties": {
                "vm_name": {"type": "string", "description": "Name of the VM to delete"}
            },
            "required": ["vm_name"]
        }
    }
}

START_VM_SCHEMA = {
    "type": "function",
    "function": {
        "name": "start_vm",
        "description": "Start a virtual machine",
        "parameters": {
            "type": "object",
            "properties": {
                "vm_name": {"type": "string", "description": "Name of the VM to start"}
            },
            "required": ["vm_name"]
        }
    }
}

STOP_VM_SCHEMA = {
    "type": "function",
    "function": {
        "name": "stop_vm",
        "description": "Stop a virtual machine",
        "parameters": {
            "type": "object",
            "properties": {
                "vm_name": {"type": "string", "description": "Name of the VM to stop"}
            },
            "required": ["vm_name"]
        }
    }
}

VM_SCHEMA = CREATE_VM_SCHEMA

TOOLS_SCHEMA = [
    CREATE_VM_SCHEMA,
    LIST_VMS_SCHEMA,
    GET_VM_SCHEMA,
    DELETE_VM_SCHEMA,
    START_VM_SCHEMA,
    STOP_VM_SCHEMA,
]