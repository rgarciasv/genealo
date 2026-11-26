#!/bin/bash
set -e
exec > /var/log/escriptorium_bootstrap.log 2>&1

echo "=== [1/5] Configurando Swap de 16GB ==="
if [ ! -f /swapfile ]; then
    fallocate -l 16G /swapfile
    chmod 600 /swapfile
    mkswap /swapfile
    swapon /swapfile
    echo '/swapfile none swap sw 0 0' >> /etc/fstab
else
    swapon /swapfile || true
fi

echo "=== [2/5] Instalando paquetes base y Docker ==="
export DEBIAN_FRONTEND=noninteractive
if ! command -v docker &> /dev/null; then
    apt-get update
    apt-get install -y git curl wget ca-certificates gnupg lsb-release htop tmux jq
    mkdir -m 0755 -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
    apt-get update
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    systemctl enable docker
    systemctl start docker
fi

echo "=== [3/5] Comprobando si hay GPU NVIDIA presente ==="
if lspci | grep -i nvidia &> /dev/null; then
    echo "GPU NVIDIA detectada. Comprobando drivers y nvidia-container-toolkit..."
    if ! command -v nvidia-smi &> /dev/null; then
        apt-get update
        apt-get install -y linux-headers-$(uname -r) nvidia-driver-535 nvidia-utils-535
        curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
        curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
            sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
            tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
        apt-get update
        apt-get install -y nvidia-container-toolkit
        nvidia-ctk runtime configure --runtime=docker
        systemctl restart docker
    fi
else
    echo "Modo solo CPU activo (ahorro de costes ~0,05 $/h)."
fi

echo "=== [4/5] Clonando y configurando eScriptorium ==="
mkdir -p /opt/escriptorium
cd /opt/escriptorium

if [ ! -d "/opt/escriptorium/.git" ]; then
    git clone https://gitlab.com/scripta/escriptorium.git /opt/escriptorium
fi

EXT_IP=$(curl -s -H "Metadata-Flavor: Google" http://metadata.google.internal/computeMetadata/v1/instance/network-interfaces/0/access-configs/0/external-ip || echo "localhost")

if [ ! -f "variables.env" ]; then
    cp variables.env_example variables.env
    SECRET_KEY=$(tr -dc 'a-zA-Z0-9' < /dev/urandom | head -c 50)
    sed -i "s/^SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" variables.env || echo "SECRET_KEY=$SECRET_KEY" >> variables.env
    echo "ALLOWED_HOSTS=*" >> variables.env
    echo "CSRF_TRUSTED_ORIGINS=http://$EXT_IP,http://$EXT_IP:8080,http://localhost:8080,http://127.0.0.1:8080" >> variables.env
else
    sed -i "s|^CSRF_TRUSTED_ORIGINS=.*|CSRF_TRUSTED_ORIGINS=http://$EXT_IP,http://$EXT_IP:8080,http://localhost:8080,http://127.0.0.1:8080|" variables.env
fi

# Exponer tanto en el puerto 80 como en el 8080 para acceso directo o por túnel
cat << 'EOF' > docker-compose.override.yml
services:
  nginx:
    ports:
      - "80:80"
      - "8080:80"
EOF

echo "=== [5/5] Levantando contenedores de eScriptorium ==="
docker compose pull
docker compose up -d

echo "=== Despliegue de eScriptorium completado a las $(date) ==="
