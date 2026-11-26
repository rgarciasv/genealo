# Mapa Operativo de Muestreo: Los 12 Clusters Morfográficos (`C01–C12`) y los 33 Cuadernos Auditados

> **Propósito:** Este documento conecta directamente todo el trabajo previo de **NotebookLM Pro** (las 33 auditorías codicológicas en [`transcripciones/auditoria_codicologica/`](file:///c:/TRABAJOS/personal/genealo/transcripciones/auditoria_codicologica/), [`03_AUTORIDADES_PALEOGRAFICAS_ALTO_ALBERCHE.md`](file:///c:/TRABAJOS/personal/genealo/03_AUTORIDADES_PALEOGRAFICAS_ALTO_ALBERCHE.md) y [`catalogo_corpus.json`](file:///c:/TRABAJOS/personal/genealo/catalogo_corpus.json)) con archivos `.jpg` reales verificados en disco para entrenar los **3 Motores Kraken Parroquiales** según la taxonomía única de [`docs/PIPELINE_HTR_Y_TAXONOMIA_CLUSTERS_PALEOGRAFICOS.md`](file:///c:/TRABAJOS/personal/genealo/docs/PIPELINE_HTR_Y_TAXONOMIA_CLUSTERS_PALEOGRAFICOS.md).
>
> **Imágenes físicas indexadas en `imagenes/`:** `7,860` archivos `.jpg` verificados en disco local.

---

## 1. Resumen Ejecutivo: Los 3 Motores Kraken Parroquiales y sus 12 Clusters (`C01–C12`)

| Motor Kraken Parroquial | Clusters Incluidos (Eje 1) | Arco Temporal Típico | Estado Actual de Muestras en Local |
| :--- | :--- | :--- | :--- |
| **`Motor 1`: `alto_alberche_antiguo_c01_c05.mlmodel`** | `C01`, `C02`, `C03`, `C04`, `C05` (+ `C12` transversal) | `1594–1680` | Candidatos localizados en disco (`DGS 004306112` y `004298571_00532`). |
| **`Motor 2`: `alto_alberche_bastardo_c06_c10.mlmodel`** | `C06`, `C07`, `C08`, `C09`, `C10` (+ `C12` transversal) | `1660–1840` | **En marcha:** Folio `004298570_01608` (69 líneas transcritas con 0 errores Unicode, `C07`/`C08`). |
| **`Motor 3`: `alto_alberche_plumilla_c11.mlmodel`** | `C11` (+ `C12` transversal) | `1840–1902` | **En marcha:** `lote_prueba_5` (`004298570_02637` a `02641`, 5 folios ya segmentados en local, `C11`). |

> **Separación estricta de Ejes y Carriles Independientes (fuera de estos 3 motores parroquiales):**
> - **Eje 1 (`C01–C12`)** describe exclusivamente la morfografía del trazo; **Eje 2** describe la tipología documental (`BAUTISMO`, `MATRIMONIO`, `DEFUNCION`, Aparato Auxiliar y Catastro de Ensenada).
> - **Carril Auxiliar (`CONFIRMACION`, `INDICE`, `AUTO_VISITA`, `MEMORIA_MISAS`):** pocos folios y formato especializado; extracción directa con Gemini 4 o motor auxiliar opcional.
> - **Carril Independiente — Catastro de Ensenada (`ENSENADA_LEGOS` / `ENSENADA_BIENES`):** va por un camino completamente separado de los libros parroquiales (ver Sección 5).

---

## 2. Catálogo de Muestreo por Cluster (`C01` a `C12`) con Rutas Locales Verificadas

### `C01` — Gótico-cortesana tardía (1500–1560 (residual en nuestro corpus desde 1594))
* **Motor Kraken destino:** `Motor 1: Bloque Antiguo C01–C05 (alto_alberche_antiguo_c01_c05.mlmodel)`
* **Rasgos morfográficos:** Trazo anguloso y quebrado, módulo pequeño, líneas muy juntas, alta densidad de abreviaturas medievales y signos tironianos (en nuestro corpus aparece como rasgo arcaizante residual en las primeras actas de 1594).
* **Escribanos / Autoridades de referencia:** Alonso del Valle (1594, NRDL — cortesana de transición a procesal en los primeros asientos); Fray Juan de la Cruz (1594, NRDL — mano claustral arcaizante)
* **Cuadernos canónicos fuente:** `NRDL-BAUT-01`
* **Muestras `.jpg` verificadas en disco listas para segmentar (`segmentar_lote.py`):**
  - [`004306112_01872.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004306112/004306112_01872.jpg) (`imagenes/rollo 004306112/004306112_01872.jpg`)
  - [`004306112_01873.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004306112/004306112_01873.jpg) (`imagenes/rollo 004306112/004306112_01873.jpg`)
  - [`004306112_01903.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004306112/004306112_01903.jpg) (`imagenes/rollo 004306112/004306112_01903.jpg`)
  - [`004306112_01904.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004306112/004306112_01904.jpg) (`imagenes/rollo 004306112/004306112_01904.jpg`)
  - [`004306112_01905.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004306112/004306112_01905.jpg) (`imagenes/rollo 004306112/004306112_01905.jpg`)

### `C02` — Procesal redonda / abierta (1530–1620)
* **Motor Kraken destino:** `Motor 1: Bloque Antiguo C01–C05 (alto_alberche_antiguo_c01_c05.mlmodel)`
* **Rasgos morfográficos:** Formas curvas y anchas, letras aislables pero con nexos envolventes largos. Pluma gruesa de ave.
* **Escribanos / Autoridades de referencia:** Fray Francisco de Oropesa (1595–1596, NRDL); Gaspar Rubiano — primera etapa (1612–1618, NRDL); Alonso Triguero y Villena (1609–1611, NRDL/JMOL); Fray Jacinto de Alcocer (1611–1613, NRDL)
* **Cuadernos canónicos fuente:** `NRDL-BAUT-01`, `NRDL-MATR-01`
* **Muestras `.jpg` verificadas en disco listas para segmentar (`segmentar_lote.py`):**
  - [`004306112_01876.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004306112/004306112_01876.jpg) (`imagenes/rollo 004306112/004306112_01876.jpg`)
  - [`004306112_01877.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004306112/004306112_01877.jpg) (`imagenes/rollo 004306112/004306112_01877.jpg`)
  - [`004306112_01912.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004306112/004306112_01912.jpg) (`imagenes/rollo 004306112/004306112_01912.jpg`)
  - [`004306112_01917.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004306112/004306112_01917.jpg) (`imagenes/rollo 004306112/004306112_01917.jpg`)
  - [`004306112_01922.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004306112/004306112_01922.jpg) (`imagenes/rollo 004306112/004306112_01922.jpg`)

### `C03` — Procesal encadenada pura (1560–1650)
* **Motor Kraken destino:** `Motor 1: Bloque Antiguo C01–C05 (alto_alberche_antiguo_c01_c05.mlmodel)`
* **Rasgos morfográficos:** Renglones casi sin levantar la pluma (scriptio continua); c, e, n, m, r, s reducidas a ondas similares.
* **Escribanos / Autoridades de referencia:** Joan Martínez [Monterroso] (1596–1604, NRDL — secuencia continua 01878–01891); Pedro Pérez de las Presas (1627–1634, NRDL); Andrés Bautista (1653–1658, NRDL)
* **Cuadernos canónicos fuente:** `NRDL-BAUT-01`, `NRDL-MATR-01`, `JMOL-DIFU-PARVULOS`
* **Muestras `.jpg` verificadas en disco listas para segmentar (`segmentar_lote.py`):**
  - [`004306112_01878.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004306112/004306112_01878.jpg) (`imagenes/rollo 004306112/004306112_01878.jpg`)
  - [`004306112_01881.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004306112/004306112_01881.jpg) (`imagenes/rollo 004306112/004306112_01881.jpg`)
  - [`004306112_01888.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004306112/004306112_01888.jpg) (`imagenes/rollo 004306112/004306112_01888.jpg`)
  - [`004306112_01938.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004306112/004306112_01938.jpg) (`imagenes/rollo 004306112/004306112_01938.jpg`)
  - [`004306112_02080.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004306112/004306112_02080.jpg) (`imagenes/rollo 004306112/004306112_02080.jpg`)

### `C04` — Humanística / Itálica libraria (1550–1640)
* **Motor Kraken destino:** `Motor 1: Bloque Antiguo C01–C05 (alto_alberche_antiguo_c01_c05.mlmodel)`
* **Rasgos morfográficos:** Vertical o levemente inclinada, letras sueltas casi de imprenta, limpia y sin apenas lazos.
* **Escribanos / Autoridades de referencia:** Don Rodrigo Antonio de Meneses (1594, NRDL/JMOL — asiento 6v); Bachiller Francisco Rodríguez (1598–1607, NRDL); Bachiller Baltasar de Luján (1600–1606, NRDL/JMOL/NMRL); Don Marcos Conde (1650–1653, NRDL)
* **Cuadernos canónicos fuente:** `NRDL-BAUT-01`, `JMOL-DIFU-PARVULOS`, `NRDL-MIXTO-01`
* **Muestras `.jpg` verificadas en disco listas para segmentar (`segmentar_lote.py`):**
  - [`004306112_01874.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004306112/004306112_01874.jpg) (`imagenes/rollo 004306112/004306112_01874.jpg`)
  - [`004306112_01880.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004306112/004306112_01880.jpg) (`imagenes/rollo 004306112/004306112_01880.jpg`)
  - [`004306112_01884.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004306112/004306112_01884.jpg) (`imagenes/rollo 004306112/004306112_01884.jpg`)
  - [`004306112_02074.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004306112/004306112_02074.jpg) (`imagenes/rollo 004306112/004306112_02074.jpg`)
  - [`004298571_00532.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004298571/004298571_00532.jpg) (`imagenes/rollo 004298571/004298571_00532.jpg`)

### `C05` — Híbrida procesal-bastarda (1610–1680)
* **Motor Kraken destino:** `Motor 1: Bloque Antiguo C01–C05 (alto_alberche_antiguo_c01_c05.mlmodel)`
* **Rasgos morfográficos:** Base inclinada de bastarda con ataduras procesales, d unciales vueltas atrás y abreviaturas arcaicas.
* **Escribanos / Autoridades de referencia:** Alonso Hernández (1601–1610, NRDL — superíndices volados extremos); Francisco Sánchez del Unar (1633–1641, NRDL); Gaspar González (1640–1642, NRDL); Fray Mateo del Mazo (1658–1689, NRDL/JMOL)
* **Cuadernos canónicos fuente:** `NRDL-BAUT-01`, `NRDL-MATR-01`, `NRDL-MIXTO-01`, `JMOL-DIFU-PARVULOS`
* **Muestras `.jpg` verificadas en disco listas para segmentar (`segmentar_lote.py`):**
  - [`004306112_01895.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004306112/004306112_01895.jpg) (`imagenes/rollo 004306112/004306112_01895.jpg`)
  - [`004306112_01950.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004306112/004306112_01950.jpg) (`imagenes/rollo 004306112/004306112_01950.jpg`)
  - [`004306112_02043.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004306112/004306112_02043.jpg) (`imagenes/rollo 004306112/004306112_02043.jpg`)
  - [`004306112_02053.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004306112/004306112_02053.jpg) (`imagenes/rollo 004306112/004306112_02053.jpg`)
  - [`004306112_02086.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004306112/004306112_02086.jpg) (`imagenes/rollo 004306112/004306112_02086.jpg`)

### `C06` — Bastarda cancilleresca / magistral (1660–1780)
* **Motor Kraken destino:** `Motor 2: Bloque Bastardo C06–C10 (alto_alberche_bastardo_c06_c10.mlmodel)`
* **Rasgos morfográficos:** Caja redonda y uniforme, inclinación constante, renglones rectos y separación clara (ej. Domingo Galán, 1710–1711).
* **Escribanos / Autoridades de referencia:** Domingo Galán (1710–1711, referencia comarcal); Domingo Hernández (1666–1680, NRDL); Lic. Jerónimo Ruiz Núñez (1689–1696, NRDL); D. Manuel Gil Sánchez y párrocos titulares de NRDL-BAUT-02 / JMOL-BAUT-01
* **Cuadernos canónicos fuente:** `NRDL-BAUT-01`, `NRDL-BAUT-02`, `JMOL-BAUT-01`, `NRDL-MATR-01`, `JMOL-MATR-01`
* **Muestras `.jpg` verificadas en disco listas para segmentar (`segmentar_lote.py`):**
  - [`004306112_02105.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004306112/004306112_02105.jpg) (`imagenes/rollo 004306112/004306112_02105.jpg`)
  - [`004306112_02135.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004306112/004306112_02135.jpg) (`imagenes/rollo 004306112/004306112_02135.jpg`)
  - [`004306112_02230.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004306112/004306112_02230.jpg) (`imagenes/rollo 004306112/004306112_02230.jpg`)
  - [`004298570_01760.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004298570/004298570_01760.jpg) (`imagenes/rollo 004298570/004298570_01760.jpg`)
  - [`004298571_00015.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004298571/004298571_00015.jpg) (`imagenes/rollo 004298571/004298571_00015.jpg`)

### `C07` — Bastarda angulosa / picuda (1680–1790)
* **Motor Kraken destino:** `Motor 2: Bloque Bastardo C06–C10 (alto_alberche_bastardo_c06_c10.mlmodel)`
* **Rasgos morfográficos:** Módulo comprimido lateralmente, picos agudos y aspecto «aserrado», enlaces rápidos (ej. Fray Francisco Martínez, 1716, folio 01608).
* **Escribanos / Autoridades de referencia:** Fray Francisco Martínez (1715–1725, JMOL — folio 004298570_01608.jpg); Lic. Melchor Núñez (1684–1689, NRDL); Párrocos de JMOL-DIFU-01 y NRDL-DIFU-01
* **Cuadernos canónicos fuente:** `JMOL-BAUT-01`, `NRDL-BAUT-01`, `NRDL-BAUT-02`, `JMOL-DIFU-01`, `NRDL-DIFU-01`
* **Muestras `.jpg` verificadas en disco listas para segmentar (`segmentar_lote.py`):**
  - [`004298570_01608.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004298570/004298570_01608.jpg) (`imagenes/rollo 004298570/004298570_01608.jpg`)
  - [`004298570_01615.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004298570/004298570_01615.jpg) (`imagenes/rollo 004298570/004298570_01615.jpg`)
  - [`004306112_02125.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004306112/004306112_02125.jpg) (`imagenes/rollo 004306112/004306112_02125.jpg`)
  - [`004298571_00575.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004298571/004298571_00575.jpg) (`imagenes/rollo 004298571/004298571_00575.jpg`)
  - [`004306113_00420.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004306113/004306113_00420.jpg) (`imagenes/rollo 004306113/004306113_00420.jpg`)

### `C08` — Bastarda corriente / desbordada (1670–1810)
* **Motor Kraken destino:** `Motor 2: Bloque Bastardo C06–C10 (alto_alberche_bastardo_c06_c10.mlmodel)`
* **Rasgos morfográficos:** Ejecución rápida y descuidada, ojales gigantescos que invaden dos renglones, renglón caído y aglutinaciones (ej. Pedro de la Rebilla, 1710).
* **Escribanos / Autoridades de referencia:** Pedro de la Rebilla (1710, referencia comarcal); Fr. Basilio Herrero Carpio (1717, JMOL — asiento 4 de 01608); Tenientes y vicarios rápidos de JMOL-BAUT-01, NRDL-BAUT-02 y NRDL-DIFU-01
* **Cuadernos canónicos fuente:** `JMOL-BAUT-01`, `NRDL-BAUT-02`, `NRDL-DIFU-01`, `NRDL-MATR-02`, `JMOL-DIFU-02`
* **Muestras `.jpg` verificadas en disco listas para segmentar (`segmentar_lote.py`):**
  - [`004298570_01650.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004298570/004298570_01650.jpg) (`imagenes/rollo 004298570/004298570_01650.jpg`)
  - [`004298570_01720.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004298570/004298570_01720.jpg) (`imagenes/rollo 004298570/004298570_01720.jpg`)
  - [`004306112_02310.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004306112/004306112_02310.jpg) (`imagenes/rollo 004306112/004306112_02310.jpg`)
  - [`004306113_00450.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004306113/004306113_00450.jpg) (`imagenes/rollo 004306113/004306113_00450.jpg`)
  - [`004306113_00750.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004306113/004306113_00750.jpg) (`imagenes/rollo 004306113/004306113_00750.jpg`)

### `C09` — Micro-cursiva compacta (1650–1830)
* **Motor Kraken destino:** `Motor 2: Bloque Bastardo C06–C10 (alto_alberche_bastardo_c06_c10.mlmodel)`
* **Rasgos morfográficos:** Letra diminuta y empastada por aprovechamiento de espacio o notas marginales densas (ej. Pedro de la Rebilla, 1711).
* **Escribanos / Autoridades de referencia:** Pedro de la Rebilla (1711, marginalia densa y aprovechamiento de espacio); Lic. Joseph Romero de Navas (1682–1684, NRDL — letra menuda muy apretada); Anotadores de marginales y extractos en NRDL-DIFU-01 / JMOL-DIFU-01 / NRDL-DIFU-02
* **Cuadernos canónicos fuente:** `NRDL-BAUT-01`, `JMOL-DIFU-01`, `NRDL-DIFU-01`, `JMOL-DIFU-02`, `NRDL-DIFU-02`
* **Muestras `.jpg` verificadas en disco listas para segmentar (`segmentar_lote.py`):**
  - [`004306112_02119.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004306112/004306112_02119.jpg) (`imagenes/rollo 004306112/004306112_02119.jpg`)
  - [`004306112_02120.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004306112/004306112_02120.jpg) (`imagenes/rollo 004306112/004306112_02120.jpg`)
  - [`004298571_00650.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004298571/004298571_00650.jpg) (`imagenes/rollo 004298571/004298571_00650.jpg`)
  - [`004306113_00520.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004306113/004306113_00520.jpg) (`imagenes/rollo 004306113/004306113_00520.jpg`)
  - [`004306113_00790.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004306113/004306113_00790.jpg) (`imagenes/rollo 004306113/004306113_00790.jpg`)

### `C10` — Bastarda ilustrada / neoclásica (1770–1840)
* **Motor Kraken destino:** `Motor 2: Bloque Bastardo C06–C10 (alto_alberche_bastardo_c06_c10.mlmodel)`
* **Rasgos morfográficos:** Pluma más fina, limpia, simplificación de abreviaturas y casi sin lazos envolventes.
* **Escribanos / Autoridades de referencia:** Párrocos ilustrados de NRDL-BAUT-03 (1750–1803) y NRDL-BAUT-04 (1804–1828); Párrocos de NRDL-DIFU-01B, NRDL-DIFU-02 y JMOL-MATR-02
* **Cuadernos canónicos fuente:** `NRDL-BAUT-03`, `NRDL-BAUT-04`, `NRDL-DIFU-01B`, `NRDL-DIFU-02`, `JMOL-MATR-02`
* **Muestras `.jpg` verificadas en disco listas para segmentar (`segmentar_lote.py`):**
  - [`004306112_02410.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004306112/004306112_02410.jpg) (`imagenes/rollo 004306112/004306112_02410.jpg`)
  - [`004306112_02520.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004306112/004306112_02520.jpg) (`imagenes/rollo 004306112/004306112_02520.jpg`)
  - [`004306112_02630.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004306112/004306112_02630.jpg) (`imagenes/rollo 004306112/004306112_02630.jpg`)
  - [`004298571_00250.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004298571/004298571_00250.jpg) (`imagenes/rollo 004298571/004298571_00250.jpg`)
  - [`004306113_00850.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004306113/004306113_00850.jpg) (`imagenes/rollo 004306113/004306113_00850.jpg`)

### `C11` — Cursiva inglesa / comercial (1840–1899)
* **Motor Kraken destino:** `Motor 3: Bloque Plumilla Metálica C11 (alto_alberche_plumilla_c11.mlmodel)`
* **Rasgos morfográficos:** Plumilla metálica: ascendentes finísimos (vulnerables a mala foto) y descendentes gruesos, muy inclinada (ej. lote_prueba_5: 02637–02641).
* **Escribanos / Autoridades de referencia:** Párrocos de JMOL-BAUT-05 (1851–1862, lote_prueba_5: 004298570_02637–02641); Párrocos de NRDL-BAUT-05, NRDL-BAUT-06, NRDL-BAUT-07 y NRDL-DIFU-05; Párrocos de JMOL-MATR-03, JMOL-DIFU-04, JMOL-DIFU-05 y JMOL-DIFU-06
* **Cuadernos canónicos fuente:** `JMOL-BAUT-05`, `NRDL-BAUT-06`, `NRDL-BAUT-07`, `JMOL-MATR-03`, `NRDL-DIFU-05`
* **Muestras `.jpg` verificadas en disco listas para segmentar (`segmentar_lote.py`):**
  - [`004298570_02637.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004298570/004298570_02637.jpg) (`imagenes/rollo 004298570/004298570_02637.jpg`)
  - [`004298570_02638.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004298570/004298570_02638.jpg) (`imagenes/rollo 004298570/004298570_02638.jpg`)
  - [`004298570_02639.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004298570/004298570_02639.jpg) (`imagenes/rollo 004298570/004298570_02639.jpg`)
  - [`004306113_00100.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004306113/004306113_00100.jpg) (`imagenes/rollo 004306113/004306113_00100.jpg`)
  - [`004306113_00360.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004306113/004306113_00360.jpg) (`imagenes/rollo 004306113/004306113_00360.jpg`)

### `C12` — Rústica / senil o temblorosa (Transversal)
* **Motor Kraken destino:** `Transversal en Motores 1, 2 y 3 (muestras repartidas en todos los bloques)`
* **Rasgos morfográficos:** Trazo roto o tembloroso, manchas de goteo y formas irregulares sin escuela clara. Se reparte transversalmente en los Motores 1, 2 y 3.
* **Escribanos / Autoridades de referencia:** Gaspar González — 2º ministerio de ancianidad (1672, NRDL — 004306112_02085.jpg); Simón Palomo Bayala (1683, JMOL/NMRL en NRDL — 004306112_02122.jpg); Manos temblorosas o rústicas en JMOL-DIFU-03, JMOL-DIFU-04 y NRDL-DIFU-04
* **Cuadernos canónicos fuente:** `NRDL-BAUT-01`, `NRDL-MIXTO-01`, `JMOL-DIFU-03`, `JMOL-DIFU-04`, `NRDL-DIFU-04`
* **Muestras `.jpg` verificadas en disco listas para segmentar (`segmentar_lote.py`):**
  - [`004306112_02085.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004306112/004306112_02085.jpg) (`imagenes/rollo 004306112/004306112_02085.jpg`)
  - [`004306112_02122.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004306112/004306112_02122.jpg) (`imagenes/rollo 004306112/004306112_02122.jpg`)
  - [`004298571_01033.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004298571/004298571_01033.jpg) (`imagenes/rollo 004298571/004298571_01033.jpg`)
  - [`004298571_01050.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004298571/004298571_01050.jpg) (`imagenes/rollo 004298571/004298571_01050.jpg`)
  - [`004306113_01020.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004306113/004306113_01020.jpg) (`imagenes/rollo 004306113/004306113_01020.jpg`)

---

## 3. Cruce de las 33 Auditorías de NotebookLM con los Clusters `C01–C12`

| # | Cuaderno Auditado (`notebook_id`) | Parroquia | Imágenes en Catálogo | Rango Cronológico | Clusters Asignados | Informe de Auditoría Codicológica | Muestras Verificadas en Disco |
| :-: | :--- | :-: | :-: | :-: | :-: | :--- | :--- |
| 1 | **`JMOL-BAUT-01`** | `JMOL` | 175 | 1715-1752 | `C06`, `C07`, `C08` | [`JMOL-BAUT-01.md`](file:///c:/TRABAJOS/personal/genealo/transcripciones/auditoria_codicologica/JMOL-BAUT-01.md) | `004298570_01599.jpg`, `004298570_01600.jpg` |
| 2 | **`JMOL-BAUT-02`** | `JMOL` | 276 | 1752-1800 | `C07`, `C08`, `C10` | [`JMOL-BAUT-02.md`](file:///c:/TRABAJOS/personal/genealo/transcripciones/auditoria_codicologica/JMOL-BAUT-02.md) | Pendiente descarga local |
| 3 | **`JMOL-BAUT-03`** | `JMOL` | 190 | 1801-1852 | `C08`, `C10`, `C11` | [`JMOL-BAUT-03.md`](file:///c:/TRABAJOS/personal/genealo/transcripciones/auditoria_codicologica/JMOL-BAUT-03.md) | Pendiente descarga local |
| 4 | **`JMOL-BAUT-04`** | `JMOL` | 189 | 1801-1852 | `C10`, `C11` | [`JMOL-BAUT-04.md`](file:///c:/TRABAJOS/personal/genealo/transcripciones/auditoria_codicologica/JMOL-BAUT-04.md) | Pendiente descarga local |
| 5 | **`JMOL-BAUT-05`** | `JMOL` | 139 | 1851-1862 | `C11` | [`JMOL-BAUT-05.md`](file:///c:/TRABAJOS/personal/genealo/transcripciones/auditoria_codicologica/JMOL-BAUT-05.md) | `004298570_02520.jpg`, `004298570_02521.jpg` |
| 6 | **`JMOL-DIFU-01`** | `JMOL` | 202 | 1715-1764 | `C06`, `C07`, `C08`, `C09` | [`JMOL-DIFU-01.md`](file:///c:/TRABAJOS/personal/genealo/transcripciones/auditoria_codicologica/JMOL-DIFU-01.md) | `004298571_00554.jpg`, `004298571_00755.jpg` |
| 7 | **`JMOL-DIFU-02`** | `JMOL` | 277 | 1764-1848 | `C08`, `C09`, `C10` | [`JMOL-DIFU-02.md`](file:///c:/TRABAJOS/personal/genealo/transcripciones/auditoria_codicologica/JMOL-DIFU-02.md) | `004298571_00756.jpg`, `004298571_01032.jpg` |
| 8 | **`JMOL-DIFU-03`** | `JMOL` | 17 | 1849-1851 | `C11`, `C12` | [`JMOL-DIFU-03.md`](file:///c:/TRABAJOS/personal/genealo/transcripciones/auditoria_codicologica/JMOL-DIFU-03.md) | `004298571_01033.jpg`, `004298571_01034.jpg` |
| 9 | **`JMOL-DIFU-04`** | `JMOL` | 214 | 1851-1883 | `C11`, `C12` | [`JMOL-DIFU-04.md`](file:///c:/TRABAJOS/personal/genealo/transcripciones/auditoria_codicologica/JMOL-DIFU-04.md) | `004298571_01050.jpg`, `004298571_01263.jpg` |
| 10 | **`JMOL-DIFU-05`** | `JMOL` | 99 | 1872-1881 | `C11` | [`JMOL-DIFU-05.md`](file:///c:/TRABAJOS/personal/genealo/transcripciones/auditoria_codicologica/JMOL-DIFU-05.md) | `004298571_01264.jpg`, `004298571_01362.jpg` |
| 11 | **`JMOL-DIFU-06`** | `JMOL` | 177 | 1881-1892 | `C11` | [`JMOL-DIFU-06.md`](file:///c:/TRABAJOS/personal/genealo/transcripciones/auditoria_codicologica/JMOL-DIFU-06.md) | `004298571_01363.jpg`, `004298571_01364.jpg` |
| 12 | **`JMOL-DIFU-PARVULOS`** | `JMOL` | 27 | 1632-1680 | `C03`, `C04`, `C05` | [`JMOL-DIFU-PARVULOS.md`](file:///c:/TRABAJOS/personal/genealo/transcripciones/auditoria_codicologica/JMOL-DIFU-PARVULOS.md) | `004298571_00527.jpg`, `004298571_00553.jpg` |
| 13 | **`JMOL-INDICE-BAUT-MAT`** | `JMOL` | 111 | 1716-1920, 1750-1914 | `C06–C11`, `Carril Auxiliar: INDICE` | [`JMOL-INDICE-BAUT-MAT.md`](file:///c:/TRABAJOS/personal/genealo/transcripciones/auditoria_codicologica/JMOL-INDICE-BAUT-MAT.md) | `004298570_02661.jpg`, `004298570_02748.jpg` |
| 14 | **`JMOL-INDICE-DIFU`** | `JMOL` | 21 | 1893-1907 | `C11`, `Carril Auxiliar: INDICE` | [`JMOL-INDICE-DIFU.md`](file:///c:/TRABAJOS/personal/genealo/transcripciones/auditoria_codicologica/JMOL-INDICE-DIFU.md) | `004298571_01540.jpg`, `004298571_01541.jpg` |
| 15 | **`JMOL-MATR-01`** | `JMOL` | 194 | 1716-1789 | `C06`, `C07`, `C10` | [`JMOL-MATR-01.md`](file:///c:/TRABAJOS/personal/genealo/transcripciones/auditoria_codicologica/JMOL-MATR-01.md) | `004298571_00001.jpg`, `004298571_00002.jpg` |
| 16 | **`JMOL-MATR-02`** | `JMOL` | 134 | 1790-1852 | `C08`, `C10`, `C11` | [`JMOL-MATR-02.md`](file:///c:/TRABAJOS/personal/genealo/transcripciones/auditoria_codicologica/JMOL-MATR-02.md) | `004298571_00195.jpg`, `004298571_00196.jpg` |
| 17 | **`JMOL-MATR-03`** | `JMOL` | 198 | 1851-1899 | `C11` | [`JMOL-MATR-03.md`](file:///c:/TRABAJOS/personal/genealo/transcripciones/auditoria_codicologica/JMOL-MATR-03.md) | `004298571_00329.jpg`, `004298571_00330.jpg` |
| 18 | **`JMOL-MIXTO-04`** | `JMOL` | 91 | 1842-1850 | `C10`, `C11` | [`JMOL-MIXTO-04.md`](file:///c:/TRABAJOS/personal/genealo/transcripciones/auditoria_codicologica/JMOL-MIXTO-04.md) | `004298570_02570.jpg`, `004298570_02660.jpg` |
| 19 | **`NRDL-BAUT-01`** | `NRDL` | 245 | 1594-1636, 1631-1672, 1638-1695 | `C01`, `C02`, `C03`, `C04`, `C05`, `C06`, `C12` | [`NRDL-BAUT-01.md`](file:///c:/TRABAJOS/personal/genealo/transcripciones/auditoria_codicologica/NRDL-BAUT-01.md) | `004306112_01870.jpg`, `004306112_01871.jpg` |
| 20 | **`NRDL-BAUT-02`** | `NRDL` | 157 | 1697-1749 | `C06`, `C07`, `C08`, `C09` | [`NRDL-BAUT-02.md`](file:///c:/TRABAJOS/personal/genealo/transcripciones/auditoria_codicologica/NRDL-BAUT-02.md) | `004306112_02218.jpg`, `004306112_02373.jpg` |
| 21 | **`NRDL-BAUT-03`** | `NRDL` | 231 | 1750-1803 | `C07`, `C08`, `C10` | [`NRDL-BAUT-03.md`](file:///c:/TRABAJOS/personal/genealo/transcripciones/auditoria_codicologica/NRDL-BAUT-03.md) | `004306112_02375.jpg`, `004306112_02376.jpg` |
| 22 | **`NRDL-BAUT-05`** | `NRDL` | 144 | 1829-1854 | `C10`, `C11` | [`NRDL-BAUT-05.md`](file:///c:/TRABAJOS/personal/genealo/transcripciones/auditoria_codicologica/NRDL-BAUT-05.md) | `004306113_00001.jpg`, `004306113_00002.jpg` |
| 23 | **`NRDL-BAUT-06`** | `NRDL` | 183 | 1852-1878 | `C11` | [`NRDL-BAUT-06.md`](file:///c:/TRABAJOS/personal/genealo/transcripciones/auditoria_codicologica/NRDL-BAUT-06.md) | `004306113_00145.jpg`, `004306113_00146.jpg` |
| 24 | **`NRDL-BAUT-07`** | `NRDL` | 102 | 1876-1889 | `C11` | [`NRDL-BAUT-07.md`](file:///c:/TRABAJOS/personal/genealo/transcripciones/auditoria_codicologica/NRDL-BAUT-07.md) | `004306113_00328.jpg`, `004306113_00329.jpg` |
| 25 | **`NRDL-DIFU-01`** | `NRDL` | 236 | 1701-1738, 1739-1767 | `C06`, `C07`, `C08`, `C09` | [`NRDL-DIFU-01.md`](file:///c:/TRABAJOS/personal/genealo/transcripciones/auditoria_codicologica/NRDL-DIFU-01.md) | `004306113_00430.jpg`, `004306113_00431.jpg` |
| 26 | **`NRDL-DIFU-01B`** | `NRDL` | 65 | 1767-1802 | `C07`, `C08`, `C10` | [`NRDL-DIFU-01B.md`](file:///c:/TRABAJOS/personal/genealo/transcripciones/auditoria_codicologica/NRDL-DIFU-01B.md) | `004306113_00666.jpg`, `004306113_00667.jpg` |
| 27 | **`NRDL-DIFU-02`** | `NRDL` | 171 | 1802-1836 | `C08`, `C09`, `C10` | [`NRDL-DIFU-02.md`](file:///c:/TRABAJOS/personal/genealo/transcripciones/auditoria_codicologica/NRDL-DIFU-02.md) | `004306113_00746.jpg`, `004306113_00779.jpg` |
| 28 | **`NRDL-DIFU-03`** | `NRDL` | 170 | 1802-1836 | `C08`, `C10` | [`NRDL-DIFU-03.md`](file:///c:/TRABAJOS/personal/genealo/transcripciones/auditoria_codicologica/NRDL-DIFU-03.md) | `004306113_01030.jpg`, `004306113_01031.jpg` |
| 29 | **`NRDL-DIFU-04`** | `NRDL` | 188 | 1836-1854, 1852-1872 | `C11`, `C12` | [`NRDL-DIFU-04.md`](file:///c:/TRABAJOS/personal/genealo/transcripciones/auditoria_codicologica/NRDL-DIFU-04.md) | `004306113_01142.jpg`, `004306113_01209.jpg` |
| 30 | **`NRDL-DIFU-05`** | `NRDL` | 211 | 1872-1902 | `C11` | [`NRDL-DIFU-05.md`](file:///c:/TRABAJOS/personal/genealo/transcripciones/auditoria_codicologica/NRDL-DIFU-05.md) | `004306113_01330.jpg`, `004306113_01331.jpg` |
| 31 | **`NRDL-MATR-01`** | `NRDL` | 33 | 1634-1686, 1637 | `C03`, `C04`, `C05`, `C06` | [`NRDL-MATR-01.md`](file:///c:/TRABAJOS/personal/genealo/transcripciones/auditoria_codicologica/NRDL-MATR-01.md) | `004306112_01955.jpg`, `004306112_01956.jpg` |
| 32 | **`NRDL-MATR-02`** | `NRDL` | 70 | 1698-1803, 1760-1790 | `C06`, `C07`, `C08`, `C10` | [`NRDL-MATR-02.md`](file:///c:/TRABAJOS/personal/genealo/transcripciones/auditoria_codicologica/NRDL-MATR-02.md) | `004306113_00806.jpg`, `004306113_00959.jpg` |
| 33 | **`NRDL-MIXTO-01`** | `NRDL` | 70 | 1649-1701 | `C04`, `C05`, `C06`, `C12` | [`NRDL-MIXTO-01.md`](file:///c:/TRABAJOS/personal/genealo/transcripciones/auditoria_codicologica/NRDL-MIXTO-01.md) | `004306112_01990.jpg`, `004306112_02008.jpg` |

---

## 4. Cómo Preparar un Lote de Entrenamiento de Cualquier Cluster en 3 Comandos

Cuando queramos entrenar o ampliar cualquiera de los 12 clusters (`C01`–`C12`):

1. **Copiar 3–5 imágenes candidatas del cluster** (de la Sección 2 de este documento) a `htr_pipeline/inputs/cluster_CXX/` y **segmentarlas en local con Kraken**:
   ```powershell
   .\.venv\Scripts\python.exe scripts/htr_kraken/segmentar_lote.py --input-dir htr_pipeline/inputs/cluster_CXX --output-dir htr_pipeline/outputs/cluster_CXX
   ```
2. **Corregir baselines (cortar llaves `}`) y regiones en Aletheia 4.1**, guardar el `.xml` y **recalcular las máscaras poligonales `<Coords>`**:
   ```powershell
   .\.venv\Scripts\python.exe scripts/htr_kraken/recalcular_mascaras_aletheia.py --xml-dir htr_pipeline/outputs/cluster_CXX
   ```
3. **Pre-transcribir con Gemini (`transcribir_pagexml.py`, regla `[L-44]`) y dar el visto bueno final en Aletheia 4.1** para incorporarlo al conjunto de entrenamiento `ketos train`:
   ```powershell
   .\.venv\Scripts\python.exe scripts/htr_kraken/transcribir_pagexml.py --image htr_pipeline/inputs/cluster_CXX/<folio>.jpg --xml htr_pipeline/outputs/cluster_CXX/<folio>.xml --output-dir htr_pipeline/outputs/cluster_CXX --mode partida --resolution ultra_high --thinking-level medium
   ```

---

## 5. Carriles Independientes fuera de los 3 Motores Parroquiales

### 5.1. Carril Independiente: Catastro del Marqués de la Ensenada (`ENSENADA_LEGOS` / `ENSENADA_BIENES`)

El Catastro de Ensenada (1751–1752) **no forma parte de `C01–C12` parroquiales** y va por un carril HTR completamente separado. Un mismo escribano real de comisión solía redactar todos los volúmenes de un pueblo e incluso de pueblos colindantes; por ello, cuando toque entrenar Kraken para Ensenada, se entrenará aparte **combinando múltiples fondos y manos de Ensenada distintos** para evitar sobreajuste a un único escribano.

| Cuaderno Catastral (`catalogo_corpus.json`) | Territorio | Tipología | Imágenes Catalogadas | Muestras Verificadas en Disco |
| :--- | :-: | :--- | :-: | :--- |
| **`ENSENADA-ECLESIASTICO-01`** | `ALTO_ALBERCHE` | `BIENES_ECLESIASTICOS` | 196 | [`004469026_00287.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004469026/004469026_00287.jpg), [`004469026_00288.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004469026/004469026_00288.jpg) |
| **`ENSENADA-ECLESIASTICO-02`** | `ALTO_ALBERCHE` | `BIENES_ECLESIASTICOS` | 195 | [`004469026_00482.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004469026/004469026_00482.jpg), [`004469026_00483.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004469026/004469026_00483.jpg) |
| **`ENSENADA-INTERROGATORIO`** | `ALTO_ALBERCHE` | `INTERROGATORIO_PREVENTIVO` | 101 | [`004469028_00785.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004469028/004469028_00785.jpg), [`004469028_00786.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004469028/004469028_00786.jpg) |
| **`JMOL-ENSENADA-BIENES-01`** | `JMOL` | `BIENES_LEGOS` | 270 | [`004469027_01891.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004469027/004469027_01891.jpg), [`004469027_01892.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004469027/004469027_01892.jpg) |
| **`JMOL-ENSENADA-BIENES-02`** | `JMOL` | `BIENES_LEGOS` | 270 | [`004469027_02161.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004469027/004469027_02161.jpg), [`004469027_02162.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004469027/004469027_02162.jpg) |
| **`JMOL-ENSENADA-LEGOS-01`** | `JMOL` | `LIBRO_LEGOS` | 28 | [`004469028_00959.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004469028/004469028_00959.jpg), [`004469028_00960.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004469028/004469028_00960.jpg) |
| **`NDRN-ENSENADA-BIENES-01`** | `NDRN` | `BIENES_LEGOS` | 209 | [`004469028_01633.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004469028/004469028_01633.jpg), [`004469028_01634.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004469028/004469028_01634.jpg) |
| **`NDRN-ENSENADA-BIENES-02`** | `NDRN` | `BIENES_LEGOS` | 208 | [`004469028_01842.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004469028/004469028_01842.jpg), [`004469028_01843.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004469028/004469028_01843.jpg) |
| **`NDRN-ENSENADA-BIENES-03`** | `NDRN` | `BIENES_LEGOS` | 208 | [`004469028_02050.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004469028/004469028_02050.jpg), [`004469028_02051.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004469028/004469028_02051.jpg) |
| **`NDRN-ENSENADA-LEGOS-01`** | `NDRN` | `LIBRO_LEGOS` | 34 | [`004469028_00988.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004469028/004469028_00988.jpg), [`004469028_00989.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004469028/004469028_00989.jpg) |
| **`NRDL-ENSENADA-BIENES-01`** | `NRDL` | `BIENES_LEGOS` | 218 | [`004469033_00282.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004469033/004469033_00282.jpg), [`004469033_00283.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004469033/004469033_00283.jpg) |
| **`NRDL-ENSENADA-BIENES-02`** | `NRDL` | `BIENES_LEGOS` | 218 | [`004469033_00500.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004469033/004469033_00500.jpg), [`004469033_00501.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004469033/004469033_00501.jpg) |
| **`NRDL-ENSENADA-BIENES-03`** | `NRDL` | `BIENES_LEGOS` | 217 | [`004469033_00718.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004469033/004469033_00718.jpg), [`004469033_00719.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004469033/004469033_00719.jpg) |
| **`NRDL-ENSENADA-LEGOS-01`** | `NRDL` | `LIBRO_LEGOS` | 87 | [`004469033_00902.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004469033/004469033_00902.jpg), [`004469033_00903.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004469033/004469033_00903.jpg) |
| **`VLLR-ENSENADA-BIENES-01`** | `VLLR` | `BIENES_LEGOS` | 261 | [`004469027_02429.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004469027/004469027_02429.jpg), [`004469027_02430.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004469027/004469027_02430.jpg) |
| **`VLLR-ENSENADA-BIENES-02`** | `VLLR` | `BIENES_LEGOS` | 261 | [`004469027_02690.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004469027/004469027_02690.jpg), [`004469027_02691.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004469027/004469027_02691.jpg) |
| **`VLLR-ENSENADA-BIENES-03`** | `VLLR` | `BIENES_LEGOS` | 260 | [`004469027_02951.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004469027/004469027_02951.jpg), [`004469027_02952.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004469027/004469027_02952.jpg) |
| **`VLLR-ENSENADA-LEGOS-01`** | `VLLR` | `LIBRO_LEGOS` | 51 | [`004469028_00913.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004469028/004469028_00913.jpg), [`004469028_00914.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004469028/004469028_00914.jpg) |

### 5.2. Carril Auxiliar: Aparato Auxiliar (`CONFIRMACION`, `INDICE`, `AUTO_VISITA`, `MEMORIA_MISAS`)

Los índices alfabéticos tabulares, nóminas de confirmaciones, autos de visita pastoral y memorias de misas representan un volumen reducido de folios con estructura especializada. Se procesan en un carril aparte mediante extracción directa con Gemini 4 (o mediante un motor auxiliar opcional dedicado), sin mezclarse con los 3 Motores Parroquiales de series sacramentales narrativas.

- **Índice de Bautismos y Matrimonios (`JMOL-INDICE-BAUT`):** [`004298570_02665.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004298570/004298570_02665.jpg) (`imagenes/rollo 004298570/004298570_02665.jpg`)
- **Índice de Defunciones (`JMOL-INDICE-DIFU`):** [`004298571_01545.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004298571/004298571_01545.jpg) (`imagenes/rollo 004298571/004298571_01545.jpg`)
- **Padrón de Confirmaciones 1649 (`NRDL-BAUT-01`):** [`004306112_02068.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004306112/004306112_02068.jpg) (`imagenes/rollo 004306112/004306112_02068.jpg`)
- **Padrón de Confirmaciones 1681 (`NRDL-BAUT-01`):** [`004306112_02114.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004306112/004306112_02114.jpg) (`imagenes/rollo 004306112/004306112_02114.jpg`)
- **Confirmaciones 1742 (`JMOL-BAUT-01`):** [`004298570_01762.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004298570/004298570_01762.jpg) (`imagenes/rollo 004298570/004298570_01762.jpg`)
