# Playbook Operativo Optimizado para un Pueblo Nuevo (Caso Piloto: Navalmoral de la Sierra — `NMRL`)

> **Propósito:** Recoger de forma estructurada todas las lecciones empíricas aprendidas en **Navarredondilla (`NRDL`)** y **San Juan del Molinillo (`JMOL`)** para procesar un nuevo fondo parroquial (**`NMRL`**, parroquia matriz del Alto Alberche pre-1715) en una línea de montaje limpia, sin exploraciones a ciegas ni retrabajos posteriores.

---

## 1. Fase 0 — Mapeo de Catálogo Previo (Antes de Descargar)
1. **Auditoría del catálogo de FamilySearch (`NMRL` + rollos pendientes de `JMOL`):**
   - Listar todos los rollos DGS, ítems y horquillas de años reales antes de abrir ningún visor.
   - Comprobar el corte cronológico por privacidad (~1890–1920) y verificar en `JMOL` si los **Bautismos `1863–1921`** y **Defunciones `1893–1907`** (cuyos índices ya extrajimos) existen en otros rollos.
   - Priorizar los tomos de **Navalmoral de la Sierra anteriores a 1715**, esenciales para entroncar los linajes fundacionales de `JMOL`, `NDRN` y `VLLR`.

---

## 2. Fase 1 — Descarga Acotada, Verificación de Huecos y «Piedra Rosetta» desde el Día 1
1. **Trazabilidad desde origen (`[L-28]` y `[ARK-01]`):**
   - Nombrado canónico `{rollo_dgs}_{fotograma}.jpg` desde la ingesta en [`catalogo_corpus.json`](file:///c:/TRABAJOS/personal/genealo/catalogo_corpus.json).
   - Captura conjunta de `url_ark` desde la vista de cuadrícula de miniaturas (con [`extraer_arks_familysearch.js`](file:///c:/TRABAJOS/personal/genealo/extraer_arks_familysearch.js)), priorizando los ítems genealógicos clave sin sobrecargar peticiones.
   - Script automático en local para verificar la **continuidad numérica de fotogramas** y detectar saltos o duplicados (`toma_hermana_de`).
2. **Construcción inmediata de la «Piedra Rosetta» de equivalencias:**
   No fiarse únicamente de la cartela de FamilySearch (propensa a erratas de fechas o pueblos intrusos). Cruzar siempre las **4 nomenclaturas** en una tabla única:
   - **Pegatina manuscrita del Archivo Diocesano en la tapa** (`Sit. Arch. ...`, `Nº ...` — fuente real habitual del volumen).
   - **Cartela de FamilySearch** (`Vol. X, Item Y`).
   - **Número de Libro citado en los Índices** (`Libro 1.º, 2.º...` — que suele omitir tomos mixtos o contar por serie).
   - **Rango exacto `.jpg` y Cuaderno(s) lógico(s)**.

---

## 3. Fase 1 bis — Barrido Completo de Principio a Fin (Sin Fiarlo Solo a Portadas y Cierres)
La experiencia en `NRDL` y `JMOL` demuestra que mirar solo las 3 primeras y 2 últimas imágenes pasa por alto sorpresas encuadernadas en mitad del volumen (padrones de confirmaciones, índices intercalados, autos de visita pastoral, inventarios, defunciones/matrimonios apuntados en huecos, folios dislocados o reescrituras tardías). Para blindar esto en **dos pasos ultraligeros**:

1. **Hojas de Contacto locales (coste 0 de NotebookLM):**
   - Montar con Python + OpenCV mosaicos PNG de `4×4` o `5×5` miniaturas por ítem con el nombre `.jpg` impreso al pie de cada celda.
   - Un libro de 200 fotos queda en 8–10 mosaicos que un agente ligero (`Hydrogen`) inspecciona en ~1–2 minutos a coste \$0 para señalar visualmente todo cambio de diseño (tablas de confirmación, índices en columna, páginas casi en blanco, cartas pastorales, roturas, pueblos ajenos).
2. **Barrido Único Codicológico + Censo de Manos (en 1 sola pasada):**
   - En NotebookLM, consultar **en una única pasada por tramos de $\le 75$ imágenes** para obtener simultáneamente:
     1. La tabla de manos/escribientes + clúster `C01–C12` + rango `.jpg` + `N_Folios_Aprox`.
     2. Todas las anomalías internas, cambios de sacramento, visitas pastorales (`[L-32]`), confirmaciones y dislocaciones cronológicas.

---

## 4. Fase 2 — Cuadernos Limpios y Equilibrados en NotebookLM AI Pro (`200–260` Imágenes)
En lugar de heredar tamaños desiguales de libro físico (cuadernos de 17 fotos frente a otros de 276) ni subir códices mixtos para desarticularlos a posteriori:

1. **Separación previa en local (`[L-29]`, `[L-30]`, `[L-31]`):**
   - Los códices mixtos y bífidos se particionan en local **antes** de subirlos, enviando cada tramo directamente a su cuaderno de Serie Pura (`BAUT`, `MATR`, `DIFU`, `CONFIRMACIONES` o `INDICE`).
   - Se excluyen previamente pueblos intrusos del rollo (como ocurrió con *Rivilla/Salobral*, *Grajos* o *Navarrevisca*).
2. **Dimensionamiento óptimo para NotebookLM AI Pro (límite `300` fuentes/cuaderno):**
   - Agrupar tomos correlativos cortos de la misma serie pura en **cuadernos equilibrados de `200–260` imágenes** (máximo `280`, dejando `~20` espacios libres para las guías `.md` y ajustes). Esto reduce drásticamente el número de cuadernos que administrar y da continuidad temporal a los análisis sin topar con el límite de `50` fuentes del plan gratuito.
3. **Regla de Oro de Consulta (`-s source_ids`) para Cero Timeouts y Respeto a la Ventana 5h:**
   - **Almacenar en grande (`200–260`), consultar en pequeño (`-s`)**:
     - Barrido de manos/codicológico: tramos de `<= 75` imágenes.
     - Cotejo de dudas concretas: ventanas estrechas de **`~20–25` imágenes estimadas por folio** (`1 folio ≈ 1 imagen`), no solo por año.
     - Extracción diplomática `[L-03]`: microlotes de **`1–4` imágenes** seguidas con `ChatSettings` (`LONGER`) para activar la segunda pasada visual VLLM sobre píxeles sin superar el timeout RPC (~240–360 s) ni agotar innecesariamente la ventana móvil de 5 horas.

---

## 5. Fase 3 — Índices Primero (`Molde LISTA`, Coste \$0) $\rightarrow$ Diccionario `01` Antes de Leer Partidas
Si `NMRL` dispone de libros de Índices:
1. Ejecutar primero [`extraer_lista_gemini.py`](file:///c:/TRABAJOS/personal/genealo/scripts/vllm_notebooklm/extraer_lista_gemini.py) (`--slice-batch --strips 4` + recorte automático de lomo/borde negro) y lectura con subagentes `Hydrogen` (**\$0 API**).
2. De esos CSV se derivan automáticamente en el día 1:
   - La auditoría de monotonía de folios y de huecos de libros/años (incluyendo cuadernos extraordinarios o de convalidación como `JMOL-SACRAMENTAL-1842-1850`).
   - El diccionario pasivo **`01_DICCIONARIO_ANCLAJE_<PUEBLO>.md`** (apellidos reales con frecuencia, detección temprana de sesgos de lectura tipo `Audrino`/`Lucabo` y nómina de párrocos).
3. Cotejar dudas/alertas contra los libros en NotebookLM (ventana estrecha por folio) o directamente con **`Gemini 4 Neon`** sobre las tiras PNG si algún libro falta de los microfilmes.

---

## 6. Fase 4 — Transferencia Kraken (`blla` + `M1/M2/M3`) + Ingesta en `ArcadeDB`
1. Con el Censo de Manos Pareto de `NMRL`, comprobar qué escribanos coinciden con los **485 ya censados en `JMOL` + `NRDL`**.
2. Aplicar directamente el segmentador **`blla_alto_alberche.mlmodel`** y los 3 motores de reconocimiento **`M1 (C01–C05)`**, **`M2 (C06–C10)`** y **`M3 (C11+C12)`**, reservando solo un **micro-*fine-tuning* de ~10–15 folios** en **Google Colab Pro (`genealo.ipynb`)** para las principales manos exclusivas de `NMRL` (en especial s. XVI–principios XVIII).
3. Volcar primero los índices como esqueleto en **ArcadeDB** y enlazar progresivamente las partidas completas con su `url_ark` para resolver el entronque comarcal **`NMRL` $\leftrightarrow$ `JMOL` / `NDRN` / `VLLR` / `NRDL`**.
