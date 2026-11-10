---
name: control-servidor-escriptorium
description: >-
  Control integral del ciclo de vida y operaciones del servidor de eScriptorium y Kraken
  en Google Compute Engine (instancia Spot con GPU NVIDIA T4). Permite a Antigravity
  crear, arrancar, apagar, monitorizar el estado, consultar IPs y revisar tareas de
  reconocimiento/entrenamiento de modelos HTR paleográficos.
---

# Skill: Control del Servidor eScriptorium (GCE Spot VM)

Esta skill permite al agente gestionar de forma 100% autónoma y desatendida la infraestructura en la nube de **eScriptorium + Kraken**:

---

## 1. Parámetros de la Infraestructura

* **Proveedor:** Google Cloud Platform (Compute Engine - GCE).
* **Proyecto:** `gen-lang-client-0513056311`.
* **Zona:** `europe-west1-b` (Bélgica).
* **Nombre de la instancia:** `escriptorium-spot-vm`.
* **Modelo de aprovisionamiento:** `SPOT` (descuento del 60–90%, con parada automática sin pérdida de disco).
* **Hardware:** `n1-standard-4` (4 vCPUs, 15 GB RAM + 16 GB Swap) + 1x **NVIDIA Tesla T4** (16 GB VRAM).
* **Disco:** 120 GB Disco persistente estándar HDD (`pd-standard`, ~4,80 \$/mes), conserva todas las imágenes, XMLs, modelos y base de datos al apagar la VM.
* **Stack Software:** Ubuntu 22.04 LTS, Docker, NVIDIA Container Toolkit, eScriptorium (Django, PostgreSQL, Redis, Celery GPU Worker).

---

## 2. Comandos Operativos Disponibles

El agente ejecutará las operaciones a través del script maestro `scripts/manage_escriptorium_vm.py`:

### A. Consultar Estado
```powershell
.\venv\Scripts\python.exe scripts/manage_escriptorium_vm.py status
```
* Devuelve el JSON con el estado de la máquina: `RUNNING`, `TERMINATED`, `STOPPED` o `NOT_FOUND`, junto a la IP externa.

### B. Crear la Instancia Inicial
```powershell
.\venv\Scripts\python.exe scripts/manage_escriptorium_vm.py create
```
* Despliega la instancia Spot, configura el cortafuegos para el puerto 8080 e inicia la instalación automática mediante el startup script.

### C. Arrancar el Servidor
```powershell
.\venv\Scripts\python.exe scripts/manage_escriptorium_vm.py start
```
* Enciende la máquina Spot. En ~15-20 segundos la IP externa está activa y los contenedores de Docker se reanudan automáticamente.

### D. Apagar el Servidor (Ahorro de Costes)
```powershell
.\venv\Scripts\python.exe scripts/manage_escriptorium_vm.py stop
```
* Detiene la máquina inmediatamente. El coste de CPU, RAM y GPU pasa a ser **0 €/hora**. Solo se mantiene el coste mínimo del disco persistente.

### E. Obtener Enlace de Conexión
```powershell
.\venv\Scripts\python.exe scripts/manage_escriptorium_vm.py ip
```
* Devuelve la IP pública y la URL directa: `http://<IP>:8080`.

---

## 3. Reglas de Comportamiento del Agente

1. **Responsabilidad Económica:** Siempre que el usuario indique que ha terminado de trabajar, o al final de una sesión de entrenamiento, el agente debe verificar si el servidor debe apagarse para no incurrir en costes innecesarios.
2. **Chequeo previo:** Antes de lanzar una petición a eScriptorium, verificar con `status` si la máquina está encendida. Si está apagada, avisar y arrancarla con `start`.
3. **Persistencia:** Todo el trabajo (modelos entrenados en Kraken, proyectos, imágenes subidas y transcripciones) reside en los volúmenes de Docker en el disco persistente estándar HDD (`pd-standard`) de 120 GB; **nunca se pierde al apagar la máquina**.
