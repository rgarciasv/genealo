# PLAN MAESTRO Y ROADMAP DE TAREAS: I+D GENEALÓGICO ALTO ALBERCHE

> **Estado del Proyecto:** Fase de Investigación y Laboratorio de Pruebas (Fases 0.5, 1 y 2).  
> **Objetivo:** Pipeline de transcripción HTR y extracción de registros sacramentales y catastrales (1594–1902, letra procesal, cortesana y humanística) hacia un grafo híbrido event-centric en **ArcadeDB**.
>
> **📚 Documentación Maestra Sincronizada (Fuente Única de Verdad):**
> - [`contexto_maestro.md`](file:///c:/TRABAJOS/personal/genealo/contexto_maestro.md) — Índice general y las 9 Reglas de Oro (`L-01` a `L-09`).
> - [`BITACORA_EXPERIMENTOS.md`](file:///c:/TRABAJOS/personal/genealo/BITACORA_EXPERIMENTOS.md) — Auditoría del cuaderno `d28c82d0` (20 turnos de chat + 2 Informes + 1 Tabla CSV) y trazabilidad de fallos cazados.
> - [`REGLAS_Y_PROMPTS_OFICIALES.md`](file:///c:/TRABAJOS/personal/genealo/REGLAS_Y_PROMPTS_OFICIALES.md) — System Prompt (`chat_configure`), Instrucciones v2.0 y Prompt de Extracción por Folio (`chat.ask`).
> - [`00_INSTRUCCIONES_PALEOGRAFICAS_V2.md`](file:///c:/TRABAJOS/personal/genealo/00_INSTRUCCIONES_PALEOGRAFICAS_V2.md) — Fuente 00 lista para subir a NotebookLM.
> - [`01_DICCIONARIO_ANCLAJE_NAVARREDONDILLA.md`](file:///c:/TRABAJOS/personal/genealo/01_DICCIONARIO_ANCLAJE_NAVARREDONDILLA.md) — Fuente 01 con candado cronológico/geográfico, tabla de curas por año y censo onomástico de los `.ged`.

---

## 🏛️ 1. FUENTES Y CORPUS DE ENTRADA (AUDITADO EN DISCO: 8.515 IMÁGENES)

Las imágenes (**8.515 archivos canónicos en disco**, ver [`GUIA_MAESTRA_ARCHIVOS_DESCARGADOS.md`](file:///c:/TRABAJOS/personal/genealo/GUIA_MAESTRA_ARCHIVOS_DESCARGADOS.md) y [`catalogo_corpus.json`](file:///c:/TRABAJOS/personal/genealo/catalogo_corpus.json)) provienen de microfilms de FamilySearch (DGS) del Archivo Diocesano de Ávila y del Archivo Histórico Provincial (AHPAv):

* **Parroquia de Navarredondilla (Sit. Arch. 166/4):**
  * `rollo 004306112` (924 imgs):
    * **Elem. 12** (1870–1987): Libro 1º Mixto — Bautismos 1º (1594–1636), Inventario de alhajas (1637) y Casados 1º (1634–1686).
    * **Elem. 13** (1988–2217): Códice Mixto ("Cajón de sastre") — Bautismos 2º/3º (1638–1701), Difuntos 1º (1631–1701), Matrimonios (1686–1697) y Padrones de Confirmación (1649 y 1681).
    * **Elem. 14** (2218–2374): Libro 3º Bautismos (1697–1749) y Visitas Pastorales (1726, 1742).
    * **Elem. 15** (2375–2605): Libro 4º Bautismos (1750–1803) y Padrones de Confirmación (1759, 1776, 1786).
    * **Elem. 16** (2606–2790): Libro 5º Bautismos (1804–1828).
  * `rollo 004306113` (1.540 imgs):
    * **Elem. 1–3** (0004–0429): Libros 6º, 7º y 8º de Bautizados (1829–1889), Padrón 1868 y Padrón de Expósitos/Nodrizas (1889).
    * **Elem. 4–5** (0430–0665): Libros 2º y 3º de Difuntos (1701–1767).
    * **Elem. 6** (0666–0800): Códice Bífido — Cara A: Difuntos 4º (1767–1802) / Cara B inversa: Casados 2º (1698–1803) + Despachos nupciales (1760–1790).
    * **Elem. 7–10** (0801–1535): Libros 5º a 8º de Difuntos (1802–1902).
* **Parroquia de San Juan del Molinillo y anejos: Navandrinal y El Villarejo (Sit. Arch. 175/1):**
  * `rollo 004298570` + Carpetas dedicadas:
    * **Elem. 14** (01599–01773): Libro 1º Bautismos Fundacional (1715–1752). *(Descarte técnico previo: 00001–01598 corresponden a Rivilla de Barajas y Salobral).*
    * **Elem. 15** (01774–02049): Libro 2º Bautismos (1752–1800, 276 imgs completas).
    * **Elem. 16** (02050–02428): Libro 3º Bautismos (1801–1852) + Padrones de Confirmación (1827 y 1850).
    * **Elem. 17–18** (02429–02658): Libro Mixto Nº 4 (1842–1850) y Libro 5º Bautismos (1851–1862).
    * **Elem. 19** (02659–02769): Índice General Alfabético de Bautismos (1750–1914).
  * `rollo 004298571` (1.560 imgs útiles: 00001–01560):
    * **Elem. 1–3** (00001–00526): Libros 1º, 2º y 3º de Matrimonios (1716–1899).
    * **Elem. 4** (00527–00553): Libro 1º de Párvulos Difuntos (1632/1644–1680).
    * **Elem. 5–10** (00554–01539): Libros 1º a 6º de Defunciones de Adultos (1715–1892).
    * **Elem. 11** (01540–01560): Índice Alfabético de Difuntos (1893–1907). *(Descarte técnico posterior: 01561–02609 corresponden a Grajos / San Juan del Olmo).*
* **Catastro del Marqués de la Ensenada (1751–1752, AHPAv):**
  * `rollo 004469028`: Libro del Personal Seglar H-669 (El Villarejo: 00901–00951, Molinillo: 00952–00979, Navandrinal: 00980–01013), Personal Navalmoral H-670 (01014–01166) y Bienes de Navandrinal H-667 (01581–02205).
  * `rollo 004469027`: Libros de Bienes H-666 de San Juan del Molinillo (01824–02363) y El Villarejo (02364–03145), y Bienes de Navalmoral (00014–01823).
  * `rollo 004469026`, `rollo 004469033`, `rollo 004273954` y carpeta `catastro ensenada Navarredondilla` (681 imgs).
* **Árboles Genealógicos Previos (Vocabulario Onomástico de Referencia — No es Ground Truth):**
  * Archivos `.ged`: `Navarredondilla_1594_1606.ged`, `Navarredondilla_1594_1616 v1.ged`, `Navarredondilla_1594_1620.ged`, `gramps.ged` y carpeta `desde geneanet arboles/` (utilidad exclusiva como n-gramas y vocabulario léxico comarcal; la validación relacional es humana e iterativa).

---

## 🎯 2. ARQUITECTURA DEL PIPELINE MEJORADA

```text
[ 1. Manifiesto de Corpus (catalogo_corpus.json) + Diccionario Onomástico (.ged / Índices) ]
               │
               ▼ (Agrupación por Unidad Documental Reconstruida + Glosario Local)
[ 2. Google NotebookLM Pro (vía MCP Nativo en Antigravity / notebooklm-py) ]
   ├── Ingesta: Cuadernos por Serie Sacramental y Periodo (<= 300 fuentes/cuaderno)
   ├── Ejecución por Micro-Lotes: Filtrado por `source_ids` (3 a 5 imágenes por consulta)
   ├── Transcripción Diplomática (Literal, grafías arcaicas, abreviaturas periciales)
   └── Extracción Ecdótica (Nombres normalizados, fechas ISO, genealogía extendida)
               │
               ▼ (JSON Estructurado [Plan A] / Data Tables CSV o Markdown [Plan B])
[ 3. Middleware Python en Antigravity ]
   ├── Extractor Regex + Validador Pydantic (ActaSacramental, MencionPersona)
   └── Generador de Transacciones Atómicas (Idempotente por id_acta)
               │
               ▼ (REST API :2480 / Cypher / SQL de ArcadeDB)
[ 4. ArcadeDB Local (Grafo Híbrido de 2 Capas: Evidencia vs. Identidad) ]
   ├── Capa 1 (Evidencia Inmutable): :DocumentoActa <--[:MENCIONADO_EN (rol, literal)]-- :MencionPersona
   ├── Capa 2 (Identidad Consolidada): :PersonaCanonica <--[:ES_LA_MISMA_PERSONA (score)]-- :MencionPersona
   └── Contexto Histórico: :Parroquia, :Lugar, :Oficio, :FincaCatastral, :DispensaMatrimonial
```

---

## 📌 AGENDA Y TAREAS PENDIENTES PARA LA PRÓXIMA SESIÓN (MAÑANA)

1. **[COMPLETADO] Estructurar y generar `catalogo_corpus.json` (`D7`):**
   - Compilado el mapa físico-lógico canónico de las **8.515 imágenes** de los 9 rollos DGS (5.223 parroquiales + 3.292 Catastro de Ensenada) en [`catalogo_corpus.json`](file:///c:/TRABAJOS/personal/genealo/catalogo_corpus.json).
   - Generada la [`GUIA_MAESTRA_ARCHIVOS_DESCARGADOS.md`](file:///c:/TRABAJOS/personal/genealo/GUIA_MAESTRA_ARCHIVOS_DESCARGADOS.md) con desglose exacto de Elementos, signaturas, años, series y partidas clave.
   - Particionamiento completo en cuadernos NotebookLM Pro respetando el límite $\le 300$ fuentes (máximo real: 277 imágenes).
   - Normalización universal de identificadores bajo Regla `[L-28]` (`{DGS}_{FOTOGRAMA}.jpg`) y tomas hermanas `[L-27]`.
2. **Prioridad Funcional del Proyecto (Decisión estratégica del usuario):**
   - Resolver si se continúa en **profundidad libro a libro** (culminar Bautismos de Navarredondilla 1594–1695, empezando por Pareja 5: 1596–1597).
   - O si se realiza una **batida transversal de censos/listas nominales** (Padrones de Confirmaciones 1649/1681, Índice de Bautismos de Molinillo 1750–1914, Catastro de Ensenada 1752) para poblar el grafo con un censo previo amplio de vecinos y familias.
3. **Codificación Geográfica (Consenso de estándar):**
   - Decidir si se mantienen exclusivamente los códigos cuatriletrados de dominio (`NRDL`, `JMOL`, `NDRN`, `VLLR`, `NMRL`, `NVTG`, `NCRZ`, `BHND`).
   - O si se añade a la ficha del lugar el código municipal oficial del INE (ej: 05164 para Navarredondilla) para cruces externos automáticos con censos y nomenclátores.
4. **Debate Metodológico sobre Criterios de Transcripción (`[ECDOTICA-01]`):**
   - Consensuar qué nivel exacto debe entregar NotebookLM en cada sección del bloque de salida:
     * **Transcripción Literal:** Fidelidad pura al trazo, sin tocar nada.
     * **Transcripción Diplomática / Semidiplomática:** Desarrollo de abreviaturas con corchetes `[ ]`, separación de palabras soldadas (*destayglesia* $\rightarrow$ *de esta yglesia*), respeto a grafías antiguas (`u/v`, `b/v`, `i/j/y`, consonantes dobles).
     * **Transcripción Crítica / Ecdótica Normalizada:** Forma moderna para indexación onomástica y motores de búsqueda.
5. **Protocolo de Verificación Humana y Calibración de NotebookLM (`[VAL-01]`):**
   - Diseñar el método de inspección y muestreo manual del usuario para evaluar el grado de aproximación a la realidad documental (asumiendo con realismo que nunca se alcanzará el 100 %).
   - Establecer ciclos de iteración empírica sobre los prompts y micro-lotes de NotebookLM para minimizar errores y exprimir su potencial.
6. **Extracción de URLs ARK de FamilySearch (`[ARK-01]`):**
   - El usuario ejecutará [`extraer_arks_familysearch.js`](file:///c:/TRABAJOS/personal/genealo/extraer_arks_familysearch.js) en la consola DevTools de FamilySearch para volcar el mapa de enlaces permanentes ARK.
7. **Catalogación de Fondos Parroquiales de Navalmoral de la Sierra (`[NMRL-01]`):**
   - Identificar y registrar en el catálogo los números de microfilm/DGS de Navalmoral de la Sierra en FamilySearch para cubrir la ascendencia pre-1715 de San Juan del Molinillo, Navandrinal y El Villarejo.
8. **Evaluación y Aprovechamiento de Chats Externos (`desde gemini/`) [DEBATE METODOLÓGICO PENDIENTE]:**
   - *Fuentes:* [`desde gemini/Extracción de Corpus Paleográficos Parroquiales.md`](file:///c:/TRABAJOS/personal/genealo/desde%20gemini/Extracci%C3%B3n%20de%20Corpus%20Paleogr%C3%A1ficos%20Parroquiales.md) y [`desde gemini/Gemini Pro para Paleografía Parroquial.md`](file:///c:/TRABAJOS/personal/genealo/desde%20gemini/Gemini%20Pro%20para%20Paleograf%C3%ADa%20Parroquial.md).
   - Analizar en su momento con el usuario qué ideas se integran al pipeline oficial y cuáles se descartan:
     * **Viabilidad de Alfabetogramas Reales:** Estudio de viabilidad y coste/beneficio de recortar caracteres reales con cajas delimitadoras (*bounding boxes*) de cada escribiente para soporte visual HTR frente al modelo actual de fichas técnicas en [`03_AUTORIDADES`](file:///c:/TRABAJOS/personal/genealo/03_AUTORIDADES_PALEOGRAFICAS_ALTO_ALBERCHE.md).
     * **Mitigación del Sesgo de Expectativa:** Pautas para evitar que el modelo complete patronímicos comunes por probabilidad lingüística en lugar de atender a los trazos reales en procesales encadenadas complejas (lección de Fray Jacinto de Alcocer en 1611).
     * **Cruce Sistemático Marginalia vs. Cuerpo Central:** Protocolo para contrastar automáticamente los nombres del margen con el texto de la partida para asignar niveles de fiabilidad o generar alertas de conflicto.
     * **Índices de Certeza / Cola de Auditoría Humana:** Evaluar la conveniencia de pedir a NotebookLM el etiquetado explícito de certeza (`[ALTA_CERTEZA]` / `[BAJA_CERTEZA]`) para dirigir la revisión visual del usuario sólo a los asientos dudosos.

---

## 📋 3. DESGLOSE DE FASES Y TAREAS

### 🟢 FASE 0: Catalogación Programática y Entorno Local
- [x] Instalación de ArcadeDB 26.10.2 nativo en Windows (GraalVM, ~110 MB RAM, sin Docker).
- [x] Configuración del plugin MCP nativo (`notebooklm` y base de datos) en Antigravity (`mcp_config.json`).
- [x] Documento de contexto inicial consolidado (`contexto_maestro.md`).
- [x] Auditoría documental de los 3 inventarios maestros en PDF (Navarredondilla, Molinillo y Ensenada).
- [x] **0.1. Generación de `catalogo_corpus.json` (Mapa Físico-Lógico Completo):**
  - [x] Compilado `catalogo_corpus.json` v1.1 con las 8.515 imágenes mapeadas campo a campo (`id_imagen` bajo `[L-28]`, `rollo_dgs`, `fotograma_numero`, `elemento_numero`, `parroquia_codigo`, `fondo`, `tipo_documento`, `libro_numero`, `signatura_archivo`, `anios_macro`, `descripcion_elemento`, `cuaderno_asignado_id`, `estado_auditoria`, `toma_hermana_de`, `tipo_toma`, `es_descarte`, `notas_paleograficas`, `url_ark`).
  - [x] Resueltos y documentados los saltos de encuadernación del *Elemento 13 ("Cajón de sastre")*, *Elemento 6 ("Libro Bífido")*, *Elemento 4 (Párvulos Molinillo)* y las 625 imágenes de Bienes de Navandrinal erróneamente rotuladas como Navalosa.
  - [ ] **[ARK-01] [TAREA USUARIO] Extracción de URLs ARK de FamilySearch:**
    - [ ] Ejecutar script en consola DevTools de FamilySearch para volcar mapa `archivo_imagen.jpg -> URL ARK`.
    - [ ] Integrar captura automática de ARK en `descargar_v2.js` para nuevas descargas de rollos.
- [x] **0.2. Extracción del Diccionario Onomástico y Toponímico (Bootstrapping):**
  - [x] Extraer de los archivos `.ged` (`Navarredondilla_1594_1620.ged`, `gramps.ged`) la lista de apellidos, nombres, oficios, matrimonios y notas paleográficas reales de la comarca.
  - [x] Generar el archivo [`01_DICCIONARIO_ANCLAJE_NAVARREDONDILLA.md`](file:///c:/TRABAJOS/personal/genealo/01_DICCIONARIO_ANCLAJE_NAVARREDONDILLA.md) con el candado cronológico, topónimos de mundo cerrado y tabla de curas por año para subirlo como **Fuente de Anclaje 01** en NotebookLM.
  - [x] **Censo Prosopográfico Exhaustivo y Mapa de Escribanos (1594–1695, 101 años):** Culminada la extracción de los 4 lotes de Bautismos (Libros 1º y 2º) y unificados los 35 clérigos con su red de licencias, movilidad comarcal (`JMOL`, `NMRL`, `NVLG`, `BHND`), ductus, tics y asignación fotograma a fotograma en [`03_AUTORIDADES_PALEOGRAFICAS_ALTO_ALBERCHE.md`](file:///c:/TRABAJOS/personal/genealo/03_AUTORIDADES_PALEOGRAFICAS_ALTO_ALBERCHE.md).

---

### 🗂️ FASE 0.5: Estrategia de Particionado y Cuadernos en NotebookLM Pro
*Objetivo: Organizar los 8.515 archivos respetando el límite de 300 fuentes por cuaderno (máximo real actual: 277) y separando por fondo, pueblo y serie.*

- [ ] **Definición de la Estructura de Cuadernos y Codificación Canónica:**
  - [x] `[NRDL-BAUT-04] Navarredondilla - Bautismos Libro 1º y 2º (1594–1695)` (ID: `7967d647-8ca2-4863-a576-11843e8e8802`, 188 fuentes: 183 imágenes + fuentes maestras `00`, `01`, `02`, `03`, `04`). **En explotación activa y preservación inmutable.**
  - [x] **[CATASTRO-1752-LEGOS] Cuadernos de Personal de Legos del Catastro de Ensenada (200/200 fuentes READY, Dictamen VICTORY CONFIRMED):**
    - [x] `NRDL-ENSENADA-LEGOS-01` (ID: `ec86de71-a11c-4489-bbb9-eea856cccac4`, 87 fuentes).
    - [x] `JMOL-ENSENADA-LEGOS-01` (ID: `407d5cb4-4b83-495f-a23a-309ea44ee8c6`, 28 fuentes).
    - [x] `VLLR-ENSENADA-LEGOS-01` (ID: `e7fba70b-af7d-4602-b543-060742b22528`, 51 fuentes).
    - [x] `NDRN-ENSENADA-LEGOS-01` (ID: `cd72ef58-fcf5-48ac-8de2-556648ebd90e`, 34 fuentes).
  - [ ] `[SERIE-PARROQUIAL] Cuadernos Parroquiales de los 4 Pueblos (Bautismos, Matrimonios y Defunciones restantes):`
    - [x] `NRDL-MATR-01` (ID: `1e6fec74-1e2f-4dd7-8ad1-6d25411de127`, 33 fuentes en estado `READY`, Dictamen VICTORY CONFIRMED).
    - [ ] `NRDL-BAUT-01..03, 05..07` (Navarredondilla Bautismos restantes: 6 cuadernos, 1.063 imgs).
    - [ ] `NRDL-MATR-02` y `NRDL-MIXTO-01` (Navarredondilla Matrimonios restantes: 2 cuadernos, 140 imgs).
    - [ ] `NRDL-DIFU-01..05, 01B` (Navarredondilla Defunciones: 6 cuadernos, 1.041 imgs).
    - [ ] `JMOL-BAUT-01..05` y `JMOL-INDICE-BAUT` (San Juan del Molinillo Bautismos).
    - [ ] `JMOL-MATR-01..03` y `JMOL-MIXTO-04` (San Juan del Molinillo Matrimonios).
    - [ ] `JMOL-DIFU-01..06`, `JMOL-DIFU-PARVULOS` y `JMOL-INDICE-DIFU` (San Juan del Molinillo Defunciones).
    - [ ] `ALTO-ALBERCHE-ANEXOS-01` (Muestras de anejos).
  - [ ] `[CATASTRO-1752-BIENES-Y-ECLESIASTICO] Ensenada - Bienes de Legos y Rentas Eclesiásticas (Pospuesto a fase posterior)`.

---

### 🔬 FASE 1: Laboratorio de Prompt Engineering en NotebookLM Pro
*Objetivo: Lograr transcripción y extracción con fidelidad pericial sin omisiones ni resúmenes.*

- [x] **1.0. Auditoría Forense del Cuaderno Experimental `d28c82d0-e15f-4d4d-8333-61f529d52815`:**
  - [x] Descarga y análisis de los 20 turnos del chat, los 2 Informes de Studio y la Tabla CSV de 484 filas.
  - [x] Identificación y documentación de las 9 Lecciones Empíricas (`L-01` a `L-09`) en [`BITACORA_EXPERIMENTOS.md`](file:///c:/TRABAJOS/personal/genealo/BITACORA_EXPERIMENTOS.md).
- [ ] **1.1. Selección del Corpus de Calibración y Validación Humana:**
  - [ ] Nivel 1 (Baja - Letra humanística/redondilla s. XVIII): 1 folio de Bautismos de San Juan del Molinillo (1752–1800, ej. `004298570_01903.jpg` donde constan abuelos paternos y maternos).
  - [ ] Nivel 2 (Media - Cortesana evolucionada s. XVII): 1 folio de Bautismos o Matrimonios de Navarredondilla (1638–1685).
  - [ ] Nivel 3 (Alta - Procesal encadenada s. XVI): 1 folio del Libro 1º Fundacional de Navarredondilla (1594–1620, ej. `004306112_01873.jpg`). *Nota:* los archivos `.ged` no son verdad de referencia para relaciones familiares; actúan como vocabulario onomástico/n-gramas, y la validación final es humana iterativa.
  - [ ] Nivel 4 (Tabular/Lista): 1 folio del Padrón de Confirmaciones de 1649 o del Personal de Ensenada (H-669).
- [x] **1.2. Diseño de la Directiva Paleográfica Dual v2.0 (System Prompt + Fuentes 00 y 01):**
  - [x] **System Prompt (`chat_configure`)** + [`00_INSTRUCCIONES_PALEOGRAFICAS_V2.md`](file:///c:/TRABAJOS/personal/genealo/00_INSTRUCCIONES_PALEOGRAFICAS_V2.md) + [`REGLAS_Y_PROMPTS_OFICIALES.md`](file:///c:/TRABAJOS/personal/genealo/REGLAS_Y_PROMPTS_OFICIALES.md) blindados contra sesgo de confirmación (`L-01`), contaminación de ejemplos (`L-02`), alucinación de fechas/topónimos (`L-05`) y deformación de curas (`L-06`).
  - [x] Inyección de `00_INSTRUCCIONES_PALEOGRAFICAS_V2`, `01_DICCIONARIO_ANCLAJE_NAVARREDONDILLA` y `02_INSTRUCCIONES_CRONOLOGICAS` en `Lib. Baut. Navarre Vol. 1 (1594-1695)` (`7967d647-8ca2-4863-a576-11843e8e8802`).
- [x] **1.3. Protocolo de Consulta por Micro-Lotes (`source_ids`) — Prueba Piloto en Vivo:**
  - [x] Prueba piloto completada en `004306112_01873.jpg` (Folio 1r, 1594). 6 partidas extraídas de arriba a abajo en Formato de Bloque Estricto con control de roturas (`[ROTO]`), candado de fechas ISO y asignación exacta de escribanos (Alonso del Valle y Francisco Ximénez). Guardado en [`transcripciones/004306112_01873.md`](file:///c:/TRABAJOS/personal/genealo/transcripciones/004306112_01873.md).
  - [x] Segunda prueba piloto completada en `004306112_01874.jpg` (Folios 1v y 2r, 1594–1595). 13 partidas extraídas en plana doble, validación de partidas cortadas al pie, apodos (`chopo`), patronímicos compuestos y rescate de clérigo beneficiado Don Rodrigo Antonio de Meneses. Guardado en [`transcripciones/004306112_01874.md`](file:///c:/TRABAJOS/personal/genealo/transcripciones/004306112_01874.md).
  - [x] Tercera prueba piloto (letra procesal encadenada extrema de Joan Martínez) completada en `004306112_01879.jpg` (Año 1596). 11 partidas extraídas íntegramente, desciframiento de *scriptio continua*, detección de óbito infantil (`+ lucas`) y rescate del cura propio Pedro de la Llana. Guardado en [`transcripciones/004306112_01879.md`](file:///c:/TRABAJOS/personal/genealo/transcripciones/004306112_01879.md).
  - [x] Cuarta prueba piloto (mano de Alonso Hernández y desbloqueo de `L-01`) completada en `004306112_01895.jpg` (Año 1604). 14 partidas extraídas íntegramente (6 en verso, 8 en recto). Lectura impecable de **Diego de Encabo** (1-mayo-1604: `v. diego`), desmantelando definitivamente el sesgo antiguo. Guardado en [`transcripciones/004306112_01895.md`](file:///c:/TRABAJOS/personal/genealo/transcripciones/004306112_01895.md). Total acumulado: **44 actas sacramentales**.
- [x] **1.4. Banco de Pruebas de Fusión de "Tomas Hermanas" (L-20 en las 10 primeras imágenes, 1594–1597):**
  - [x] Mapeo de las 5 parejas de tomas dobles de FamilySearch (`01872/01873`, `01874/01875`, `01876/01877`, `01878/01879`, `01880/01881`).
  - [x] Prueba de fusión completada en **Pareja 1 (`004306112_01872.jpg` + `004306112_01873.jpg`)**: Cotejo forense del Folio 1r (1594). Confirmada la ausencia de portada previa, identificadas placas técnicas de microfilmación ("Volumen Entero" / "Página Rota") y verificada la fractura física idéntica en ambas tomas con cero duplicados.
  - [x] Prueba de fusión completada en **Pareja 2 (`004306112_01874.jpg` + `004306112_01875.jpg`)**: 13 asientos extraídos en Folios 1v y 2r (1594–1595), con rescate íntegro al pie de página de los padrinos, testigos y firmas de Don Rodrigo Antonio de Meneses y de Francisco Ximénez. Guardado en [`transcripciones/004306112_01874_01875.md`](file:///c:/TRABAJOS/personal/genealo/transcripciones/004306112_01874_01875.md).
  - [x] Prueba de fusión completada en **Pareja 3 (`004306112_01876.jpg` + `004306112_01877.jpg`)**: 12 asientos extraídos en Folios 2v y 3r (1595), resolución perfecta de la costura apretada en el lomo (*gutter shadow*), cero duplicados y rescate de Fray Francisco de Oropesa. Guardado en [`transcripciones/004306112_01876_01877.md`](file:///c:/TRABAJOS/personal/genealo/transcripciones/004306112_01876_01877.md). Total acumulado en pruebas: **56 actas sacramentales**.
  - [x] Prueba de fusión completada en **Pareja 4 (`004306112_01878.jpg` + `004306112_01879.jpg`)**: 11 asientos extraídos en Folios 3v y 4r (1596), aislamiento de *bleed-through* parásito, desambiguación de trazos de tinta del reverso y confirmación forense de *omissio scribae* en el último asiento. Guardado en [`transcripciones/004306112_01878_01879.md`](file:///c:/TRABAJOS/personal/genealo/transcripciones/004306112_01878_01879.md).
  - [x] Validación del mecanismo de reautenticación desatendida de NotebookLM MCP vía perfil persistente de Chromium (`L-21`).
- [ ] **1.5. [VAL-01] [TAREA USUARIO] Protocolo de Verificación Humana y Calibración de NotebookLM:**
  - [ ] Muestreo e inspección manual directa por el usuario sobre un conjunto acotado de folios para medir el porcentaje real de acierto y tipología de errores (asumiendo de forma realista que nunca se alcanzará el 100%).
  - [ ] Ciclos de iteración empírica sobre los prompts y micro-lotes para exprimir al máximo las capacidades de visión multimodal de NotebookLM y minimizar fallos.
- [ ] **1.6. [ECDOTICA-01] [METODOLOGÍA PALEOGRÁFICA] Debate y Consenso de Criterios de Transcripción:**
  - [ ] Sesión de definición metodológica con el usuario para clarificar las fronteras entre:
    * **Transcripción Literal Estricta:** Grafías puras, abreviaturas sin desarrollar, respeto absoluto a la disposición física.
    * **Transcripción Diplomática vs. Semidiplomática:** Tratamiento de letras dobles, `u/v`, `b/v`, `i/j/y`, separación de palabras unidas (*scriptio continua* tipo `destayglesia`) y desarrollo de abreviaturas con corchetes `[ ]`.
    * **Transcripción Crítica / Ecdótica Normalizada:** Forma moderna estándar para motores de búsqueda, n-gramas y grafos genealógicos.
  - [ ] Consensuar el contrato exacto de salida para que NotebookLM devuelva el equilibrio idóneo entre fidelidad paleográfica e indexación.

---

### 📦 FASE 2: Especificación y Contratos de Salida
*Objetivo: Blindar la estructura de datos para soportar la riqueza documental sacramental y polimórfica.*

- [x] **2.1. Modelo de Identificación en Dos Capas (Soporte Físico Inmutable + Entidad Acta Desacoplada + ARK) (`L-26`):**
  - [x] Soporte Físico Inmutable: Archivo JPG / Fotograma `{DGS}_{FOTOGRAMA}` (ej. `004306112_01874`). Coincidencia 1:1 con el fichero en disco, con FamilySearch y con la URL ARK persistente. No se fuerza división física en L/R.
  - [x] Entidad Acta Desacoplada del Orden: Cada acta posee identificador único propio (UUID / ID interno) y propiedades descriptivas de ubicación (`lado: izquierda/derecha`, `orden_en_imagen: 1, 2...`). Elimina el efecto dominó en base de datos si la IA omite un asiento, fusiona dos partidas indebidamente o divide una nota marginal.
  - [x] Desglose de Roles Eclesiásticos (`L-27`): Diferenciación formal en los contratos de extracción entre `redactor_material` (mano caligráfica que empuña la pluma y fija el ductus), `oficiante_sacramental` (quien administra el sacramento canónico) y `firmas` (suscripción y rúbrica al pie).
  - [x] Atributos descriptivos revisables: `folio_manuscrito`, `folio_moderno`, `id_archivistico` (`ES-AV-{LOCALIDAD}-{SERIE}-{VOL}-{FOL_CARA}-{ASIENTO}`).
  - [x] Metadato digital persistente: `url_ark` (FamilySearch ARK URL) a nivel de soporte e imagen.
  - [x] Trazabilidad y protocolos de partidas bipartitas (Intra-imagen verso $\rightarrow$ recto unificada; e Inter-imagen recto $N \rightarrow$ verso $N+1$ con enlace direccional).
- [ ] **2.2. Validación empírica de Contratos Polimórficos (`L-23`):**
  - [ ] Formato de Padrones de Confirmación (`PADRON_CONFIRMACION`) probado en Padrón de 1649 (`02067`–`02070`).
  - [ ] Formato de Autos de Visita Pastoral (`AUTO_VISITA`) probado en Visita de 1638 (`02052`).
  - [ ] Formato de Índices Parroquiales (`INDICE_PARROQUIAL`).
  - [ ] Formato de Minutas y Borradores de Sacristía (`MINUTA_SACRISTIA`).
- [ ] **2.3. Serialización JSON / Pydantic (Plan A) y Contingencia Markdown (Plan B):**
  - [ ] Modelos Pydantic en Python mapeados 1:1 con los contratos de bloque.

---

### 🐍 FASE 3: Middleware de Python y Automatización (MCP + `notebooklm-py`)
*Objetivo: Orquestar lotes masivos de transcripción, validar la integridad y permitir reanudación sin pérdida.*

- [ ] **3.1. Orquestador de Lotes con Checkpoint (`transcriptor_batch.py`):**
  - [ ] Script Python que recorra las imágenes del cuaderno con checkpoint local en JSON.
  - [ ] Detección y fusión automática de tomas hermanas (usando el mapa de parejas dobles).
  - [ ] Manejo de actas cortadas entre dos fotogramas consecutivos (unión de ventana deslizante).
- [ ] **3.2. Sanitizador y Validador Pydantic:**
  - [ ] Extractor Regex de bloques Markdown y reparador de texto antiguo.
  - [ ] Modelos Pydantic estrictos (`ActaSacramental`, `PadronConfirmacion`, `AutoVisita`, `MinutaSacristia`).

---

### 🕸️ FASE 4: Modelo de Datos de 2 Capas e Ingesta en ArcadeDB
*Objetivo: Separar la evidencia documental inmutable de la reconstrucción genealógica probabilística.*

- [ ] **4.1. Esquema Híbrido en ArcadeDB (Grafo + Documental):**
  - [ ] **Capa 1 — Evidencia Documental (Inmutable):**
    - `CREATE VERTEX TYPE Acta` (`id_acta`, `rollo_dgs`, `imagen_archivo`, `folio_fisico`, `localidad`, `tipo_sacramento`, `fecha_iso`, `transcripcion_diplomatica`, `texto_ecdotico`).
    - `CREATE VERTEX TYPE MencionPersona` (`id_mencion`, `nombre_literal`, `nombre_normalizado`, `apellido1_normalizado`, `apellido2_normalizado`, `sexo`, `vecindad`, `oficio`, `estado_civil`).
    - `CREATE VERTEX TYPE SoporteFisico` (`id_soporte`, `rollo_dgs`, `fotograma`, `archivo_jpg`, `url_ark`, `toma_hermana_de`).
    - `CREATE EDGE TYPE PARTICIPA_EN` (de `MencionPersona` a `Acta` con propiedades: `rol` [`BAUTIZADO`, `PADRE`, `MADRE`, `ABUELO_P`, `ABUELO_M`, `PADRINO`, `MADRINA`, `TESTIGO`], `confianza_lectura`).
    - `CREATE EDGE TYPE OFICIA_SACRAMENTO` (de `MencionPersona` a `Acta` con propiedades: `cargo`, `parroquia_origen`, `licencia_abacial`).
    - `CREATE EDGE TYPE ESCRIBE` (de `MencionPersona` a `SoporteFisico` / `Acta` con propiedades: `ductus_caligrafico`, `confianza_mano`, `es_autografo`).
    - `CREATE EDGE TYPE FIRMA` (de `MencionPersona` a `Acta` con propiedades: `tipo_suscripcion` [`AUTOGRAFA`, `RUBRICA_SOLA`, `SIGNO_NOTARIAL`, `NO_FIRMA`]).
    - `CREATE EDGE TYPE RELACION_DECLARADA` (entre dos `MencionPersona` dentro de la misma acta: `PADRE_DE`, `CONYUGE_DE`, `VIUDO_DE`).
  - [ ] **Capa 2 — Identidad Consolidada (Reconstrucción Genealógica):**
    - `CREATE VERTEX TYPE PersonaCanonica` (`id_persona`, `nombre_canonico`, `apellidos_canonicos`, `anio_nacimiento_est`, `anio_defuncion_est`).
    - `CREATE EDGE TYPE CORRESPONDE_A` (de `MencionPersona` a `PersonaCanonica` con `score_similitud`, `metodo_resolucion` [`REGLA_DETERMINISTA`, `GEDCOM_MATCH`, `HUMANO`]).
  - [ ] **Nodos de Contexto:**
    - `Lugar` / `Parroquia` / `FincaCatastral` (para enlazar el Catastro de Ensenada H-666/H-667 con el Libro del Personal H-669).
- [ ] **4.2. Inyector Transaccional en Python:**
  - [ ] Carga idempotente vía REST API (`http://localhost:2480/api/v1/command`) para no duplicar actas si se re-procesa un folio.

---

### 🔍 FASE 5: Deduplicación, Cruce Multisource y Analítica de Redes
*Objetivo: Reconstruir las familias del Alto Alberche (1594–1900) y cruzarlas con el Catastro y los GEDCOM.*

- [ ] **5.1. Motor de Resolución de Identidades (Entity Resolution):**
  - [ ] Enlace por **Tríada Familiar** (Padres + Abuelos): en las partidas del s. XVIII que incluyen a los 4 abuelos, enlazar automáticamente a los hermanos y cruzar con la partida de matrimonio de los padres.
  - [ ] Enlace con `Navarredondilla_1594_1620.ged` y `gramps.ged` como semilla de validación para el siglo XVI–XVII.
- [ ] **5.2. Integración del Catastro de Ensenada (1751–1752):**
  - [ ] Vincular cada cabeza de familia del Libro del Personal (`H-669`, rollo `004469028`) con sus bautismos/matrimonios en San Juan del Molinillo, Navandrinal y El Villarejo, y con su declaración de tierras y ganado en los Libros de Bienes (`H-666` y `H-667`).
- [ ] **5.3. Consultas Cypher y Visualización en ArcadeDB Studio:**
  - [ ] Consultas de árboles de ascendencia/descendencia, detección de consanguinidad/endogamia y redes de padrinazgo entre las tres aldeas y Navarredondilla.

---

## 📌 PRÓXIMOS PASOS OPERATIVOS INMEDIATOS
1. **Ejecutar la Pareja 5 de Tomas Hermanas (`004306112_01880.jpg` + `004306112_01881.jpg`)**: Cerrar la validación pericial de las 10 primeras imágenes dobles (1594–1597).
2. **Desarrollar el script `transcriptor_batch.py` (Fase 3)**: Automatizar la extracción secuencial del resto del cuaderno (`01882.jpg` en adelante) con checkpoint y guardado automático en `transcripciones/`.
