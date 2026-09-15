from .vm import (
    create_vm, list_vms, get_vm, delete_vm, start_vm, stop_vm,
    CREATE_VM_SCHEMA, LIST_VMS_SCHEMA, GET_VM_SCHEMA, DELETE_VM_SCHEMA, START_VM_SCHEMA, STOP_VM_SCHEMA
)

# Combine them
TOOLS_MAP = {
    "create_vm": create_vm,
    "list_vms": list_vms,
    "get_vm": get_vm,
    "delete_vm": delete_vm,
    "start_vm": start_vm,
    "stop_vm": stop_vm,
}

# Combine schemas
TOOLS_SCHEMA = [
    CREATE_VM_SCHEMA,
    LIST_VMS_SCHEMA,
    GET_VM_SCHEMA,
    DELETE_VM_SCHEMA,
    START_VM_SCHEMA,
    STOP_VM_SCHEMA,
]