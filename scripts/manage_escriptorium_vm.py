#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Manager CLI for eScriptorium + Kraken Spot VM on Google Compute Engine (GCE).
Allows Antigravity and user to create, start, stop, monitor, and tunnel to the VM.
"""

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration Constants
# ---------------------------------------------------------------------------
PROJECT_ID = "gen-lang-client-0513056311"
DEFAULT_ZONE = "europe-west1-b"
INSTANCE_NAME = "escriptorium-spot-vm"
MACHINE_TYPE = "n1-standard-4"  # 4 vCPU, 15 GB RAM
ACCELERATOR = "type=nvidia-tesla-t4,count=1"
DISK_SIZE_GB = 120
DISK_TYPE = "pd-standard"  # Disco persistente estándar (HDD): ~0.04 $/GB/mes (~4,80 $/mes por 120 GB)
IMAGE_PROJECT = "ubuntu-os-cloud"
IMAGE_FAMILY = "ubuntu-2204-lts"

GCLOUD_PATHS = [
    r"C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd",
    r"C:\Program Files\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd",
    "gcloud",
]

def find_gcloud() -> str:
    for path in GCLOUD_PATHS:
        if os.path.isabs(path) and os.path.exists(path):
            return path
    return "gcloud"

GCLOUD_CMD = find_gcloud()

STARTUP_SCRIPT = """#!/bin/bash
set -e
exec > /var/log/escriptorium_bootstrap.log 2>&1

echo "=== [1/6] Actualizando paquetes del sistema ==="
export DEBIAN_FRONTEND=noninteractive
apt-get update && apt-get upgrade -y
apt-get install -y git curl wget ca-certificates gnupg lsb-release htop tmux jq

echo "=== [2/6] Configurando Swap de 16GB ==="
if [ ! -f /swapfile ]; then
    fallocate -l 16G /swapfile
    chmod 600 /swapfile
    mkswap /swapfile
    swapon /swapfile
    echo '/swapfile none swap sw 0 0' >> /etc/fstab
fi

echo "=== [3/6] Instalando Drivers NVIDIA y CUDA ==="
apt-get install -y linux-headers-$(uname -r)
add-apt-repository -y ppa:graphics-drivers/ppa
apt-get update
apt-get install -y nvidia-driver-535 nvidia-utils-535

echo "=== [4/6] Instalando Docker y Docker Compose ==="
mkdir -m 0755 -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

echo "=== [5/6] Instalando NVIDIA Container Toolkit (nvidia-docker) ==="
curl -fsSL https://native-cloud.gitlab.io/nvidia-container-toolkit/gpgkey | gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg || \\
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \\
    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \\
    tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
apt-get update
apt-get install -y nvidia-container-toolkit
nvidia-ctk runtime configure --runtime=docker
systemctl restart docker

echo "=== [6/6] Desplegando eScriptorium ==="
mkdir -p /opt/escriptorium
cd /opt/escriptorium

if [ ! -d "/opt/escriptorium/.git" ]; then
    git clone https://gitlab.com/scripta/escriptorium.git /opt/escriptorium
fi

if [ ! -f "variables.env" ]; then
    cp variables.env_example variables.env
    SECRET_KEY=$(tr -dc 'a-zA-Z0-9!@#$%^&*(-_=+)' < /dev/urandom | head -c 50)
    sed -i "s/^SECRET_KEY=.*/SECRET_KEY='$SECRET_KEY'/" variables.env
fi

cat << 'EOF' > docker-compose.override.yml
services:
  celery-gpu:
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    shm_size: '4gb'
    environment:
      - KRAKEN_TRAINING_DEVICE=cuda:0
      - NVIDIA_VISIBLE_DEVICES=all
      - NVIDIA_DRIVER_CAPABILITIES=all
EOF

docker compose up -d

echo "=== Despliegue completado con éxito a las $(date) ==="
"""

def run_cmd(cmd_list, capture=True, check=True):
    print(f"[RUN] {' '.join(cmd_list)}")
    res = subprocess.run(
        cmd_list,
        capture_output=capture,
        text=True,
        encoding="utf-8",
        errors="replace"
    )
    if check and res.returncode != 0:
        err_msg = res.stderr.strip() if res.stderr else res.stdout.strip()
        print(f"[ERROR] Command failed with code {res.returncode}:\n{err_msg}", file=sys.stderr)
        raise RuntimeError(err_msg)
    return res

def get_status(zone=DEFAULT_ZONE):
    cmd = [
        GCLOUD_CMD, "compute", "instances", "describe", INSTANCE_NAME,
        f"--project={PROJECT_ID}",
        f"--zone={zone}",
        "--format=json"
    ]
    res = run_cmd(cmd, capture=True, check=False)
    if res.returncode != 0:
        if "not found" in res.stderr.lower():
            return {"exists": False, "status": "NOT_FOUND"}
        raise RuntimeError(res.stderr.strip())
    
    data = json.loads(res.stdout)
    status = data.get("status", "UNKNOWN")
    
    # Get external IP
    ext_ip = "None"
    try:
        net_interfaces = data.get("networkInterfaces", [])
        if net_interfaces:
            access_configs = net_interfaces[0].get("accessConfigs", [])
            if access_configs:
                ext_ip = access_configs[0].get("natIP", "None")
    except Exception:
        pass

    scheduling = data.get("scheduling", {})
    prov_model = scheduling.get("provisioningModel", "STANDARD")
    machine = data.get("machineType", "").split("/")[-1]
    
    return {
        "exists": True,
        "status": status,
        "ip": ext_ip,
        "machine_type": machine,
        "provisioning_model": prov_model,
        "zone": zone,
    }

def cmd_create(args):
    print(f"=== Creando Instancia Spot '{INSTANCE_NAME}' ===")
    status_info = get_status(args.zone)
    if status_info.get("exists"):
        print(f"La instancia '{INSTANCE_NAME}' ya existe (Estado: {status_info['status']}).")
        return

    # Write startup script to temp file
    temp_script = Path("scripts") / "startup_escriptorium.sh"
    temp_script.write_text(STARTUP_SCRIPT, encoding="utf-8")

    cmd = [
        GCLOUD_CMD, "compute", "instances", "create", INSTANCE_NAME,
        f"--project={PROJECT_ID}",
        f"--zone={args.zone}",
        f"--machine-type={MACHINE_TYPE}",
        f"--accelerator={ACCELERATOR}",
        "--provisioning-model=SPOT",
        "--instance-termination-action=STOP",
        "--maintenance-policy=TERMINATE",
        f"--boot-disk-size={DISK_SIZE_GB}GB",
        f"--boot-disk-type={DISK_TYPE}",
        f"--image-project={IMAGE_PROJECT}",
        f"--image-family={IMAGE_FAMILY}",
        f"--metadata-from-file=startup-script={temp_script.resolve()}",
        "--tags=http-server,https-server,escriptorium-server"
    ]
    
    print("Invocando gcloud compute instances create con modelo SPOT...")
    run_cmd(cmd, capture=False, check=True)
    print("\nInstancia creada con éxito.")
    
    # Ensure firewall rule exists for port 8080
    ensure_firewall()
    
    time.sleep(3)
    info = get_status(args.zone)
    print(f"\nEstado actual: {info['status']}")
    print(f"IP Externa: {info['ip']}")
    print(f"URL eScriptorium: http://{info['ip']}:8080")
    print("Nota: El script de inicialización tardará entre 3 y 5 minutos en instalar drivers y Docker.")

def ensure_firewall():
    rule_name = "allow-escriptorium-8080"
    print(f"Comprobando regla de cortafuegos '{rule_name}'...")
    check_cmd = [
        GCLOUD_CMD, "compute", "firewall-rules", "describe", rule_name,
        f"--project={PROJECT_ID}", "--format=value(name)"
    ]
    res = run_cmd(check_cmd, capture=True, check=False)
    if res.returncode == 0:
        print(f"Regla de firewall '{rule_name}' ya activa.")
        return

    create_cmd = [
        GCLOUD_CMD, "compute", "firewall-rules", "create", rule_name,
        f"--project={PROJECT_ID}",
        "--direction=INGRESS",
        "--priority=1000",
        "--network=default",
        "--action=ALLOW",
        "--rules=tcp:8080",
        "--source-ranges=0.0.0.0/0",
        "--target-tags=escriptorium-server",
        "--description=Permitir acceso web a eScriptorium puerto 8080"
    ]
    run_cmd(create_cmd, capture=True, check=True)
    print(f"Regla de firewall '{rule_name}' creada exitosamente.")

def cmd_start(args):
    print(f"=== Arrancando instancia '{INSTANCE_NAME}' ===")
    cmd = [
        GCLOUD_CMD, "compute", "instances", "start", INSTANCE_NAME,
        f"--project={PROJECT_ID}",
        f"--zone={args.zone}"
    ]
    run_cmd(cmd, capture=False, check=True)
    time.sleep(2)
    info = get_status(args.zone)
    print(f"\nInstancia iniciada: {info['status']}")
    print(f"IP Externa: {info['ip']}")
    print(f"URL de acceso: http://{info['ip']}:8080")

def cmd_stop(args):
    print(f"=== Deteniendo instancia '{INSTANCE_NAME}' (para evitar costes) ===")
    cmd = [
        GCLOUD_CMD, "compute", "instances", "stop", INSTANCE_NAME,
        f"--project={PROJECT_ID}",
        f"--zone={args.zone}"
    ]
    run_cmd(cmd, capture=False, check=True)
    print("Instancia detenida correctamente. No consume cómputo ni GPU.")

def cmd_status(args):
    info = get_status(args.zone)
    print(json.dumps(info, indent=2))

def cmd_ip(args):
    info = get_status(args.zone)
    if not info.get("exists"):
        print("La instancia no existe.")
    elif info["status"] != "RUNNING":
        print(f"La instancia existe pero está en estado: {info['status']}")
    else:
        print(f"IP: {info['ip']}")
        print(f"URL: http://{info['ip']}:8080")

def cmd_tunnel(args):
    print(f"=== Abriendo túnel SSH a {INSTANCE_NAME}:8080 -> localhost:8080 ===")
    cmd = [
        GCLOUD_CMD, "compute", "ssh", INSTANCE_NAME,
        f"--project={PROJECT_ID}",
        f"--zone={args.zone}",
        "--", "-N", "-L", "8080:localhost:8080"
    ]
    print("El túnel quedará abierto. Accede a http://localhost:8080 en tu navegador local.")
    print("Presiona Ctrl+C para cerrarlo cuando termines.")
    subprocess.run(cmd)

def main():
    parser = argparse.ArgumentParser(description="eScriptorium Spot VM Manager")
    parser.add_argument("--zone", default=DEFAULT_ZONE, help="GCP Zone (default: europe-west1-b)")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("create", help="Crear la instancia Spot con GPU y eScriptorium")
    subparsers.add_parser("start", help="Arrancar la instancia apagada")
    subparsers.add_parser("stop", help="Apagar la instancia para no gastar")
    subparsers.add_parser("status", help="Comprobar estado actual de la instancia")
    subparsers.add_parser("ip", help="Obtener IP pública y enlace web")
    subparsers.add_parser("tunnel", help="Conectar túnel seguro SSH a http://localhost:8080")

    args = parser.parse_args()
    if args.command == "create":
        cmd_create(args)
    elif args.command == "start":
        cmd_start(args)
    elif args.command == "stop":
        cmd_stop(args)
    elif args.command == "status":
        cmd_status(args)
    elif args.command == "ip":
        cmd_ip(args)
    elif args.command == "tunnel":
        cmd_tunnel(args)

if __name__ == "__main__":
    main()
