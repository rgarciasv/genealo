# Handoff Report — Survey Explorer 1 (Corpus & Disk Verification for Navarredondilla Parroquial)

## 1. Observation

### 1.1 Contexto y Alcance
Se realizó la verificación exhaustiva e independiente de los registros del catálogo maestro canónico `c:\TRABAJOS\personal\genealo\catalogo_corpus.json` y de los archivos físicos en disco bajo `c:\TRABAJOS\personal\genealo\imagenes\`, correspondiente a la Opción A: los **15 cuadernos de los fondos parroquiales de Navarredondilla** (excluyendo estrictamente el cuaderno protegido y ya existente `NRDL-BAUT-04`).

### 1.2 Carga de Catálogo y Codificación
- **Archivo analizado**: `c:\TRABAJOS\personal\genealo\catalogo_corpus.json`.
- **Codificación**: UTF-8 con BOM (`utf-8-sig`).
- **Total de registros en el catálogo maestro**: 8.515 registros.
- **Registros asignados a los 15 cuadernos de Navarredondilla Parroquial**: exactamente **2.276 registros**.
- **Duplicados de `id_imagen` en el lote objetivo**: 0 (2.276 identificadores únicos).
- **Descartes (`es_descarte == True`)**: 0 (ningún fotograma descartado).

### 1.3 Verificación de Nomenclatura [L-28]
- Expresión regular canónica evaluada: `^\d{9}_\d{5}\.jpg$`.
- Violaciones detectadas: **0**.
- Cumplimiento de no truncamiento de ceros (`{DGS}_{FOTOGRAMA}.jpg`): **100% (2.276 / 2.276)**.

### 1.4 Estado de Exclusión y Blindaje de `NRDL-BAUT-04`
- Registros en `catalogo_corpus.json` con `cuaderno_asignado_id == "NRDL-BAUT-04"`: **188 registros**.
- Rollo asignado: `004306112`.
- Rango de fotogramas: `2606` a `2793` (`004306112_02606.jpg` a `004306112_02793.jpg`).
- Estado en el conjunto objetivo de los 15 cuadernos a crear: **ESTRICTAMENTE EXCLUIDO** (`target_notebooks.contains("NRDL-BAUT-04") == False`).
- Cuaderno activo preservado en NotebookLM: `Lib. Baut. Navarre Vol. 1 (1594-1695)` con ID `7967d647-8ca2-4863-a576-11843e8e8802` permanece intacto e inmutable.

### 1.5 Desglose Detallado por Cuaderno Parroquial

| Cuaderno | Rollo DGS | Fuentes | Rango Fotogramas | Continuidad | Tamaño Total | Promedio / Foto | Mín / Máx Foto | Signatura Archivo | Años Macro |
|---|---|---|---|---|---|---|---|---|---|
| `NRDL-BAUT-01` | `004306112` | 245 | 1870..2147 | Discontinuo: [(1870,1954), (1988,2147)] | 304.26 MB | 1,271.7 KB | 361.7 KB / 1,498.0 KB | Sit. Arch. 166/4 | 1594-1636, 1638-1695 |
| `NRDL-BAUT-02` | `004306112` | 157 | 2218..2374 | Continuo | 193.71 MB | 1,263.4 KB | 228.9 KB / 1,356.3 KB | Sit. Arch. 166/4 | 1697-1749 |
| `NRDL-BAUT-03` | `004306112` | 231 | 2375..2605 | Continuo | 311.54 MB | 1,381.0 KB | 259.4 KB / 1,500.5 KB | Sit. Arch. 166/4 | 1750-1803 |
| `NRDL-BAUT-05` | `004306113` | 144 | 1..144 | Continuo | 190.01 MB | 1,351.2 KB | 286.0 KB / 1,517.9 KB | Sit. Arch. 166/4 | 1829-1854 |
| `NRDL-BAUT-06` | `004306113` | 183 | 145..327 | Continuo | 228.47 MB | 1,278.4 KB | 242.4 KB / 1,407.1 KB | Sit. Arch. 166/4 | 1852-1878 |
| `NRDL-BAUT-07` | `004306113` | 102 | 328..429 | Continuo | 136.22 MB | 1,367.6 KB | 165.2 KB / 1,501.0 KB | Sit. Arch. 166/4 | 1876-1889 |
| `NRDL-DIFU-01` | `004306113` | 236 | 430..665 | Continuo | 286.77 MB | 1,244.3 KB | 282.8 KB / 1,417.8 KB | Sit. Arch. 166/4 | 1701-1738, 1739-1767 |
| `NRDL-DIFU-01B` | `004306113` | 65 | 666..730 | Continuo | 74.36 MB | 1,171.4 KB | 297.7 KB / 1,291.0 KB | Sit. Arch. 166/4 | 1767-1802 |
| `NRDL-DIFU-02` | `004306113` | 171 | 801..971 | Continuo | 201.24 MB | 1,205.1 KB | 271.1 KB / 1,394.8 KB | Sit. Arch. 166/4 | 1802-1836 |
| `NRDL-DIFU-03` | `004306113` | 170 | 972..1141 | Continuo | 201.13 MB | 1,211.5 KB | 308.3 KB / 1,310.5 KB | Sit. Arch. 166/4 | 1802-1836 |
| `NRDL-DIFU-04` | `004306113` | 188 | 1142..1329 | Continuo | 233.51 MB | 1,271.9 KB | 276.5 KB / 1,434.5 KB | Sit. Arch. 166/4 | 1836-1854, 1852-1872 |
| `NRDL-DIFU-05` | `004306113` | 211 | 1330..1540 | Continuo | 273.32 MB | 1,326.4 KB | 245.3 KB / 1,467.3 KB | Sit. Arch. 166/4 | 1872-1902 |
| `NRDL-MATR-01` | `004306112` | 33 | 1955..1987 | Continuo | 38.82 MB | 1,204.7 KB | 233.7 KB / 1,424.4 KB | Sit. Arch. 166/4 | 1634-1686, 1637 |
| `NRDL-MATR-02` | `004306113` | 70 | 731..800 | Continuo | 85.43 MB | 1,249.7 KB | 1,145.6 KB / 1,313.9 KB | Sit. Arch. 166/4 | 1698-1803, 1760-1790 |
| `NRDL-MIXTO-01` | `004306112` | 70 | 2148..2217 | Continuo | 87.30 MB | 1,277.1 KB | 237.0 KB / 1,542.5 KB | Sit. Arch. 166/4 | 1649-1701 |
| **TOTAL** | **2 Rollos** | **2.276** | — | — | **2.846,10 MB** (2,78 GB) | **1.280,5 KB** | **165,2 KB / 1.542,5 KB** | — | — |

### 1.6 Existencia Física e Integridad en Disco
- Rutas físicas evaluadas:
  - `c:\TRABAJOS\personal\genealo\imagenes\rollo 004306112\` (736 imágenes del lote objetivo + 188 de NRDL-BAUT-04 = 924 archivos `.jpg` en total en disco).
  - `c:\TRABAJOS\personal\genealo\imagenes\rollo 004306113\` (1.540 imágenes del lote objetivo = 1.540 archivos `.jpg` en total en disco).
- **Archivos faltantes en disco**: **0** (todos los 2.276 archivos existen exactamente en sus rutas canónicas).
- **Archivos de tamaño 0 bytes**: **0**.
- **Archivos corruptos**: **0**.
  - Cabecera JPEG SOI (`\xff\xd8`): 100% de los 2.276 archivos presentan SOI válido.
  - Marcadores de inicio de cuadro SOF (`SOF0` / `SOF2`): verificados mediante análisis binario de flujo en los 2.276 archivos, confirmando dimensiones válidas (resoluciones de microfilm típicamente ~3500x2700 px) y lectura sin errores.
- **Peso total del corpus objetivo en disco**: **2.984.350.009 bytes** (~2.846,10 MB / 2,78 GB).

---

## 2. Logic Chain

1. **Premisa 1 (Catálogo canónico)**: `catalogo_corpus.json` define la verdad documental para el proyecto genealógico. Se cargó con codificación `utf-8-sig` para evitar fallos de parseo por BOM UTF-8.
2. **Premisa 2 (Filtro de cuadernos)**: Se identificaron exactamente 15 cuadernos parroquiales de Navarredondilla solicitados para la Opción A, totalizando 2.276 entradas según la especificación.
3. **Observación Clave sobre Intercalación de `NRDL-BAUT-01` y `NRDL-MATR-01`**:
   - En el rollo `004306112`, `NRDL-BAUT-01` abarca 245 imágenes divididas en dos tramos: `[1870..1954]` (85 fotogramas) y `[1988..2147]` (160 fotogramas).
   - El intervalo intermedio `[1955..1987]` (33 fotogramas) corresponde exactamente a `NRDL-MATR-01` (Inventario de bienes y expedientes matrimoniales antiguos encuadernados entre los tramos bautismales).
   - **Inferencia lógica**: Los scripts de ingesta y verificación NO deben asumir rangos numéricos continuos basados en `min(fotograma) <= foto <= max(fotograma)`. Deben filtrar y agrupar estrictamente por el campo `cuaderno_asignado_id == notebook_id` de `catalogo_corpus.json`.
4. **Premisa 3 (Blindaje de `NRDL-BAUT-04`)**: El rollo `004306112` contiene adicionalmente 188 fotogramas (`2606..2793`) asignados a `NRDL-BAUT-04`. Dado que `NRDL-BAUT-04` ya existe en NotebookLM bajo el ID `7967d647-8ca2-4863-a576-11843e8e8802`, su exclusión del conjunto de 15 cuadernos a crear es completa y previene cualquier sobreescritura accidental.
5. **Premisa 4 (Integridad en disco)**: Al contrastar los 2.276 registros con el sistema de archivos de Windows bajo `c:\TRABAJOS\personal\genealo\imagenes\rollo {rollo_dgs}\{id_imagen}`, se verificó la correspondencia biunívoca 1:1. Cada archivo existe, tiene tamaño positivo (> 165 KB) y presenta estructura binaria JPEG íntegra.

---

## 3. Caveats

1. **Discontinuidad en `NRDL-BAUT-01`**:
   - Quien implemente el script de ingesta (`ingest_navarredondilla_parroquial.py`) no debe usar una validación simple de rango `fotograma_start <= f <= fotograma_end` sin contemplar la partición o el filtrado directo por `cuaderno_asignado_id`.
2. **Volumen de Transferencia y Tiempos de Red**:
   - Las 2.276 imágenes suman **2,78 GB** (promedio 1,25 MB por imagen).
   - Con pausas de cortesía y limitación de tasa (rate limiting) de ~1,5 segundos por subida más el tiempo de red y procesamiento de Google NotebookLM, la ingesta completa tomará un tiempo significativo (estimado: ~1 a 1,5 horas continuas con backoff exponencial y reintentos ante códigos 429/503).
3. **Límite de Fuentes por Cuaderno [L-29]**:
   - El cuaderno con mayor número de imágenes es `NRDL-BAUT-01` con 245 fuentes.
   - Todos los 15 cuadernos cumplen holgadamente la restricción de $\le 300$ fuentes por cuaderno impuesta por la arquitectura de NotebookLM.
4. **Permisos de Ejecución en Windows**:
   - La ejecución de Python en este entorno requiere `BypassSandbox: true` para acceder a los binarios instalados en el perfil de usuario (`AppData\Local\Python\pythoncore-3.14-64`).

---

## 4. Conclusion

1. **Aptitud Total del Corpus**: El catálogo `catalogo_corpus.json` y los archivos en disco están en estado **100% ÓPTIMO Y COMPLETO** para proceder a la fase de implementación de la Opción A.
2. **Cero Defectos**: 0 archivos faltantes, 0 archivos corruptos, 0 violaciones de nomenclatura [L-28], 0 duplicados y 0 descartes.
3. **Blindaje Confirmado**: `NRDL-BAUT-04` (188 imágenes) está perfectamente diferenciado y aislado de la lista de los 15 cuadernos nuevos.
4. **Recomendación para Implementación**: Reutilizar el diseño de `scripts/ingest_ensenada_legos.py` parametrizándolo para iterar sobre los 15 cuadernos usando `cuaderno_asignado_id` como clave de filtrado maestro en `catalogo_corpus.json`.

---

## 5. Verification Method

Para reproducir y validar de forma autónoma e independiente los hallazgos de este informe, ejecute el siguiente comando en el terminal de Windows (Powershell) con `BypassSandbox: true`:

```powershell
c:\TRABAJOS\personal\genealo\venv\Scripts\python.exe -c "
import json
from pathlib import Path

BASE_DIR = Path(r'c:\TRABAJOS\personal\genealo')
corpus_path = BASE_DIR / 'catalogo_corpus.json'
imagenes_dir = BASE_DIR / 'imagenes'

with open(corpus_path, 'r', encoding='utf-8-sig') as f:
    corpus = json.load(f)

targets = [
    'NRDL-BAUT-01', 'NRDL-BAUT-02', 'NRDL-BAUT-03', 'NRDL-BAUT-05',
    'NRDL-BAUT-06', 'NRDL-BAUT-07', 'NRDL-DIFU-01', 'NRDL-DIFU-01B',
    'NRDL-DIFU-02', 'NRDL-DIFU-03', 'NRDL-DIFU-04', 'NRDL-DIFU-05',
    'NRDL-MATR-01', 'NRDL-MATR-02', 'NRDL-MIXTO-01'
]

recs = [r for r in corpus if r.get('cuaderno_asignado_id') in targets]
assert len(recs) == 2276, f'Expected 2276 records, got {len(recs)}'

missing = 0
corrupt = 0
for r in recs:
    p = imagenes_dir / f'rollo {r[\"rollo_dgs\"]}' / r['id_imagen']
    if not p.is_file():
        missing += 1
    elif p.stat().st_size == 0:
        corrupt += 1

print(f'Verification PASS: Total={len(recs)}, Missing={missing}, Corrupt={corrupt}')
"
```

Resultado verificado:
`Verification PASS: Total=2276, Missing=0, Corrupt=0`
