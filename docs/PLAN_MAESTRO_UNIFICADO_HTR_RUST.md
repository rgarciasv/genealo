# Plan Maestro Unificado: Del Microfilm a la Aplicación de Escritorio en Rust (HTR + PAGE-XML + NER)

> **Propósito de este documento («Memoria Total del Proyecto»):**
> Este documento es la hoja de ruta única y auto-contenida del proyecto genealógico e histórico del **Alto Alberche (Ávila, 1594–1902)** y del **Catastro del Marqués de la Ensenada (1751–1752)**. Está diseñado para que en cualquier sesión futura podamos retomar el trabajo en menos de 2 minutos sabiendo exactamente:
> 1. **Qué hemos construido ya** y por qué cada pieza existe.
> 2. **Cómo encajan las 4 capas** (Corpus $\rightarrow$ Ground Truth & Clusters Kraken $\rightarrow$ NER & Tipologías Documentales $\rightarrow$ App Nativa en Rust para Indexadores).
> 3. **En qué fase estamos hoy** y cuál es el siguiente paso concreto.

---

## 1. Visión General: Las 4 Capas del Proyecto

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ CAPA 1: ARCHIVO Y RECONSTRUCCIÓN CODICOLÓGICA (✅ COMPLETADA EN PARROQUIAS)          │
│ • 13.719 imágenes JPG catalogadas en catalogo_corpus.json                           │
│ • 33 cuadernos canónicos en NotebookLM Pro auditados al 100% (0 errores)            │
│ • Mapas de manos, escribanos (03_AUTORIDADES_PALEOGRAFICAS) y dislocaciones (02)    │
│ • Pendiente en reserva: Subida a NotebookLM de los 11 cuadernos de Bienes de Legos  │
└─────────────────────────────────────────┬───────────────────────────────────────────┘
                                          ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ CAPA 2: FÁBRICA LOCAL DE GROUND TRUTH Y MOTORES KRAKEN POR CLUSTERS (🔄 FASE ACTUAL) │
│ • 100% Local en Windows 11 (Adiós a eScriptorium Web UI)                            │
│ • Estándar único de intercambio: PAGE-XML 2019-07-15                                │
│ • Segmentación local: segmentar_lote.py (Kraken 7.2 BLLA, ~18 s/folio en local)     │
│ • Edición geométrica: Aletheia 4.1 portable + recalcular_mascaras_aletheia.py       │
│ • Transcripción diplomática (solo para fabricar GT): transcribir_pagexml.py (Gemini)│
│ • Taxonomía pura C01–C12 en 3 Motores Parroquiales + Carril Auxiliar y Ensenada     │
└─────────────────────────────────────────┬───────────────────────────────────────────┘
                                          ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ CAPA 3: INFERENCIA OFFLINE + EXTRACCIÓN ESTRUCTURADA (NER GENEALÓGICO Y CATASTRAL)  │
│ • Inferencia de texto 100% local con modelos Kraken fine-tuned (.mlmodel)           │
│ • Agrupación automática de Partida (<ReadingOrder>: margen_indice + cuerpo + firma) │
│ • Motor NER local (Reglas diplomáticas + GLiNER / ONNX local) para 6 tipologías:    │
│   1. Bautismos / Nacimientos   3. Defunciones            5. Índices Parroquiales    │
│   2. Matrimonios / Velaciones  4. Listas de Confirmación 6. Ensenada (Legos/Bienes) │
│ • Fallback puntual opcional: API gratuita Google AI Studio / OpenRouter (solo dudas)│
└─────────────────────────────────────────┬───────────────────────────────────────────┘
                                          ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ CAPA 4: APLICACIÓN DE ESCRITORIO NATIVA EN RUST PARA INDEXADORES (🎯 PRODUCTO FINAL) │
│ • Binario nativo redistribuible en Rust (egui + wgpu + lyon + cosmic-text)          │
│ • Sustituye el trabajo manual de teclear partida a partida en Excel                 │
│ • Tres vistas sincronizadas:                                                        │
│   [A] Lienzo PAGE-XML (inspirado en Aletheia: tijera/pegamento de baselines, 4 reg.)│
│   [B] Visor sincronizado línea a línea (recorte de polígono + teclado 16 glifos)    │
│   [C] Ficha / Tabla NER editable (validación rápida con Tab/Enter -> Excel/ArcadeDB)│
│ • Escalable a todos los pueblos del Alto Alberche y al resto de parroquias de Ávila │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Decisiones Arquitectónicas Definitivas (Reglas de Oro)

### 2.1. Abandono definitivo de eScriptorium Web UI (`[L-42]`)
* **Decisión:** No volvemos a levantar ni depender de la interfaz web de eScriptorium en servidor para segmentar, revisar o transcribir. La instancia `escriptorium-spot-vm` permanece apagada (`TERMINATED`, `$0.00/h`) y solo se reserva como recurso opcional de cómputo por línea de comandos (`ketos train` / `ketos segtrain` en GPU Tesla T4) si algún lote masivo supera a la GPU local (**NVIDIA GeForce RTX 3050 Ti Laptop GPU**).
* **Por qué:** En el portátil local, `Kraken 7.2` segmenta cada folio en **16–22 segundos** (frente a los 420 segundos en la CPU remota) y `PAGE-XML` nos permite trabajar directamente sobre los archivos locales con **Aletheia 4.1** y nuestros scripts modulares.

### 2.2. `PAGE-XML` (`2019-07-15`) como columna vertebral única
Todo el flujo habla un único idioma de archivo: un par **`<imagen>.jpg` + `<imagen>.xml`** en formato `PAGE-XML`.
* Guarda las **regiones semánticas** (`<TextRegion>`).
* Guarda la **asociación entre margen, cuerpo y firma de una misma partida** (`<ReadingOrder>` $\rightarrow$ `<OrderedGroup id="partida_01">`).
* Guarda la **línea base** (`<Baseline points="..."/>`) y la **máscara poligonal** (`<Coords points="..."/>`) de cada `<TextLine>`.
* Guarda la **transcripción diplomática** (`<TextEquiv><Unicode>...</Unicode></TextEquiv>`).

### 2.3. Esquema Cerrado de 4 Regiones Semánticas y Asociación de Partida
Para que el modelo segmentador de Kraken (`ketos segtrain`) aprenda con máxima precisión sin fragmentar las muestras en clases raras, usamos **exactamente 4 tipos de región**:

| `#` | Tipo de Región (`custom="structure {type:...;}"`) | Qué contiene | Uso en el flujo HTR + NER |
| :--- | :--- | :--- | :--- |
| **1** | `cuerpo_partida` | El bloque principal del asiento sacramental, lista de confirmados o asiento catastral. | Se transcribe completo y alimenta el extractor NER principal. |
| **2** | `margen_indice` | El nombre o resumen anotado en el margen izquierdo o derecho (a menudo separado por llave `}` o línea vertical). | Se transcribe y sirve de **ancla de validación cruzada** del sujeto principal de la partida. |
| **3** | `firma` | Rúbricas y firmas autógrafas al pie del asiento (`Dⁿ Joseph Ximenez`, `Juan Lopez`). | Identifica al párroco/escribano (autoridad paleográfica) y cierra la partida. |
| **4** | `nota_extra` | Numeración de folio, reclamos al pie, notas marginales tardías (`Casó en...`, `Sacóse fe`), subtotales o texto vertical. | Se conserva separado para no contaminar el texto del `cuerpo_partida`. |

#### ¿Cómo se une cada `margen_indice` con su `cuerpo_partida` y su `firma`?
Como el margen no siempre está a la misma altura geométrica que la primera línea del cuerpo, aplicamos una **estrategia dual**:
1. **En Ground Truth curado y en la App de Escritorio (`PAGE-XML <ReadingOrder>`)**:
   * Agrupamos las regiones de una misma partida dentro de un `<OrderedGroup id="partida_01" caption="Partida 1">` en la cabecera `<ReadingOrder>` del `PAGE-XML` (soportado nativamente por Aletheia 4.1 con su herramienta *Grouping / Reading Order*).
   * Además, prefijamos los IDs de región como `p01_margen`, `p01_cuerpo`, `p01_firma`.
2. **En Inferencia Automática sobre folios nuevos**:
   * El post-procesador (`htr_pipeline/postprocess.py`) combina **solapamiento vertical flexible** con **anclaje léxico difuso (Fuzzy Name Anchor)**: busca el nombre transcrito en `margen_indice` (ej. `Maria / hija de Po.`) dentro de las 4 primeras líneas de los `cuerpo_partida` candidatos en la misma plana.

### 2.4. Inventario Cerrado de 16 Caracteres Especiales Unicode (`[L-39]` / `[L-41]`)
Prohibida la normalización ortográfica (`s` alta/baja, `u`/`v`, `b`/`v`, `ç`/`z`, `x`/`j`). Solo se permiten letras estándar, signos de puntuación originales y estos **16 glifos especiales cerrados**:

| Categoría | Glifos Permitidos | Codepoints Unicode | Ejemplos Reales del Corpus |
| :--- | :--- | :--- | :--- |
| **Ordinales / Superíndices vocales** | `ª`, `º`, `ᵉ` | `U+00AA`, `U+00BA`, `U+1D49` | `mª`, `franᶜᵒ`, `pº`, `Juº`, `dº`, `pᵉ` |
| **Superíndices consonánticos** | `ᶜ`, `ᵈ`, `ᵐ`, `ⁿ`, `ʳ`, `ˢ`, `ᵗ`, `ˡ` | `U+1D9C`, `U+1D48`, `U+1D50`, `U+207F`, `U+02B3`, `U+02E2`, `U+1D57`, `U+02E1` | `franᶜᵒ`, `mʳᵈ`, `lexᵐᵒ`, `Dⁿ`, `Bʳ`, `tsˢ`, `stᵗᵃ`, `Migˡ`, `Manˡ` |
| **Diacrítico combinante de abreviatura** | `◌̄` (sobre letra base) | `U+0304` (`COMBINING MACRON`) | `q̄`, `n̄`, `m̄`, `cō`, `ē`, `Jū` |
| **Grafías históricas hispanas** | `ç`, `Ç`, `ñ`, `Ñ` | `U+00E7`, `U+00C7`, `U+00F1`, `U+00D1` | `baçiador`, `março`, `año`, `niño` |

> **Nota crítica:** Quedan prohibidos `ᵒ` (`U+1D52`), `ᵃ` (`U+1D43`) y `°` (`U+00B0`), que se sustituyen automáticamente por `º` (`U+00BA`) y `ª` (`U+00AA`).

### 2.5. Los 3 Moldes Documentales (`PARTIDA` / `LISTA` / `DOCUMENTO_SINGULAR`), Folio por Anclas y Muestreo 50/50 (`[L-45]`)
Toda página útil de los libros parroquiales encaja en **3 moldes estructurales**:
1. **`PARTIDA` (~92% del corpus):** Bautismos, Matrimonios y Defunciones regulares (`margen_indice` + `cuerpo_partida` + `firma`, pudiendo continuar al folio siguiente `[L-25]`). Procesado con los **3 Motores Kraken Parroquiales** (`C01–C12`) entrenados con Ground Truth **50% folios limpios + 50% folios degradados reales** (manchas de agua, *bleed-through*, tinta pálida).
2. **`LISTA` (~5% del corpus: ~250–350 fotos):** Índices (`JMOL-INDICE-BAUT-MAT`, `JMOL-INDICE-DIFU`), Padrones de Confirmaciones, `JMOL-DIFU-PARVULOS`, Memorias de Misas e Inventarios. Se procesa sin entrenar Kraken mediante **recorte local en 4 tiras horizontales solapadas por plana/columna** (`scripts/vllm_notebooklm/extraer_lista_gemini.py`, con `_wide_true_bounds`), lectura por subagentes (`Hydrogen` pasada 1 + `Neon` solo en dudas/alertas, **coste `$0` de API**), propagación determinista de `id` y auditoría de monotonía de folios (validado en **Experimento 26**).
3. **`DOCUMENTO_SINGULAR` (~3%):** Autos de Visita Pastoral (`[L-32]`), Licencias impresas, Decretos del Provisor y certificaciones sueltas; catalogados ya en las 33 auditorías y extraídos bajo demanda.
* **Reconstrucción del Número de Folio:** la clave física inmutable es siempre `imagen_id + plana`; el folio manuscrito se reconstruye automáticamente entre **anclas legibles** mediante interpolación secuencial (`leido` / `inferido`), lanzando alertas ante saltos o folios arrancados.

---

## 3. Cómo Aprovechamos los 33 Cuadernos de NotebookLM ya Organizados

El trabajo previo de organizar y auditar los **33 cuadernos en NotebookLM Pro** y redactar [`03_AUTORIDADES_PALEOGRAFICAS_ALTO_ALBERCHE.md`](file:///c:/TRABAJOS/personal/genealo/03_AUTORIDADES_PALEOGRAFICAS_ALTO_ALBERCHE.md) y los 33 informes en [`transcripciones/auditoria_codicologica/`](file:///c:/TRABAJOS/personal/genealo/transcripciones/auditoria_codicologica/) es nuestra **mina de oro para entrenar Kraken sin buscar a ciegas**:

1. **Selección Quirúrgica de Muestras por Cluster (`C01–C12`) y Separación de Ejes**:
   * Gracias a las auditorías codicológicas y al registro de autoridades paleográficas, ya sabemos **qué párroco o escribano escribió en qué rango exacto de años e imágenes `DGS`** en Navarredondilla, San Juan del Molinillo, Navandrinal, El Villarejo y Navalmoral.
   * Siguiendo la fuente única de verdad en [`docs/PIPELINE_HTR_Y_TAXONOMIA_CLUSTERS_PALEOGRAFICOS.md`](file:///c:/TRABAJOS/personal/genealo/docs/PIPELINE_HTR_Y_TAXONOMIA_CLUSTERS_PALEOGRAFICOS.md), separamos estrictamente el **Eje 1 (Morfografía pura del trazo: `C01–C12`)** del **Eje 2 (Tipología documental)**.
   * El mapa generado en [`docs/MAPA_MUESTREO_CLUSTERS_C01_C12.md`](file:///c:/TRABAJOS/personal/genealo/docs/MAPA_MUESTREO_CLUSTERS_C01_C12.md) nos dice exactamente qué archivos `.jpg` locales sacar para entrenar los **3 Motores Kraken Parroquiales** (que cubren `C01–C12` para `BAUTISMO`, `MATRIMONIO` y `DEFUNCION`), dejando aparte los **2 carriles independientes**:
     * **Motor 1 (`alto_alberche_antiguo_c01_c05.mlmodel`)**: Bloque Antiguo (`C01–C05`, ~1594–1680: Gótico-cortesana tardía, Procesal redonda/abierta, Procesal encadenada pura, Humanística/Itálica libraria e Híbrida procesal-bastarda) + muestras transversales de `C12` (Rústica/senil o temblorosa).
     * **Motor 2 (`alto_alberche_bastardo_c06_c10.mlmodel`)**: Bloque Bastardo (`C06–C10`, ~1660–1840: Bastarda cancilleresca/magistral, Bastarda angulosa/picuda, Bastarda corriente/desbordada, Micro-cursiva compacta y Bastarda ilustrada/neoclásica) + muestras transversales de `C12`.
     * **Motor 3 (`alto_alberche_plumilla_c11.mlmodel`)**: Bloque Plumilla Metálica / Decimonónico (`C11`, ~1840–1902: Cursiva inglesa/comercial de plumilla metálica) + muestras transversales de `C12`.
     * **Carril Auxiliar (`Aparato Auxiliar`)**: `CONFIRMACION`, `INDICE`, `AUTO_VISITA` y `MEMORIA_MISAS` (pocos folios y maquetación tabular/especializada; extracción directa con Gemini 4 o motor auxiliar opcional fuera de los 3 motores parroquiales).
     * **Carril Independiente (`Catastro de Ensenada`)**: `ENSENADA_LEGOS` y `ENSENADA_BIENES` van por un camino completamente separado de los libros parroquiales, ya que un mismo escribano real de comisión solía redactar todos los volúmenes de un pueblo e incluso de pueblos colindantes; cuando toque entrenar Kraken para Ensenada, se entrenará aparte combinando múltiples fondos/manos de Ensenada distintos para evitar sobreajuste a un solo escribano.
2. **Diccionario Histórico de Entidades para el NER Local**:
   * Los archivos [`01_LEXICO_Y_TOPONIMIA_MENOR_ALTO_ALBERCHE.md`](file:///c:/TRABAJOS/personal/genealo/01_LEXICO_Y_TOPONIMIA_MENOR_ALTO_ALBERCHE.md), [`03_AUTORIDADES_PALEOGRAFICAS_ALTO_ALBERCHE.md`](file:///c:/TRABAJOS/personal/genealo/03_AUTORIDADES_PALEOGRAFICAS_ALTO_ALBERCHE.md) y [`04_HISTORIA_Y_CRONOLOGIA_CANONICA_ALTO_ALBERCHE.md`](file:///c:/TRABAJOS/personal/genealo/04_HISTORIA_Y_CRONOLOGIA_CANONICA_ALTO_ALBERCHE.md) alimentan directamente los diccionarios locales de apellidos, topónimos menores, oficios y sacerdotes del motor NER, permitiendo corregir errores de OCR/HTR sin llamar a ninguna API externa.

---

## 4. Eje 2 — Tipologías Documentales y sus Plantillas NER

> **Separación estricta de Ejes:** El **Eje 1 (`C01–C12`)** describe únicamente la geometría del trazo para elegir el motor HTR adecuado, mientras que el **Eje 2** define la tipología documental y su esquema NER. El sistema (primero en Python y luego integrado en la App en Rust) soporta **6 plantillas principales** (más `AUTO_VISITA` y `MEMORIA_MISAS` dentro del Aparato Auxiliar) a partir de los bloques `<OrderedGroup>` del `PAGE-XML`:

### A. Series Sacramentales Narrativas (Carril Parroquial — Motores 1, 2 y 3)

### 4.1. Bautismos y Nacimientos (`BAUTISMO`)
* **Campos extraídos**: `id_partida`, `folio`, `fecha_bautismo`, `fecha_nacimiento`, `bautizado_nombre`, `bautizado_sexo`, `legitimidad` (legítimo, natural, expósito), `padre_nombre`, `padre_apellidos`, `padre_naturaleza`, `padre_vecindad`, `madre_nombre`, `madre_apellidos`, `madre_naturaleza`, `abuelos_paternos`, `abuelos_maternos`, `padrinos`, `testigos`, `ministro_celebrante`, `firma_parroco`, `notas_marginales`.

### 4.2. Matrimonios y Velaciones (`MATRIMONIO`)
* **Campos extraídos**: `id_partida`, `folio`, `fecha_desposorio`, `fecha_velacion`, `contrayente_varon` (nombre, apellidos, estado civil previo, viudo de, naturaleza, vecindad, padres), `contrayente_mujer` (nombre, apellidos, estado civil previo, viuda de, naturaleza, vecindad, padres), `dispensas_consanguinidad` (grado, bula), `amonestaciones_fechas`, `padrinos`, `testigos`, `ministro_celebrante`, `notas_marginales`.

### 4.3. Defunciones y Entierros (`DEFUNCION`)
* **Campos extraídos**: `id_partida`, `folio`, `fecha_defuncion`, `fecha_entierro`, `difunto_nombre`, `difunto_apellidos`, `clase_parvulo_adulto`, `edad_declarada`, `estado_civil`, `conyuge_nombre`, `padres_difunto`, `recibio_sacramentos`, `testamento` (sí/no, fecha, escribano, albaceas, misas), `lugar_sepultura` (tramo, capilla, cementerio), `ministro_firmante`.

### B. Aparato Auxiliar (Carril Aparte — Extracción directa con Gemini 4 o motor auxiliar opcional)

> Incluye también `AUTO_VISITA` y `MEMORIA_MISAS`. Al representar pocos folios y formatos tabulares o de decreto diferenciados, no se mezclan con el entrenamiento de los 3 Motores Parroquiales.

### 4.4. Listas de Confirmación (`CONFIRMACION`)
* **Estructura**: Cabecera episcopal única (`fecha_visita`, `obispo_confirmante`, `parroquia`) + tabla multi-registro donde cada línea o par de líneas es un confirmado (`confirmado_nombre`, `padre_nombre`, `madre_nombre`, `padrino_confirmacion`, `edad`).

### 4.5. Índices Parroquiales y Abecedarios (`INDICE`)
* **Estructura**: Listados tabulares por letra inicial o año (`letra_abecedario`, `nombre_indexado`, `apellidos_indexados`, `padres_resumen`, `libro_referencia`, `folio_referencia`, `anio_referencia`). Sirven además para autocompletar y verificar huecos en los libros sacramentales.

### C. Carril HTR Independiente — Catastro del Marqués de la Ensenada

### 4.6. Catastro del Marqués de la Ensenada (`ENSENADA_LEGOS` y `ENSENADA_BIENES`)
> **Carril Independiente de Entrenamiento:** El Catastro de Ensenada sigue un flujo HTR separado de los libros parroquiales. Un mismo escribano real de comisión solía redactar todos los volúmenes de un pueblo e incluso de pueblos colindantes; por ello, cuando se entrene Kraken para Ensenada, se combinarán múltiples fondos y manos de Ensenada distintos para evitar el sobreajuste a un único escribano.
1. **Libro Personal de Legos (Vecindario / Familias)**:
   * `cabeza_casa_nombre`, `apellidos`, `estado_civil`, `oficio_categoria`, `edad`, `conyuge`, `hijos_detalle` (nombre, edad, oficio), `criados_detalle` (`soldada`).
2. **Libro Real de Bienes de Legos (Hacienda / Parcelas / Ganado / Censos)**:
   * **Cabecera de Titular**: `titular_nombre`, `vecindad`.
   * **Asientos de Casas**: `tipo_inmueble`, `ubicacion_calle`, `medidas_varas`, `renta_anual`, `linderos` (`L.`, `P.`, `M.`, `N.`).
   * **Asientos de Tierras/Prados/Viñas/Huertos**: `tipo_predio`, `pago_toponimo_menor`, `distancia_pueblo`, `cabida` (`fanegas`, `celemines`, `peonadas`, `obradas`), `calidad` (`1ª`, `2ª`, `3ª`), `linderos` (`Levante`, `Poniente`, `Mediodía`, `Norte`), `producto_especie`.
   * **Ganados y Censos**: `especie_ganado`, `numero_cabezas`, `censo_principal`, `censo_reditos`, `acreedor_capellania`.

---

## 5. Las 4 Fases Secuenciales de Ejecución

### FASE 1: Flujo Local `PAGE-XML` y Fábrica de Ground Truth (HOY — En Curso)
**Objetivo:** Dominar y producir los primeros lotes limpios de Ground Truth `PAGE-XML` en local sin tocar ningún servidor web.

* **Paso 1.1 (Segmentación Local)**:
  ```powershell
  .\.venv\Scripts\python.exe scripts/htr_kraken/segmentar_lote.py --input-dir htr_pipeline/inputs/<lote> --output-dir htr_pipeline/outputs/<lote>
  ```
* **Paso 1.2 (Corrección Geométrica en Aletheia 4.1)**:
  * Abrir el par `.xml` + `.jpg` en `programs\Aletheia 4.1\Aletheia.exe`.
  * Usar **`Split`** (tijera) en las líneas donde la llave `}` del margen haya unido `margen_indice` con `cuerpo_partida`.
  * Asignar las 4 regiones (`cuerpo_partida`, `margen_indice`, `firma`, `nota_extra`) y agrupar cada partida en `<ReadingOrder>`.
  * Guardar el `.xml` en Aletheia.
* **Paso 1.3 (Recálculo Automático de Máscaras Poligonales)**:
  ```powershell
  .\.venv\Scripts\python.exe scripts/htr_kraken/recalcular_mascaras_aletheia.py --xml htr_pipeline/outputs/<lote>/<archivo>.xml
  ```
  *(Reconstruye las máscaras `<Coords>` de cada línea que hayas partido o movido en Aletheia usando la topología de Kraken).*
* **Paso 1.4 (Transcripción Diplomática Asistida para Ground Truth, `[L-44]`)**:
  ```powershell
  .\.venv\Scripts\python.exe scripts/htr_kraken/transcribir_pagexml.py --image <ruta.jpg> --xml <ruta.xml> --output-dir <salida> --mode partida --resolution ultra_high --thinking-level medium
  ```
* **Paso 1.5 (Revisión Humana Final en Aletheia 4.1)**:
  * Abrir el `.xml` enriquecido en Aletheia 4.1 (con el teclado virtual de 16 caracteres especiales ya configurado) y corregir solo las líneas marcadas en `cola_revision_*.json`.
* **Iniciativa Complementaria en Reserva (`C.4` en [`TODO.md`](file:///c:/TRABAJOS/personal/genealo/TODO.md), Prioridad Baja)**:
  * Banco de pruebas de VLLMs vía CLIs locales autenticados (`copilot.exe`, `codex exec --image`, `gemini`) ejecutado por script desatendido sobre recortes de partida o bloques de líneas frente a nuestro Ground Truth `PAGE-XML` (sin bucle agéntico en chat ni gasto extra de API).

### FASE 2: Muestreo de los 12 Clusters (`C01–C12`) y Entrenamiento de los 3 Motores Parroquiales
**Objetivo:** Entrenar nuestros propios modelos de segmentación (`blla_alto_alberche.mlmodel`) y de reconocimiento parroquial (`Motor 1` a `Motor 3`, dejando Aparato Auxiliar y Catastro de Ensenada en sus carriles independientes).

1. **Muestreo guiado por [`docs/MAPA_MUESTREO_CLUSTERS_C01_C12.md`](file:///c:/TRABAJOS/personal/genealo/docs/MAPA_MUESTREO_CLUSTERS_C01_C12.md)**:
   * Empezar por **3 folios por cluster** en los clusters prioritarios (`C11` cursiva inglesa de plumilla metálica que ya tenemos en `lote_prueba_5`, `C07` bastarda angulosa de `01608`, `C06`/`C08` bastarda cancilleresca y corriente, y `C02`/`C03` procesal del XVII). *(El Catastro de Ensenada se reserva para su carril independiente combinando múltiples fondos/manos).*
2. **Entrenamiento del Segmentador Local (`ketos segtrain`)**:
   * Con los primeros 15–20 folios corregidos en Aletheia con las 4 regiones (`cuerpo_partida`, `margen_indice`, `firma`, `nota_extra`) y las baselines cortadas en las llaves `}`, entrenamos el segmentador para que Kraken nunca más vuelva a unir el margen con el cuerpo.
3. **Entrenamiento de Reconocimiento (`ketos train`)**:
   * Fine-tuning sobre `catmus-medieval-1.6.0.mlmodel` con `NFD`, `augment: true` y validación de códec (`scripts/htr_kraken/check_kraken_codec.py`).
   * Evaluación objetiva de `CER` y `WER` con `PrimaText.jar` (incluido en `programs\Aletheia 4.1\bin\data\TextEval\PrimaText.jar`) o `ketos test`.

### FASE 3: Prototipo Local de Inferencia Kraken + Motor NER (Sin API de Pago)
**Objetivo:** Demostrar que un folio nuevo se segmenta, se transcribe con nuestro modelo Kraken local y se convierte automáticamente en registros estructurados (JSON / Excel / CSV) de las 6 tipologías.

1. **Inferencia Kraken Local (`inferir_lote_kraken.py`)**:
   * Toma un lote de imágenes nuevas, aplica `blla_alto_alberche.mlmodel` + el motor Kraken del cluster correspondiente y genera el `PAGE-XML` completo en local (coste API = `$0.00`).
2. **Asociación Automática de Partidas (`ReadingOrder` + Fuzzy Name Anchor)**:
   * Empareja cada `margen_indice` con su `cuerpo_partida` y su `firma`.
3. **Motor NER Híbrido Local (`htr_pipeline/ner_extractor.py`)**:
   * **Capa 1 (Gramática Diplomática y Expresiones Regulares Paleográficas)**: Patrones de apertura (`En el lugar de...`, `baptize solemnemente a...`, `casé y velé in facie ecclesiae...`, `sepultóse el cuerpo de...`), expansión de abreviaturas en capa semántica (`Juº` $\rightarrow$ `Juan`, `Franᶜᵒ` $\rightarrow$ `Francisco`, `lexᵐᵒ` $\rightarrow$ `legítimo`) manteniendo intacta la capa diplomática en el `PAGE-XML`.
   * **Capa 2 (Diccionarios Locales del Alto Alberche)**: Validación con los topónimos menores, apellidos y autoridades de las fuentes maestras `01`, `03` y `04`.
   * **Capa 3 (Fallback opcional gratuito)**: Solo para partidas con sintaxis muy alterada o ilegible, botón opcional para consultar `Google AI Studio (Free Tier)` o `OpenRouter (modelos gratuitos)`.

### FASE 4: Aplicación de Escritorio Nativa en Rust para Indexadores (`genealo-htr-desktop`)
**Objetivo:** Empaquetar todo el flujo en una aplicación nativa en Rust rápida, ergonómica y redistribuible para grupos de genealogía y para indexar todas las parroquias de Ávila.

---

## 6. Especificación Técnica de la App de Escritorio Nativa en Rust (Fase 4)

> **Documento de Ingeniería Inversa y Arquitectura Detallada en 7 Crates (Athalia):**
> Ver [**`docs/ANALISIS_ALETHEIA_PARA_APP_RUST.md`**](file:///c:/TRABAJOS/personal/genealo/docs/ANALISIS_ALETHEIA_PARA_APP_RUST.md) (`H-01` a `H-13`: disección de `Aletheia 4.1` con Ghidra/Craft Anything, equivalencia de sus 19 DLLs en Rust puro, algoritmos `Sauvola w=50, k=0.30`, `Shrink` Coarse + Fine RLSA, `Split/Merge`, bitflags, decompilación completa con CFR de `PrimaText.jar` en [`prima_java_src/org/primaresearch/text/`](file:///c:/TRABAJOS/personal/genealo/prima_java_src/org/primaresearch/text/) y estructura del Cargo Workspace de **7 crates** sin dependencia de JVM: `genealo-page-core`, `genealo-image`, `genealo-layout`, **`prima-text-rs` (`genealo-text-eval`)**, `genealo-htr-ner`, `genealo-desktop` y `genealo-cli`).

### 6.1. Stack Tecnológico 100% Rust Nativo
* **Framework GUI**: **`egui` + `eframe` (`wgpu` backend)** — interfaz en modo inmediato acelerada por GPU a 60–120 FPS, ideal para sincronizar un lienzo vectorial de alta resolución con tablas y formularios.
* **Teselación de Polígonos Cóncavos (`<Coords>`)**: **`lyon_tessellation`** o **`earcutr`** — convierte los polígonos orgánicos cóncavos de las máscaras de Kraken en mallas de triángulos (`egui::epaint::Mesh`) sin deformaciones y en microsegundos.
* **Geometría 2D Interactiva (Tijera / Pegamento / Hit-Testing)**: **`geo` + `kurbo`** — intersección de línea de corte con `<Baseline>`, proyección de punto a polilínea, cálculo de cajas envolventes y detección de clic dentro de polígono.
* **Shaping Tipográfico Paleográfico (`U+0304`, superíndices)**: **`cosmic-text` (`rustybuzz`)** + fuente **Junicode Two** embebida en el binario — garantiza que `n̄`, `q̄`, `m̄`, `franᶜᵒ`, `Migˡ` se dibujen al píxel sin desplazamientos.
* **Motor `PAGE-XML` (`2019-07-15`)**: **`quick-xml` + `serde`** — lectura y escritura ultrarrápida y tipada del estándar `PAGE-XML` de PRImA (compatible 100% con Aletheia 4.1 y Kraken).
* **Procesamiento de Imagen**: **`image` + `imageproc`** — carga de microfilms de `4500×3500 px`, recortes al vuelo de líneas individuales y filtros de mejora visual en tiempo real (contraste, CLAHE, inversión de tinta desvaída).
* **Base de Datos Local del Proyecto**: **`rusqlite` (SQLite embebido)** — guarda el estado de cada lote, las partidas extraídas por el NER, el historial de validación del indexador y permite exportar en un clic a **Excel (`.xlsx` vía `rust_xlsxwriter`)**, **CSV**, **GEDCOM 5.5.1/7.0** y **ArcadeDB (JSONL)**.
* **Puente de Inferencia HTR y NER**:
  * *Modo A (Subproceso / Sidecar Kraken)*: Invoca el entorno local de Kraken o un worker persistente por `stdin/stdout` JSON-RPC para segmentar e inferir con los `.mlmodel` entrenados.
  * *Modo B (ONNX Runtime nativo en Rust vía `ort`)*: Carga directa de modelos exportados a ONNX (`GLiNER` para NER genealógico y modelos VGSL de Kraken exportados) sin requerir instalación de Python en el PC del indexador.

### 6.2. Diseño de la Interfaz de Usuario (Lo mejor de Aletheia + Ficha NER)

```
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│ [Abrir Lote] [Cluster: C07 Bastarda Pic. ▼] [1. Segmentar] [2. Leer HTR] [3. Extraer NER] │
├────────────────────────────────────────┬─────────────────────────────────────────────────┤
│                                        │ PANEL DERECHO SUPERIOR: VISOR DE LÍNEA ACTIVA   │
│                                        │ ┌─────────────────────────────────────────────┐ │
│   PANEL IZQUIERDO: LIENZO PAGE-XML     │ │ [Recorte Poligonal con Zoom de Línea 14]    │ │
│   (Inspirado en Aletheia, simplificado)│ └─────────────────────────────────────────────┘ │
│                                        │ [ en veinte y seis de março de mil y seisºs   ] │
│   • Colores por las 4 Regiones:        │ [ª][º][ᶜ][ᵈ][ᵉ][ᵐ][ⁿ][ʳ][ˢ][ᵗ][ˡ][◌̄][ç][ñ]    │
│     - Azul:   cuerpo_partida           ├─────────────────────────────────────────────────┤
│     - Ámbar:  margen_indice            │ PANEL DERECHO INFERIOR: FICHA NER DE PARTIDA #3 │
│     - Verde:  firma                    │ (Vinculada por <ReadingOrder id="partida_03">)  │
│     - Gris:   nota_extra               │ • Tipo:      [Bautismo ▼]   Folio: [ 42v      ] │
│                                        │ • Margen:    [ Maria / hija de Po. Garcia     ] │
│   • Herramientas Rápidas (1 tecla):    │ • Fecha:     [ 26/03/1674                     ] │
│     [S] Tijera (Partir Baseline en })  │ • Bautizado: [ María García López             ] │
│     [M] Pegamento (Unir 2 Baselines)   │ • Padre:     [ Pedro García    ] Vec: [Navand.] │
│     [G] Agrupar Partida (Margen+Cuerpo)│ • Madre:     [ Catalina López  ]                │
│     [1-4] Cambiar tipo de región       │ • Padrinos:  [ Juan Sánchez y María Martín    ] │
│                                        │ • Párroco:   [ Dⁿ Joseph Ximénez (C07)        ] │
│                                        │ [✓ Validar Partida (Ctrl+Enter)] [? Duda IA]    │
├────────────────────────────────────────┴─────────────────────────────────────────────────┤
│ Barra Inferior: Folio 01608 (Partida 3 de 6) | CER estimado: 2.1% | [Exportar a Excel]   │
└──────────────────────────────────────────────────────────────────────────────────────────┘
```

### 6.3. Qué conservamos de Aletheia y qué quitamos en nuestra App en Rust
* **Quitamos el 80% de complejidad de Aletheia que no necesitamos**:
  * Fuera regiones de periódico moderno (`ChartRegion`, `ChemRegion`, `MathsRegion`, `AdvertRegion`, `MusicRegion`).
  * Fuera la jerarquía forzada de segmentar `Word` y `Glyph` (Kraken trabaja a nivel de `TextLine`).
  * Fuera los decenas de atributos de tipografía impresa moderna (fuente, tamaño en puntos, kerning, color RGB).
* **Incluimos lo que Aletheia no tiene y nos multiplica la velocidad**:
  * **Tijera de Llave Marginal (`[S]`)**: Con un solo clic o trazando una línea vertical sobre la llave `}`, parte todas las `<Baseline>` que la cruzan, recalcula sus máscaras `<Coords>` y asigna la mitad izquierda a `margen_indice` y la derecha a `cuerpo_partida`.
  * **Detector Automático de Pliegue Central (Gutter `X`)**: Separa automáticamente plana izquierda (`verso`) y plana derecha (`recto`) en microfilms a doble página.
  * **Agrupador Visual de Partida (`[G]`)**: Arrastrar desde el `margen_indice` al `cuerpo_partida` y a la `firma` dibuja un conector visual y crea el `<OrderedGroup>` en `<ReadingOrder>`.
  * **Iluminación Bidireccional Texto $\leftrightarrow$ Ficha NER**: Al hacer clic en el campo `Padre` o `Bautizado` de la ficha derecha, se ilumina en el folio la línea y palabra exacta de donde salió el dato, para que el indexador valide visualmente en 1 segundo sin teclear.
