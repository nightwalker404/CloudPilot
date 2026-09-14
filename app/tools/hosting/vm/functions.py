import time
import requests
from app.core import get_settings

settings = get_settings()

def _incus_request(method: str, path: str, json: dict | None = None):
    response = requests.request(
        method,
        f"https://127.0.0.1:8443{path}",
        cert=(str(settings.CLIENT_CERT), str(settings.CLIENT_KEY)),
        json=json,
        verify=False,
    )
    response.raise_for_status()
    return response.json()

def request_to_incus():
    return _incus_request("GET", "/1.0")

def create_vm(cpu: int, memory: int, disk: int, vm_name: str = "", os: str = "ubuntu") -> str:
    """Create a virtual machine"""
    if cpu < 1 or memory < 1 or disk < 1:
        raise ValueError("cpu, memory and disk must all be positive")

    if os not in ["ubuntu", "debian"]: # we will read this from db in future
        raise ValueError("os must be one of 'ubuntu', 'debian', or 'centos'")

    if not vm_name.strip():
        vm_name = f"{os}-{time.strftime('%Y%m%d%H%M%S')}"

    payload = {
        "name": vm_name,
        "type": "virtual-machine",
        "source": {"type": "image", "alias": os},
        "config": {
            "limits.cpu": str(cpu),
            "limits.memory": f"{memory}GB",
        },
        "devices": {
            "root": {
                "path": "/",
                "pool": "default",  # adjust to your actual storage pool name
                "type": "disk",
                "size": f"{disk}GB",
            }
        },
    }

    result = _incus_request("POST", "/1.0/instances", json=payload)
    return f"VM '{vm_name}' creation started — {cpu} vCPU, {memory}GB RAM, {disk}GB disk, {os}."