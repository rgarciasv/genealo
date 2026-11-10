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
* **Hardware:** `n1-standard-4` (4 vCPUs, 15 GB RAM + 16 GB Swap) + soporte opcional para **NVIDIA Tesla T4** (16 GB VRAM).
* **Disco:** 120 GB Disco persistente estándar HDD (`pd-standard`, ~4,80 \$/mes), conserva todas las imágenes, XMLs, modelos y base de datos al apagar la VM.
* **Stack Software:** Ubuntu 22.04 LTS, Docker CE, Docker Compose (11 contenedores activos: `web`, `db` PostgreSQL, `redis`, `nginx`, `channelserver`, `flower`, workers de Celery).

---

## 2. Modelos HTR Pre-entrenados Registrados en la Instancia

La instancia cuenta con 5 modelos registrados en la base de datos de eScriptorium (`core_ocrmodel`), listos para inferencia y fine-tuning:

| ID Modelo | Nombre Canónico | Ámbito de Especialidad | Rendimiento Zero-Shot Observado |
| :---: | :--- | :--- | :--- |
| **`2`** | **TRIDIS (Documental y Notarial s.XII-XVI)** | Notaría, pleitos y registros parroquiales ibéricos (s. XII–XVI). **Modelo Rector**. | **Excelente en s. XVIII (~85–90%)**; captura fórmulas, nombres y citas al folio. En s. XVII extrae anclas aisladas (~40%). |
| **`3`** | **CATMuS Medieval (Castellano y Latín s.XIII-XVI)** | Códices góticos, humanísticos y romances medievales (+113.000 líneas). | Tiende a producir pseudo-latín o formas medievales arcaizantes en manuscritos modernos. |
| **`4`** | **McCATMuS (Español y Romance s.XVI-XIX)** | Corpus romance diacrónico en Unicode NFD estricto con `ſ` larga. | Moderado en s. XVIII (~60%). Colisiona con abreviaturas y genera ruido ortográfico por la `ſ`. |
| **`5`** | **CREMMA ManuMcFondue (Manuscritos Modernos s.XVI-XIX)** | Manuscritos modernos franceses/europeos (proyectos FoNDUE / Gallicorpora). | Moderado (~55%). Tiende a galicismos fonéticos en español al carecer de léxico notarial ibérico. |
| **`6`** | **Lectaurep Base (Administrativo y Notarial s.XVIII-XX)** | Tablas notariales y registros administrativos franceses. | Especializado en registros tabulares; no recomendado para prosa parroquial continua. |

---

## 3. Comandos Operativos Disponibles

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
* Devuelve la IP pública y la URL directa: `http://<IP>:8080` (Credenciales: `admin` / `admin`).

---

## 4. Reglas y Lecciones Operativas (`[L-36]` a `[L-40]`)

1. **Responsabilidad Económica y Ciclo de Vida (`[L-36]`):** Siempre que se termine una sesión de trabajo o inferencia, la VM Spot debe apagarse con `stop`. En estado `TERMINATED` el coste horario de cómputo es exactamente **0,00 \$/h**.
2. **Modelo Rector TRIDIS (`[L-37]`):** Para cualquier tarea de inferencia en frío o como base para reentrenamientos (*fine-tuning*) en el archivo parroquial o catastral, usar **TRIDIS (ID 2)**.
3. **Codec y Unificación de la `s` (`[L-38]`):** El codec de TRIDIS no contiene `ſ` larga (`U+017F`); unifica la grafía a `s` (`U+0073`), pero soporta superíndices (`º`, `ª`) y macrones/tildes (`ā`, `ō`). Al preparar *Ground Truth* con LLMs, mapear siempre `ſ` $\rightarrow$ `s`.
4. **Anti-Normalización en Ground Truth (`[L-39]`):** Nunca expandir abreviaturas ni modernizar ortografía en textos de entrenamiento para Kraken. Mantener ligaduras (`deste`, `dela`) y formas literales (`fevrero`, `Ju.º`).
5. **Depuración de PAGE-XML (`[L-40]`):** Al exportar PAGE-XML de eScriptorium para poblar transcripciones con Gemini, eliminar los nodos `<Word>` y `<Glyph>` (reducción del 98% de líneas) manteniendo solo `<TextRegion>`, `<TextLine>`, `<Coords>` y `<Baseline>`.
6. **Persistencia:** Todo el trabajo (modelos, proyectos, imágenes y transcripciones) reside en los volúmenes Docker del disco persistente de 120 GB (`pd-standard`); **nunca se pierde al apagar la VM**.
