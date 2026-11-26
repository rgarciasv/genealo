# Archivo: Infraestructura eScriptorium (GCP Spot VM) — `[ARCHIVADO]`

> **Estado:** Descartado para el flujo diario (`[L-42]`). La instancia `escriptorium-spot-vm` en Google Cloud está apagada (`TERMINATED`, `$0.00/h` de cómputo).

## Por qué está archivado aquí
Inicialmente probamos el despliegue de **eScriptorium + Kraken** en una instancia Spot de Google Compute Engine (`europe-west1-b`) para segmentar y transcribir vía web. Sin embargo:
1. Obligaba a arrancar y apagar un servidor remoto para tareas de segmentación y edición que en local (Windows 11) son mucho más rápidas (~18 s/folio en local con Kraken 7.2 frente a ~420 s en la CPU remota).
2. El proyecto migró definitivamente a un flujo **100% local basado en `PAGE-XML`** (`scripts/htr_kraken/` + `htr_pipeline/`) y a la futura aplicación nativa en Rust (**Athalia**).

## Contenido conservado (por si hiciera falta una prueba puntual en la nube)
* [`manage_escriptorium_vm.py`](manage_escriptorium_vm.py) — Script de ciclo de vida (`status`, `create`, `start`, `stop`, `ip`) de la VM Spot `escriptorium-spot-vm`.
* [`startup_escriptorium.sh`](startup_escriptorium.sh) — Script de inicialización Docker Compose de eScriptorium en Ubuntu 22.04 LTS.
* Informe histórico de benchmark: [`../docs/BENCHMARK_HTR_ESCRIPTORIUM_KRAKEN.md`](../docs/BENCHMARK_HTR_ESCRIPTORIUM_KRAKEN.md).

## Uso de emergencia (solo bajo demanda explícita)
```powershell
.\.venv\Scripts\python.exe archivo_escriptorium/manage_escriptorium_vm.py status
.\.venv\Scripts\python.exe archivo_escriptorium/manage_escriptorium_vm.py start
# Al terminar siempre apagar:
.\.venv\Scripts\python.exe archivo_escriptorium/manage_escriptorium_vm.py stop
```
