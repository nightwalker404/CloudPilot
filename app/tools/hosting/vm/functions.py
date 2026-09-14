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

def _incus_request(method: str, path: str, json: dict | None = None):
    response = requests.request(
        method,
        f"{settings.INCUS_URL}{path}",
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

def create_vm(cpu: int, memory: int, disk: int, vm_name: str = "", os: str = "ubuntu") -> str:
    """Create a virtual machine"""
    for name, value in (("cpu", cpu), ("memory", memory), ("disk", disk)):
        if not isinstance(value, (int, float)):
            raise ValueError(f"{name} must be a number, got {type(value).__name__}: {value!r}")
    
    if os not in ["ubuntu", "debian"]: # we will read this from db in future
        raise ValueError("os must be one of 'ubuntu', 'debian', or 'centos'")

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
        f"VM '{vm_name}' created — {cpu} vCPU, {memory}GB RAM, {disk}GB disk, {os}.\n"
        f"Username: {username}\n"
        f"Password: {password}\n"
        f"IP address: {ip or 'not assigned yet — check again shortly'}"
    )