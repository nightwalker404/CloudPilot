import time
import requests
from app.core import get_settings
from .cloud_init.loader import load_cloud_init_yaml


settings = get_settings()

import re

def _sanitize_vm_name(name: str) -> str:
    name = re.sub(r"[^a-zA-Z0-9-]", "-", name.strip())
    name = re.sub(r"-+", "-", name).strip("-")
    return name.lower()

def _validate_vm_params(cpu: int, memory: int, disk: int):
    if not isinstance(cpu, int) or cpu < 1 or cpu > 64:
        raise ValueError("cpu must be an integer between 1 and 64")
    if not isinstance(memory, int) or memory < 1 or memory > 512:
        raise ValueError("memory must be an integer between 1 and 512 GB")
    if not isinstance(disk, int) or disk < 10 or disk > 2000:
        raise ValueError("disk must be an integer between 10 and 2000 GB")

def _incus_request(method: str, path: str, json: dict | None = None):
    response = requests.request(
        method,
        f"{settings.incus_url}{path}",
        cert=(str(settings.CLIENT_CERT), str(settings.CLIENT_KEY)),
        json=json,
        verify=str(settings.SERVER_CERT),
    )
    if not response.ok:
        try:
            detail = response.json().get("error", response.text)
        except ValueError:
            detail = response.text
        raise RuntimeError(f"Incus request failed ({response.status_code}): {detail}")

    data = response.json()
    if data.get("type") == "error":
        raise RuntimeError(f"Incus error: {data.get('error', 'unknown error')}")
    return data

def _wait_for_operation(operation_url: str, timeout: int = 60) -> dict:
    result = _incus_request("GET", f"{operation_url}/wait?timeout={timeout}")
    metadata = result.get("metadata") or {}
    if metadata.get("status") != "Success":
        err = metadata.get("err") or "unknown error"
        raise RuntimeError(f"Incus operation failed: {err}")
    return result

def request_to_incus():
    return _incus_request("GET", "/1.0")

def _get_instance_ip(vm_name: str, retries: int = 15, delay: int = 2) -> str | None:
    for _ in range(retries):
        state = _incus_request("GET", f"/1.0/instances/{vm_name}/state")
        network = state.get("metadata", {}).get("network") or {}
        for iface, data in network.items():
            if iface == "lo":
                continue
            for addr in data.get("addresses", []):
                if addr.get("family") == "inet":
                    return addr.get("address")
        time.sleep(delay)
    return None

def _get_instance_full(vm_name: str) -> dict:
    return _incus_request("GET", f"/1.0/instances/{vm_name}")

def _list_instances() -> list[dict]:
    result = _incus_request("GET", "/1.0/instances?recursion=1")
    return result.get("metadata", [])

def create_vm(cpu: int, memory: int, disk: int, vm_name: str = "", os: str = "ubuntu") -> str:
    """Create a virtual machine"""
    _validate_vm_params(cpu, memory, disk)
    
    if not os or os not in ["ubuntu", "debian"]:
        os = "ubuntu"

    os_label = os 
    image_alias = "ubuntu:24.04" if os == "ubuntu" else os  

    if not vm_name.strip():
        vm_name = f"{os}-{time.strftime('%Y%m%d%H%M%S')}"
    else:
        vm_name = _sanitize_vm_name(vm_name)

    cloud_init_config, auth = load_cloud_init_yaml(os_label)
    username, password = auth

    payload = {
        "name": vm_name,
        "type": "virtual-machine",
        "source": {"type": "image", "alias": image_alias},
        "config": {
            "limits.cpu": str(cpu),
            "limits.memory": f"{memory}GB",
            "user.user-data": cloud_init_config,
        },
        "devices": {
            "root": {
                "path": "/",
                "pool": "default",
                "type": "disk",
                "size": f"{disk}GB",
            }
        },
    }

    result = _incus_request("POST", "/1.0/instances", json=payload)
    if operation_url := result.get("operation"):
        _wait_for_operation(operation_url)

    _incus_request("PUT", f"/1.0/instances/{vm_name}/state", json={"action": "start", "timeout": 30})

    ip = _get_instance_ip(vm_name)

    return (
        f"✅ VM '{vm_name}' created successfully!\n"
        f"   OS: {os}   •   CPU: {cpu} vCPU   •   RAM: {memory}GB   •   Disk: {disk}GB\n"
        f"   Username: {username}\n"
        f"   Password: {password}\n"
        f"   IP: {ip or 'not assigned yet — check again shortly'}"
    )

def list_vms() -> str:
    """List all virtual machines"""
    instances = _list_instances()
    if not instances:
        return "No VMs found."
    
    lines = ["📋 Virtual Machines:"]
    for inst in instances:
        name = inst.get("name", "unknown")
        status = inst.get("status", "unknown")
        type_ = inst.get("type", "unknown")
        location = inst.get("location", "local")
        lines.append(f"  • {name} ({type_}) - {status} [{location}]")
    return "\n".join(lines)

def get_vm(vm_name: str) -> str:
    """Get details of a specific VM"""
    try:
        inst = _get_instance_full(vm_name)
        name = inst.get("name", vm_name)
        status = inst.get("status", "unknown")
        type_ = inst.get("type", "unknown")
        config = inst.get("config", {})
        cpu = config.get("limits.cpu", "?")
        memory = config.get("limits.memory", "?")
        devices = inst.get("devices", {})
        root_disk = devices.get("root", {}).get("size", "?")
        location = inst.get("location", "local")
        
        ip = _get_instance_ip(vm_name)
        
        return (
            f"🖥️ VM: {name}\n"
            f"   Status: {status}\n"
            f"   Type: {type_}\n"
            f"   CPU: {cpu} vCPU\n"
            f"   RAM: {memory}\n"
            f"   Disk: {root_disk}\n"
            f"   Location: {location}\n"
            f"   IP: {ip or 'not assigned'}"
        )
    except RuntimeError as e:
        if "404" in str(e):
            return f"❌ VM '{vm_name}' not found"
        raise

def delete_vm(vm_name: str) -> str:
    """Delete a virtual machine"""
    try:
        # Stop first if running
        try:
            state = _incus_request("GET", f"/1.0/instances/{vm_name}/state")
            if state.get("metadata", {}).get("status") == "Running":
                _incus_request("PUT", f"/1.0/instances/{vm_name}/state", json={"action": "stop", "timeout": 30})
                _wait_for_operation(f"/1.0/operations/{state.get('metadata', {}).get('operation', '')}")
        except:
            pass
        
        result = _incus_request("DELETE", f"/1.0/instances/{vm_name}")
        if operation_url := result.get("operation"):
            _wait_for_operation(operation_url)
        return f"✅ VM '{vm_name}' deleted successfully"
    except RuntimeError as e:
        if "404" in str(e):
            return f"❌ VM '{vm_name}' not found"
        raise

def start_vm(vm_name: str) -> str:
    """Start a virtual machine"""
    try:
        result = _incus_request("PUT", f"/1.0/instances/{vm_name}/state", json={"action": "start", "timeout": 30})
        if operation_url := result.get("operation"):
            _wait_for_operation(operation_url)
        return f"✅ VM '{vm_name}' started"
    except RuntimeError as e:
        if "404" in str(e):
            return f"❌ VM '{vm_name}' not found"
        raise

def stop_vm(vm_name: str) -> str:
    """Stop a virtual machine"""
    try:
        result = _incus_request("PUT", f"/1.0/instances/{vm_name}/state", json={"action": "stop", "timeout": 30})
        if operation_url := result.get("operation"):
            _wait_for_operation(operation_url)
        return f"✅ VM '{vm_name}' stopped"
    except RuntimeError as e:
        if "404" in str(e):
            return f"❌ VM '{vm_name}' not found"
        raise