from pathlib import Path
import yaml
import string
import secrets


def _generate_password(length: int = 16) -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def _load_cloud_init_template(os: str) -> dict:
    base_dir = Path(__file__).parent
    template_file = base_dir / f"{os}.yaml"

    if not template_file.exists():
        raise FileNotFoundError(f"Cloud-init template not found: {template_file}")

    with open(template_file, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _generate_cloud_init_with_password(os: str) -> str:
    template = _load_cloud_init_template(os)

    password = _generate_password()

    if "chpasswd" not in template:
        template["chpasswd"] = {}

    template["chpasswd"]["list"] = f"{os}:{password}"
    template["chpasswd"]["expire"] = False
    template["ssh_pwauth"] = True

    template_str: str = yaml.dump(template)
    return template_str


def load_cloud_init_yaml(os: str) -> str | tuple[str, str]:
    cloud_init_yaml = _generate_cloud_init_with_password(os)
    return cloud_init_yaml, (os, _generate_password())