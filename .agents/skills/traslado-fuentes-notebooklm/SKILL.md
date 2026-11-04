---
name: traslado-fuentes-notebooklm
description: >-
  Reorganización, traslado y copia de fuentes fotográficas entre cuadernos de
  NotebookLM Pro bajo las directivas del Archivero Virtual (Reglas [L-30] y [L-31]).
  Permite transferir imágenes server-to-server en Google sin resubir datos
  (CopySourcesAsync), aplicar traslados puros (mover con borrado en origen) o
  duplicidad lógica (para imágenes híbridas), resolver nombres canónicos de cuadernos
  y registrar la trazabilidad sin alterar los archivos JPG locales.
---

# Traslado y Reorganización de Fuentes en NotebookLM Pro

Esta skill proporciona los procedimientos, reglas archivísticas y herramientas automatizadas para **mover o duplicar lógicamente fotogramas parroquiales entre cuadernos de Google NotebookLM Pro**.

Permite resolver los desórdenes codicológicos originados por encuadernaciones mixtas del Antiguo Régimen o clasificaciones erróneas de FamilySearch, garantizando que cada cuaderno contenga una **serie sacramental pura y correlativa** (`[L-30]`).

---

## 1. Principios Archivísticos Obligatorios

1. **Inviolabilidad del Archivo Físico Local (`[L-26]`):**
   * Queda estrictamente prohibido renombrar, cortar, dividir o borrar los archivos JPG originales en la carpeta `imagenes/`.
   * El nombre de archivo canónico `{DGS}_{FOTOGRAMA}.jpg` es la clave primaria inmutable que enlaza con las URLs ARK de FamilySearch y el Catálogo General (`catalogo_corpus.json`).

2. **Diferenciación entre TRASLADO PURO y DUPLICIDAD LÓGICA:**
   * **Modo Mover (`--delete-source` / `--move`):**
     * Se aplica cuando una imagen fue erróneamente clasificada en un sacramento al que no pertenece en absoluto (ej. un folio que contiene 100% actas de difuntos metido en un cuaderno de matrimonios).
     * El script copia la fuente al cuaderno destino y, una vez confirmada en estado `SourceStatus.READY`, la elimina del cuaderno origen.
   * **Modo Duplicidad Lógica (`--keep-source`, por defecto `[L-31]`):**
     * Se aplica a **imágenes híbridas a doble plana abierta** (ej. plana izquierda con últimos bautismos de un año y plana derecha con el arranque de matrimonios del año siguiente).
     * La imagen completa debe coexistir en ambos cuadernos, instruyendo al prompt ecdótico a transcribir únicamente la plana correspondiente a cada sacramento.

3. **Límite Estricto de Fuentes (`<= 300` fuentes/cuaderno):**
   * NotebookLM rechaza cualquier adición que supere las 300 fuentes por cuaderno.
   * Antes de transferir un lote, la skill verifica el número de fuentes actuales y advierte si se aproxima al límite de seguridad (recomendado: `<= 280` para dejar espacio a las fuentes maestras de anclaje `00..04`).

4. **Transferencia Server-to-Server Ultra-Rápida (`CopySourcesAsync`):**
   * Siempre que la fuente ya exista en los servidores de Google NotebookLM en el cuaderno origen, la skill ejecuta la copia interna en la nube de Google (`client.sources.copy`), sin consumir ancho de banda de subida ni descargar el archivo.
   * Si por cualquier motivo la fuente no estuviera en el origen, el script dispone de **fallback automático a disco local** buscando el JPG en `imagenes/` y subiéndolo con control de reintentos.

---

## 2. Herramienta Oficial de Ejecución: `move_notebooklm_sources.py`

El repositorio incluye la herramienta de producción:
[`scripts/move_notebooklm_sources.py`](file:///c:/TRABAJOS/personal/genealo/scripts/move_notebooklm_sources.py)

### Sintaxis General:
```bash
python scripts/move_notebooklm_sources.py --source <ORIGEN> --target <DESTINO> [OPCIONES]
```

* `--source`, `-s`: Nombre canónico (ej. `NRDL-MIXTO-01`) o UUID del cuaderno origen.
* `--target`, `-t`: Nombre canónico (ej. `NRDL-MATR-01`) o UUID del cuaderno destino.
* `--images`, `-i`: Lista de nombres de archivos separados por espacio.
* `--images-file`, `-f`: Archivo de texto (`.txt`) con un nombre de imagen por línea.
* `--delete-source`, `--move`: Activa el modo mover (elimina la fuente del origen tras certificar la copia).
* `--pause`: Segundos de pausa entre operaciones (default: `2.0s` anti-429).

---

## 3. Ejemplos Prácticos de Uso

### Ejemplo A: Duplicidad Lógica de Matrimonios en `NRDL-MATR-01`
Copiar los folios matrimoniales del libro mixto hacia el cuaderno de matrimonios sin borrarlos del libro mixto:
```bash
python scripts/move_notebooklm_sources.py \
  --source NRDL-MIXTO-01 \
  --target NRDL-MATR-01 \
  --images 004306112_02013.jpg 004306112_02014.jpg 004306112_02015.jpg
```

### Ejemplo B: Mover un bloque entero desde un archivo de texto
Mover 50 defunciones extraviadas eliminándolas del cuaderno origen tras certificar la copia en destino:
```bash
python scripts/move_notebooklm_sources.py \
  --source NRDL-MATR-02 \
  --target NRDL-DIFU-02 \
  --images-file scripts/lote_defunciones_traslado.txt \
  --move
```

---

## 4. Bucle de Trazabilidad y Sincronización
Tras cada operación de traslado:
1. Comprobar el log de ejecución en `scripts/traslado_fuentes.log`.
2. Actualizar `catalogo_corpus.json` si el cuaderno canónico asignado a la imagen ha cambiado de forma definitiva.
3. Actualizar `scripts/ingest_checkpoint_<localidad>.json` con el nuevo `source_id` en el cuaderno destino.
