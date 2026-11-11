# CONTEXTO MAESTRO: PROYECTO DE I+D GENEALÓGICO ALTO ALBERCHE

> **FUENTE ÚNICA DE VERDAD (ÍNDICE DOCUMENTAL DEL PROYECTO):**
> Para evitar dispersión de reglas entre conversaciones, todo el conocimiento del proyecto está centralizado en estos 7 archivos maestros en `c:\TRABAJOS\personal\genealo\`:
> 1. [`contexto_maestro.md`](file:///c:/TRABAJOS/personal/genealo/contexto_maestro.md) *(Este documento)*: Visión general, arquitectura y reglas de oro del sistema.
> 2. [`TODO.md`](file:///c:/TRABAJOS/personal/genealo/TODO.md): Inventario completo auditado de los **8.515 archivos canónicos** de imagen (rollos DGS) y estado de avance por fases.
> 3. [`GUIA_MAESTRA_ARCHIVOS_DESCARGADOS.md`](file:///c:/TRABAJOS/personal/genealo/GUIA_MAESTRA_ARCHIVOS_DESCARGADOS.md): Guía canónica de desglose por Elementos, fondos, signaturas AHPAv/Diocesanas, libros, series y años (1751-1752 y 1594-1902).
> 4. [`INVENTARIO_DESCARGAS_Y_ANOMALIAS_DOCUMENTALES.md`](file:///c:/TRABAJOS/personal/genealo/INVENTARIO_DESCARGAS_Y_ANOMALIAS_DOCUMENTALES.md): Inventario exhaustivo de descargas y catálogo sistemático de anomalías históricas (padrones de confirmación, visitas pastorales, inventarios de alhajas, códices bífidos, pliegos invertidos, expósitos, epidemias y descartes técnicos).
> 5. [`catalogo_corpus.json`](file:///c:/TRABAJOS/personal/genealo/catalogo_corpus.json): Mapa físico-lógico estructurado en JSON de las 8.515 imágenes con metadatos completos y particionado NotebookLM ($\le 300$ imgs).
> 6. [`BITACORA_EXPERIMENTOS.md`](file:///c:/TRABAJOS/personal/genealo/BITACORA_EXPERIMENTOS.md): Registro histórico de todas las pruebas hechas en NotebookLM, los fallos cazados (`L-01` a `L-29`) y qué regla soluciona cada fallo.
> 7. [`REGLAS_Y_PROMPTS_OFICIALES.md`](file:///c:/TRABAJOS/personal/genealo/REGLAS_Y_PROMPTS_OFICIALES.md): Versión oficial vigente (`v2.0`) del System Prompt (`chat_configure`), instrucciones paleográficas (`00_INSTRUCCIONES_PALEOGRAFICAS_V2.md`), Prompt de Extracción por Folio (`chat.ask`), formatos polimórficos (`PADRON_CONFIRMACION`, `AUTO_VISITA`, `INDICE_PARROQUIAL`, `MINUTA_SACRISTIA`) e ID canónico universal.
> 8. [`01_DICCIONARIO_ANCLAJE_NAVARREDONDILLA.md`](file:///c:/TRABAJOS/personal/genealo/01_DICCIONARIO_ANCLAJE_NAVARREDONDILLA.md): Candado cronológico (con todos los saltos de encuadernación), diccionario de lugares de mundo cerrado y vocabulario onomástico local (nombres, apellidos, apodos y fórmulas vecinales).
> 9. [`03_AUTORIDADES_PALEOGRAFICAS_ALTO_ALBERCHE.md`](file:///c:/TRABAJOS/personal/genealo/03_AUTORIDADES_PALEOGRAFICAS_ALTO_ALBERCHE.md): Banco transversal de escribanos, ductus, abreviaturas, tics de redacción y firmas autógrafas (1594–1683).
> 10. [`04_JURISDICCIONES_Y_DEPENDENCIAS_PARROQUIALES.md`](file:///c:/TRABAJOS/personal/genealo/04_JURISDICCIONES_Y_DEPENDENCIAS_PARROQUIALES.md): Códigos cuatriletrados unívocos, dependencia de Molinillo respecto a Navalmoral pre-1715, arranque de series, lagunas y libros bífidos/paralelos.
> 11. Carpeta [`desde gemini/`](file:///c:/TRABAJOS/personal/genealo/desde%20gemini/): Material en bruto exportado de sesiones con Gemini (alfabetogramas reales, sesgo de expectativa, cruce marginalia/cuerpo), registrado en `TODO.md` (punto 8) como debate pendiente para análisis y aprovechamiento selectivo.

---

## 1. OBJETIVO DEL SISTEMA
Pipeline de reconocimiento de texto manuscrito (HTR paleográfico asistido por **NotebookLM Pro**) y extracción genealógica para los fondos parroquiales y catastrales del **Alto Alberche (Diócesis de Ávila, 1594–1902)**: **Navarredondilla**, **San Juan del Molinillo**, **Navandrinal**, **El Villarejo** y **Navalmoral de la Sierra**, con validación humana iterativa e inyección de los datos en un grafo híbrido de 2 capas en **ArcadeDB 26.10.2** local (`http://localhost:2480`). *(Decisión de proyecto ratificada: descarte formal de la API de Gemini; foco en optimización de micro-lotes, modularización de prompts y control de calidad empírico en NotebookLM).*

---

## 2. REGLA SUPREMA DE DOCUMENTACIÓN CONTINUA Y REGLAS DE ORO CONSOLIDADAS (`v2.0`)

> ### 🛑 PROTOCOLO DE DOCUMENTACIÓN CONTINUA (OBLIGATORIO EN CADA PASO):
> Para que nunca más se nos quede información dispersa en el historial del chat, existe la **obligación estricta de mantener actualizada en tiempo real nuestra Fuente Única de Verdad en `c:\TRABAJOS\personal\genealo\`** cada vez que hagamos una prueba, descubramos algo nuevo o ajustemos un prompt:
> 
> 1. **[`BITACORA_EXPERIMENTOS.md`](file:///c:/TRABAJOS/personal/genealo/BITACORA_EXPERIMENTOS.md):**
>    - Cada vez que lancemos una prueba en NotebookLM (ya sea en el chat o en Studio), debes registrar inmediatamente una fila o entrada nueva con: **Fecha, Cuaderno e imágenes probadas, Prompt exacto utilizado, Resultado obtenido (aciertos y fallos detectados) y Código de Lección aprendida (`L-16`, `L-17`, etc.)**.
> 2. **[`REGLAS_Y_PROMPTS_OFICIALES.md`](file:///c:/TRABAJOS/personal/genealo/REGLAS_Y_PROMPTS_OFICIALES.md) y [`00_INSTRUCCIONES_PALEOGRAFICAS_V2.md`](file:///c:/TRABAJOS/personal/genealo/00_INSTRUCCIONES_PALEOGRAFICAS_V2.md):**
>    - Ningún ajuste de prompt se hace "de palabra" solo en el chat: si modificamos una regla o mejoramos un prompt tras ver el resultado de una prueba, **primero actualizas el archivo oficial en disco (y en la fuente `00` del cuaderno en NotebookLM) indicando qué lección `[L-XX]` lo motiva**.
> 3. **[`01_DICCIONARIO_ANCLAJE_NAVARREDONDILLA.md`](file:///c:/TRABAJOS/personal/genealo/01_DICCIONARIO_ANCLAJE_NAVARREDONDILLA.md):**
>    - Cada vez que durante las pruebas identifiquemos una nueva variante diplomática de un nombre, apellido o lugar, un nuevo tic/abreviatura de un escribano, o una anomalía física en un fotograma concreto, **debes añadirlo inmediatamente a su sección correspondiente de este diccionario (y actualizar la fuente `01` en NotebookLM)**.
> 4. **[`contexto_maestro.md`](file:///c:/TRABAJOS/personal/genealo/contexto_maestro.md) y [`TODO.md`](file:///c:/TRABAJOS/personal/genealo/TODO.md):**
>    - Cada vez que cerremos una tarea (como borrar un duplicado, actualizar las fuentes de un cuaderno o validar un lote de páginas), **marca el avance en `TODO.md` y actualiza el estado en `contexto_maestro.md`**.
> 
> **No des nunca una prueba o descubrimiento por terminado hasta haber guardado el cambio en el archivo `.md` correspondiente de `c:\TRABAJOS\personal\genealo\`.**

### Las Reglas de Oro Técnicas:
Tras auditar el cuaderno experimental `d28c82d0-e15f-4d4d-8333-61f529d52815` (20 turnos de chat + 2 Informes Studio + 1 Data Table CSV de 484 filas), el sistema aplica de forma obligatoria:

1. **`[L-01]` Prohibición de preguntas dirigidas a un nombre ("Busca a X"):** Nunca se pide buscar a un individuo durante la transcripción de un folio (evita el sesgo de confirmación que hizo leer *Domingo* donde ponía *Diego* en `S3HT-DTLS-HXS.jpg`).
2. **`[L-02]` Cero ejemplos con nombres reales en el archivo de instrucciones:** Los ejemplos de formato en [`00_INSTRUCCIONES_PALEOGRAFICAS_V2.md`](file:///c:/TRABAJOS/personal/genealo/00_INSTRUCCIONES_PALEOGRAFICAS_V2.md) usan placeholders abstractos (`[contrayente_varón]`), evitando que el modelo inyecte el ejemplo como una partida falsa (como ocurrió en la `Img 87` de 1634).
3. **`[L-03]` Prohibido usar *Studio Reports* sobre un libro entero para transcribir:** El botón de Informes de Studio tiene un límite duro de ~10.000 tokens de salida y se saltó 57 de las 89 imágenes (64%), además de perder resolución visual en la `Img 31`.
4. **`[L-04]` Extracción mediante `chat.ask` filtrando `source_ids` (1 a 2 imágenes por llamada):** Cada llamada pasa únicamente `[id_fuente_00, id_fuente_01, id_imagen_actual]`, obligando a Gemini a dedicar el 100% de sus tokens visuales de alta resolución a ese folio y manteniendo la trazabilidad exacta al archivo `.jpg`.
5. **`[L-05]` Candado Cronológico y Geográfico de Mundo Cerrado:** Impide leer años fuera del rango del libro (evita confundir *noventa* [1597] con *sesenta* [1567] o *cincuenta* [1553]) y prohíbe alucinar topónimos ajenos (*Benavides, Seseña, Valdemoro*).
6. **`[L-06]` Tabla de Autoridades de Sacerdotes por Año:** Evita deformaciones de firmas sacerdotales (*Alonso Hernández*, *Baltasar de Luján*, *Gaspar Rubiano*, *Miguel Baguer*, *Pedro Sánchez de Luna*, *Antonio de Prado*, *Juan de la Hija*).
7. **`[L-07]` Declaración obligatoria de `Nivel de Certeza y Dudas Paleográficas`:** Cuando un trazo es ambiguo, el modelo tiene prohibido adivinar en silencio y debe reportar `[DUDOSO: opción_1 / opción_2]`.
8. **`[L-08]` Uso exclusivo de archivos con numeración secuencial DGS (`004306112_01870.jpg`):** Garantiza que el orden alfabético en NotebookLM coincida al 100% con el orden físico y cronológico del libro.
9. **`[L-09]` Configuración obligatoria de `ChatSettings` (`chat_configure`):** Todo cuaderno se inicializa con `response_length="longer"` y el System Prompt paleográfico oficial.
10. **`[L-10 a L-15]` Perfiles de Escribanos (Ductus, Abreviaturas y Tics) + Uso de `.ged` solo como N-gramas Onomásticos:**
    - Para cada escribano se documenta de forma práctica su **ductus** (tipo de letra, velocidad, si une palabras) y sus **tics formulares y abreviativos** (sin complicarlo con un alfabetograma teórico separado), junto con el mapa de patologías físicas por fotograma (`Página Rota`, `Costura Apretada`, `Tinta Traspasada`, `Corrección`).
    - Los archivos `.ged` previos **NO se tratan como verdad absoluta de relaciones familiares ni fechas** (pueden contener errores de pruebas anteriores): se usan única y exclusivamente como **referencia onomástica pasiva (n-gramas de nombres y apellidos locales)**. La validación real de cada transcripción es siempre humana e iterativa por el usuario.
11. **`[L-20]` Protocolo de Fusión de Tomas Hermanas (Base vs. Corrección):** Las tomas duplicadas de FamilySearch (`004306112_01872/004306112_01873`, `004306112_01874/004306112_01875`, `004306112_01876/004306112_01877`, `004306112_01878/004306112_01879`, `004306112_01880/004306112_01881`) se envían de forma complementaria para rescatar texto perdido en lomos apretados y pies cortados, produciendo un único registro depurado con CERO DUPLICADOS.
12. **`[L-21]` Reautenticación Desatendida de NotebookLM MCP:** Renovación automática de credenciales mediante el perfil persistente de Chromium sin requerir intervención manual del usuario.
13. **`[L-22]` Transversalidad del Ductus Eclesiástico (Desacoplamiento Libro-Escribano):** La mano y los tics de un cura no cambian entre bautismos, matrimonios y entierros. Las fichas técnicas de caligrafía residen de forma centralizada en [`03_AUTORIDADES_PALEOGRAFICAS_ALTO_ALBERCHE.md`](file:///c:/TRABAJOS/personal/genealo/03_AUTORIDADES_PALEOGRAFICAS_ALTO_ALBERCHE.md).
14. **`[L-23]` Extracción Polimórfica Obligatoria:** Tratamiento estructurado y riguroso de documentos no sacramentales presentes en los libros: padrones de confirmaciones (`PADRON_CONFIRMACION`), decretos de visitas pastorales (`AUTO_VISITA`), índices alfabéticos (`INDICE_PARROQUIAL`) y minutas de sacristía (`MINUTA_SACRISTIA`).
15. **`[L-24]` Estándar Geográfico Cuatriletrado y Redirección Canónica Pre-1715:** Sustitución de `NAVA-` por `NRDL`, `NMRL`, `NCRZ`, `JMOL`, `NDRN`, `VLLR`, `BHND`. Redirección obligatoria de las búsquedas genealógicas de Molinillo y anejos anteriores a 1715 hacia Navalmoral de la Sierra (`NMRL`) y Navarredondilla (`NRDL`).
16. **`[L-25]` Protocolo de Trazabilidad Total y Tratamiento de Partidas Bipartitas (Split Acts):** Las partidas que arrancan al pie de una plana y concluyen en la siguiente (intra-imagen verso $\rightarrow$ recto, o inter-imagen recto $N \rightarrow$ verso $N+1$) se restituyen sin pérdida de padrinos ni firmas, vinculando mitades con marcadores direccionales.
17. **`[L-26]` Modelo de Identificación en Dos Capas (Soporte Físico Inmutable = Archivo JPG + Cita Archivística + Metadato ARK):** Separación tajante entre el **soporte físico digital inmutable** (`{DGS}_{FOTOGRAMA}`, ej. `004306112_01874`, que coincide 1:1 con el JPG en disco, con FamilySearch y con el titular de la URL ARK) y los **atributos descriptivos revisables** (`lado: izquierda/derecha`, `folio_manuscrito: 1v`, `id_archivistico: ES-AV-...`). Las actas poseen identificador interno propio en ArcadeDB desacoplado del orden numérico rígido, blindando el sistema contra omisiones o fusiones indebidas de la IA.
18. **`[L-27]` Desglose Obligatorio entre Redactor Material, Oficiante Sacramental y Firmas:** Desacoplamiento estricto en el bloque de extracción y en el modelo de grafo de ArcadeDB entre el **Redactor Material** (quien empuña físicamente la pluma, define el ductus caligráfico y enlaza con la arista `ESCRIBE`), el **Oficiante Sacramental** (quien bautiza/casa canónicamente con licencia o delegación y enlaza con la arista `OFICIA_SACRAMENTO`), y las **Firmas** (quien suscribe autógrafamente al pie con la arista `FIRMA`). Previene asignar páginas completas a sacerdotes que solo oficiaron un bautismo esporádico (como Don Rodrigo Antonio de Meneses en 1594 o Baltasar de Luján en 1624).
19. **`[L-28]` Identificación Primaria Absoluta mediante Nombre Completo de Archivo:** Toda referencia a un fotograma de imagen debe utilizar OBLIGATORIAMENTE su nombre completo de archivo (`{DGS}_{FOTOGRAMA}.jpg`, ej. `004306112_01874.jpg`). Queda terminantemente prohibido truncar la referencia únicamente al número de fotograma (ej. `01874.jpg` o `01874`). El proyecto abarca 9 rollos DGS distintos (más de 8.500 imágenes); por tanto, el nombre de archivo completo es la única clave primaria universal e inequívoca tanto para el archivo físico en disco, como para NotebookLM, ArcadeDB, el árbol genealógico y las URLs ARK de FamilySearch.
20. **`[L-29]` Principio de Aislamiento Topográfico y Grafocrítico en Cuadernos (`[CUADERNO-MONO-LOCALIDAD]`):** Ningún cuaderno de NotebookLM Pro debe mezclar fondos documentales de diferentes localidades o pueblos. Cada cuaderno debe asociarse estrictamente a **un único código cuatriletrado** (`NRDL`, `JMOL`, `NDRN`, `VLLR`, `NMRL`), garantizando la pureza del escribiente, los modismos notariales y la toponimia menor sin contaminación cruzada. En el Catastro de Ensenada, es obligatorio diferenciar escrupulosamente entre **Bienes de Legos / Seglares** (`BIENES_LEGOS`) y **Bienes Eclesiásticos** (`BIENES_ECLESIASTICOS`).
21. **`[L-30]` Principio de Reconstrucción Lógico-Sacramental (Desarticulación de Códices Mixtos y Series Puras Correlativas):** Los cuadernos de NotebookLM y las colecciones en el grafo deben organizarse por **Series Sacramentales Puras y Correlativas en el Tiempo** (Bautismos, Matrimonios, Defunciones) para cada localidad. Los códices físicos mixtos (volúmenes donde el párroco encuadernó varios sacramentos juntos por escasez de papel) se desarticulan lógicamente asignando cada fotograma a su serie cronológica correspondiente, reservando cuadernos o anexos independientes para documentos extraordinarios no sacramentales (censos de confirmación, inventarios de bienes de la iglesia, autos de visitas episcopales).
22. **`[L-31]` Tratamiento de Imágenes Híbridas (Duplicidad Lógica Multi-Cuaderno + Directiva de Extracción por Plana):** En fotogramas fotografiados a doble página que contienen sacramentos distintos en plana izquierda (verso) y derecha (recto) (ej. `004306112_02023.jpg`, `02044.jpg`, `02048.jpg`, `02049.jpg`, `02050.jpg`), se prohíbe cortar físicamente la imagen JPG. El archivo original `{DGS}_{FOTOGRAMA}.jpg` se mantiene íntegro y se incluye como fuente en ambos cuadernos sacramentales respectivos, instruyendo a NotebookLM mediante el prompt a procesar únicamente la plana correspondiente (`lado: izquierda` o `lado: derecha`). En ArcadeDB, cada partida se indexa desacoplada con su tipo sacramental y lado físico de soporte (`[L-26]`).
23. **`[L-32]` Autos de Visita Pastoral In Situ:** Los decretos y autos de Santa Visita Pastoral intercalados en los libros sacramentales (ej. `004306112_02052.jpg`, `02064.jpg`, `02088.jpg`, `02109.jpg-02111.jpg`) deben permanecer in situ en su posición cronológica exacta dentro de las series sacramentales, ya que constituyen auditorías canónicas contemporáneas de la diligencia o negligencia del cura y ordenan mandatos ecdóticos y paleográficos vinculantes para el propio libro.
24. **`[L-33]` Bucle de Retroalimentación Léxico-Onomástica y Toponímica Incremental:** Los diccionarios de anclaje (`01`) y autoridades paleográficas (`03`) no son estáticos ni cerrados de antemano. Operan en un bucle acumulativo vivo (*feedback loop*): cada nuevo topónimo menor (pagos, cerros, arroyos, molinos), variante gráfica de linajes locales o mano sacerdotal descubierta al transcribir un cuaderno se consolida de inmediato en el corpus de referencia para anclar y blindar las lecturas de los cuadernos siguientes de la comarca.
25. **`[L-34]` Protocolo de Reconocimiento Previo y Test A/B de Ductus:**
    - **Redacción Asistida de Guías Codicológicas (`02`):** Antes de iniciar la transcripción de un cascarón vacío con imágenes, se realiza un barrido topográfico mediante consultas preliminares al propio NotebookLM (fechas límite, cambios de cura, visitas episcopales) para redactar su guía `02_INSTRUCCIONES_CRONOLOGICAS_...` en minutos.
    - **Test Empírico de Rendimiento del Ductus:** Realización de pruebas comparativas A/B (con ficha caligráfica vs. ciego) en `NRDL-BAUT-01` para evaluar científicamente si el perfilado caligráfico detallado del párroco incrementa la fidelidad de la IA o si constituye sobreingeniería frente a la visión multimodal de Gemini.
26. **`[L-35]` Red Prosopográfica Comarcal del Clero del Alberche:** Los sacerdotes, tenientes, beneficiados y frailes regulares (especialmente del monasterio de Burgohondo) no operaban aislados en una única parroquia. La prosopografía del archivo `03` se expande orgánicamente en red interparroquial trazando la itinerancia de clérigos entre `NRDL`, `JMOL`, `NDRN`, `VLLR` y `NMRL`.
27. **`[L-36]` Arquitectura de Infraestructura HTR Efímera en GCE Spot VM y Disciplina de Costes:** El despliegue de eScriptorium y Kraken se realiza sobre instancias Spot de Google Compute Engine (`n1-standard-4`, 120 GB `pd-standard`). Toda sesión de trabajo se inicia con `python scripts/manage_escriptorium_vm.py start` (0,05 $/h) y se detiene obligatoriamente con `stop` al concluir (0,00 $/h en computación), conservando imágenes, bases de datos y modelos en el disco persistente (~4,80 $/mes).
28. **`[L-37]` Inviabilidad de Modelos HTR Generales Zero-Shot para Producción en Siglos XVI-XVII:** Ningún modelo pre-entrenado público de Kraken es apto para transcribir directamente manuscritos en letra procesal o cortesana del siglo XVII sin fine-tuning local. La extracción directa sobre imágenes de los siglos XVI y XVII se delega en Gemini 2.5 Pro / Flash.
29. **`[L-38]` Disección del Codec HTR: Modelo TRIDIS y Mapeo de la 's' Larga (`ſ`):** Para manuscritos notariales y parroquiales hispánicos, el modelo base de referencia es **TRIDIS**, cuyo codec de 183 clases unificó la `ſ` larga a la `s` ordinaria (`U+0073`) e integró superíndices (`º`, `ª`) y macrones notariales, alcanzando un 85-90% de acierto en el siglo XVIII sin requerir caracteres Unicode exóticos.
30. **`[L-39]` Pipeline Híbrido Gemini $\rightarrow$ eScriptorium (Aligeramiento PAGE-XML del 98% y Ground Truth Asistido):** Para entrenar modelos locales de Kraken sin transcripción manual lenta, se exporta el PAGE-XML de eScriptorium, se eliminan todos los nodos `<Word>` y `<Glyph>` (reduciendo de 16.000 líneas a ~300 líneas), se alimenta a Gemini con directiva de anti-normalización diplomática estricta para rellenar las etiquetas `<Unicode>`, y se reimporta para entrenar el modelo local con 5-10 folios de máxima fidelidad.
31. **`[L-40]` Particionado por Plana y Mitigación de Lomo Central en Microfilms:** El segmentador `blla.mlmodel` de Kraken puede generar ambigüedad en el canal de encuadernación de microfilms a doble página. Se resuelve mediante particionado lógico de planas antes de inferencia o corrección rápida con la herramienta tijeras (`✂`). Detalle en [`docs/BENCHMARK_HTR_ESCRIPTORIUM_KRAKEN.md`](file:///c:/TRABAJOS/personal/genealo/docs/BENCHMARK_HTR_ESCRIPTORIUM_KRAKEN.md).
32. **`[L-41]` Directivas de Entrenamiento Extremo para Kraken (`ketos`) en GPU:** Para maximizar la precisión paleográfica de Kraken y mitigar las limitaciones alfabéticas de modelos preentrenados, se aplican las 6 estrategias maestras de [`docs/ENTRENAMIENTO_EXTREMO_KRAKEN.md`](file:///c:/TRABAJOS/personal/genealo/docs/ENTRENAMIENTO_EXTREMO_KRAKEN.md):
    - **Topología CRNN profunda (`-s`):** Convolución ensanchada a 128/256 filtros para discriminar tinta traspasada (*bleed-through*), celdas BiLSTM de 256/512 unidades para ligaduras procesales, y entrada RGB nativa sin binarización destructiva.
    - **Aumento de Datos Agresivo (`--augment`):** Deformación espacial elástica (*grid distortion*) y ruido fotométrico sobre GPU Tesla T4 (16 GB VRAM).
    - **Control de Codec y Transferencia:** Expansión de codec (`--resize add`) para inyectar `ſ` larga (`U+017F`) y glifos NFD sobre modelos base, congelación de visión (`--freeze-backbone`), o entrenamiento *from scratch* con 50-100 folios curados por Gemini.
    - **Hiperparámetros de Rendimiento:** Batch size de 16-32 líneas y optimizador AdamW con *Cosine Annealing*.
    - **Model Ensembling:** Inferencia simultánea multimodelo por consenso estadístico de probabilidades CTC (`ketos trans -m A -m B -m C`).
    - **Ontología DLA Semántica:** Segmentación geométrica clasificada (`Region_Bautismo`, `Margen_Nombres`, `Auto_Visita_Pastoral`) para ingesta estructurada en ArcadeDB.

---

## 3. CATÁLOGO OFICIAL DE CUADERNOS EN NOTEBOOKLM (ACCESO VÍA MCP `notebooklm`)
> **Convención de Nombres Obligatoria:** Llamar siempre a cada cuaderno por su título oficial o descriptor exacto (nunca usar términos ambiguos como *"el primer cuaderno"* o *"el segundo cuaderno"*).

### A. Serie Canónica de Cuadernos Validados y en Producción (v2.0)

| Nº | Identificador / Título Oficial | ID en NotebookLM (`notebook_id`) | Localidad | Fuentes | Estado y Cobertura |
| :-: | :--- | :--- | :-: | :-: | :--- |
| **1** | **`Lib. Baut. Navarre Vol. 1 (1594-1695)`** | `7967d647-8ca2-4863-a576-11843e8e8802` | `NRDL` | 188 | **Cuaderno protegido.** Bautismos de Navarredondilla (1594–1695, DGS 004306112). 183 imágenes + 5 fuentes maestras (`00..04`). |
| **2** | **`NRDL-ENSENADA-LEGOS-01`** | `ec86de71-a11c-4489-bbb9-eea856cccac4` | `NRDL` | 87 | **Verificado E2E (READY).** Catastro Ensenada 1752, Personal Seglar Navarredondilla (DGS 004469033, 00881–00967). |
| **3** | **`JMOL-ENSENADA-LEGOS-01`** | `407d5cb4-4b83-495f-a23a-309ea44ee8c6` | `JMOL` | 28 | **Verificado E2E (READY).** Catastro Ensenada 1751, Personal Seglar San Juan del Molinillo (DGS 004469028, 00952–00979). |
| **4** | **`VLLR-ENSENADA-LEGOS-01`** | `e7fba70b-af7d-4602-b543-060742b22528` | `VLLR` | 51 | **Verificado E2E (READY).** Catastro Ensenada 1751, Personal Seglar El Villarejo (DGS 004469028, 00901–00951). |
| **5** | **`NDRN-ENSENADA-LEGOS-01`** | `cd72ef58-fcf5-48ac-8de2-556648ebd90e` | `NDRN` | 34 | **Verificado E2E (READY).** Catastro Ensenada 1751, Personal Seglar Navandrinal (DGS 004469028, 00980–01013). |
| **6** | **`NRDL-MATR-01`** | `1e6fec74-1e2f-4dd7-8ad1-6d25411de127` | `NRDL` | 36 | **Verificado E2E (READY).** Matrimonios Navarredondilla (1634–1686, DGS 004306112). 36 imágenes (33 originales + 3 añadidas bajo `[L-31]`: `004306112_02050.jpg` [boda Alonso Sánchez con Francisca Andrino], `004306112_02148.jpg` [tira con 3 bodas de 1667] y `004306112_02149.jpg` [tira con bodas de 1667–1668]). |
| **7** | **`JMOL-DIFU-03`** | `a5d19fcc-d266-4497-bdb3-df182328bdcb` | `JMOL` | 17 | **Verificado E2E (READY).** Libro 3º Defunciones San Juan del Molinillo (1849–1851, DGS 004298571). 17/17 imágenes READY. |
| **8** | **`NRDL-BAUT-01`** | `a187936c-55f4-4319-87db-6bf4e21e8613` | `NRDL` | 193 | **Purificado y Preparado (READY).** Bautismos Navarredondilla (1594–1695). 188 imágenes (depuradas 57 defunciones puras, preservadas 5 híbridas `02023`, `02044`, `02048`, `02049`, `02050` bajo `[L-31]`) + 5 fuentes maestras (`00..04`) + ChatSettings configurado. |
| **9** | **`NRDL-BAUT-02`** | `0a6561ec-ee7c-47bc-8164-bcba8be5acef` | `NRDL` | 157 | **Verificado E2E (READY).** Bautismos Navarredondilla. |
| **10** | **`NRDL-BAUT-03`** | `6853e55d-3e72-42d3-bf01-6d2a510978b7` | `NRDL` | 231 | **Verificado E2E (READY).** Bautismos Navarredondilla. |
| **11** | **`NRDL-BAUT-05`** | `9fa0454b-5898-4efc-be90-a02524298906` | `NRDL` | 144 | **Verificado E2E (READY).** Bautismos Navarredondilla. |
| **12** | **`NRDL-BAUT-06`** | `9cdd4e0c-a922-4edc-acfb-4a5dee7a896d` | `NRDL` | 183 | **Verificado E2E (READY).** Bautismos Navarredondilla. |
| **13** | **`NRDL-BAUT-07`** | `0a31b8ce-184b-49af-ae17-0df8446ecc5f` | `NRDL` | 102 | **Verificado E2E (READY).** Bautismos Navarredondilla. |
| **14** | **`NRDL-DIFU-01`** | `77aff174-b9ae-4273-be03-41d94b20a7d4` | `NRDL` | 236 | **Verificado E2E (READY).** Defunciones Navarredondilla. |
| **15** | **`NRDL-DIFU-01B`** | `5820003c-3577-496a-b3db-6903365a201f` | `NRDL` | 65 | **Verificado E2E (READY).** Defunciones Navarredondilla. |
| **16** | **`NRDL-DIFU-02`** | `1e77ba17-cf48-4fca-8a0a-e91aa41eb4bb` | `NRDL` | 171 | **Verificado E2E (READY).** Defunciones Navarredondilla. |
| **17** | **`NRDL-DIFU-03`** | `ab115a24-e08b-4ee6-b990-9027d7ac1abf` | `NRDL` | 170 | **Verificado E2E (READY).** Defunciones Navarredondilla. |
| **18** | **`NRDL-DIFU-04`** | `9e03f5d3-3425-456b-9df1-b69bf6a3a1a2` | `NRDL` | 188 | **Verificado E2E (READY).** Defunciones Navarredondilla. |
| **19** | **`NRDL-DIFU-05`** | `d73e0a6c-7fa9-4c78-aec9-6c0bfcfd2ccf` | `NRDL` | 211 | **Verificado E2E (READY).** Defunciones Navarredondilla. |
| **20** | **`NRDL-MATR-02`** | `c1ffffaf-c722-4ee9-9093-21194a822e69` | `NRDL` | 70 | **Verificado E2E (READY).** Matrimonios Navarredondilla. |
| **21** | **`NRDL-DIFU-S17 (1631-1701)`** | `14cf46ae-7d73-4f2c-b001-5e5de0f29c6c` | `NRDL` | 132 | **Verificado E2E (READY).** Defunciones Navarredondilla (1631–1701, DGS 004306112). 132 imágenes (70 originales + 62 añadidas [57 puras + 5 híbridas]). Renombrado desde `NRDL-MIXTO-01` / `NRDL-DIFU-S17-B` bajo `[L-30]`. |

### B. Corpus Certificado de San Juan del Molinillo (`JMOL`) (100% Ingestado y Verificado E2E)
- **Total corpus fotográfico JMOL:** **2.731 imágenes en 18 cuadernos parroquiales puros** bajo regla `[L-30]` (100% de fuentes en estado `READY`, 0 faltantes, 0 duplicados, certificado por auditor independiente).
- **Desglose de los 18 cuadernos certificados:**
  1. `JMOL-BAUT-01` (`fa62871d-cb66-4af4-8e13-4dcc1c12b7ce`): 175/175 fuentes READY (1715–1752, Libro 1º).
  2. `JMOL-BAUT-02` (`ad39ba03-d91f-4357-a4cd-bc845ff5f5d4`): 276/276 fuentes READY (1752–1800, Libro 2º).
  3. `JMOL-BAUT-03` (`8816402f-ccce-4ebe-95a1-eb337e8a367a`): 190/190 fuentes READY (1801–1826, Libro 3º-A).
  4. `JMOL-BAUT-04` (`303c70ed-bdd5-4570-a19a-08ebb945bdf5`): 189/189 fuentes READY (1827–1852, Libro 3º-B).
  5. `JMOL-BAUT-05` (`7f64917d-d8d1-45a0-b8c2-dfe0314a48d1`): 139/139 fuentes READY (1851–1862, Libro 5º).
  6. `JMOL-INDICE-BAUT` (`e26e1dd5-a9aa-469a-80af-3d52603bbdc0`): 111/111 fuentes READY. **Códice Bífido de Índices:**
     - *Sección Bautismos (1750–1914):* `02661.jpg` a `02748.jpg` (88 imágenes, orden alfabético por nombre de pila de la A a la Z).
     - *Sección Matrimonios (1716–1920):* `02749.jpg` a `02766.jpg` (18 imágenes) bajo el título *«Índice de casados en la Parroquia de San Juan Bautista de San Juan del Molinillo desde el año 1716»*. Disposición cronológica de contrayentes, estado civil, año, libro y folio. Llave maestra de toda la serie matrimonial.
  7. `JMOL-MATR-01` (`50e8d7d8-7afe-4d70-9a8e-e22cc2cc1101`): 194/194 fuentes READY (1716–1789, Libro 1º).
  8. `JMOL-MATR-02` (`772135ac-4305-4a22-ad89-bf996f0ff37a`): 134/134 fuentes READY (1790–1852, Libro 2º).
  9. `JMOL-MATR-03` (`07a61f80-24e6-484e-af57-ebe19d09960a`): 198/198 fuentes READY (1851–1899, Libro 3º).
  10. `JMOL-DIFU-01` (`44aaf6f4-ef87-4740-8d34-bc661923df87`): 202/202 fuentes READY (1715–1764, Libro 1º de Adultos).
  11. `JMOL-DIFU-02` (`9d0e8882-7d5f-4677-98f3-1913bbbefcc9`): 277/277 fuentes READY (1764–1848, Libro 2º de Adultos).
  12. `JMOL-DIFU-03` (`a5d19fcc-d266-4497-bdb3-df182328bdcb`): 17/17 fuentes READY (1849–1851, Libro 3º).
  13. `JMOL-DIFU-04` (`457361c1-70f8-4368-8e86-10b0beeb169f`): 214/214 fuentes READY (1851–1883, Libro 4º).
  14. `JMOL-DIFU-05` (`bbb4a49c-90a4-4af1-8818-484fa158e929`): 99/99 fuentes READY (1872–1881, Libro 5º).
  15. `JMOL-DIFU-06` (`de24a81e-df39-49ec-8ca0-63f23827f745`): 177/177 fuentes READY (1881–1892, Libro 6º).
  16. `JMOL-DIFU-PARVULOS` (`d974c19c-6a6d-46f2-8f29-e996af323d67`): 27/27 fuentes READY (1632/1644–1680, Libro de Párvulos Difuntos, joya del siglo XVII).
  17. `JMOL-INDICE-DIFU` (`34b553cd-c82d-4311-b5c6-bdaeb2451372`): 21/21 fuentes READY (1893–1907, Índice de Difuntos).
  18. `JMOL-SACRAMENTAL-1842-1850` (`81eb6310-b70c-40db-9fb0-b0c1f364ce05`): 91/91 fuentes READY. **Expediente Episcopal de Convalidación Sacramental (1842–1850):**
      - Códice extraordinario abierto tras el fallecimiento del cura párroco D. Marcelino Tore Díaz para recoger formalmente mediante declaraciones juradas de testigos, informes vecinales y testimonio del médico titular las partidas que habían quedado sin asentar por su enfermedad o desatención final.
      - Incluye: Bautismos 1847–1848 (con filiación completa a 4 abuelos y vecindad en Navandrinal y El Villarejo), Matrimonios 1842–1849 (con dispensas de parentesco) y Defunciones 1843–1849.
      - Aprobado y convalidado con valor registral pleno por decreto judicial del Obispo de Ávila, D. Manuel López Santisteban, en septiembre de 1850.

### C. Balance Integral del Fondo de Matrimonios de Navarredondilla y Detección de Lagunas
Tras la auditoría exhaustiva de los rollos DGS `004306112` y `004306113`, se constata que en FamilySearch solo existen **106 imágenes de matrimonios en todo el fondo microfilmado** de Navarredondilla:
1. **`NRDL-MATR-01` (1634–1686, DGS `004306112`):** 36 imágenes (33 del Libro 1º de Casados + 3 imágenes añadidas bajo `[L-31]` con bodas dispersas de 1667–1668 e intercaladas en `02050`).
2. **`NRDL-MATR-02` (1698–1803, DGS `004306113`):** 70 imágenes (Libro 2º de Casados dentro del códice bífido invertido + despachos nupciales).

#### Lagunas y Quiebras Documentales Constatadas:
- **Laguna Fundacional (1594–1634, 40 años):** No existe libro de desposorios propio conservado; Navarredondilla dependía de la villa matriz o colegiata comarcal.
- **Laguna Intermedia (1686–1698, 12 años):** Vacío documental sin registros conservados en la microfilmación.
- **La Gran Omisión del Siglo XIX (1803–1902, 99 años):** FamilySearch cortó abruptamente la filmación de matrimonios en noviembre de 1803 (fotograma `004306113_00800.jpg`), **omitiendo en su totalidad el Libro 3º de Casados**, a pesar de que la serie de Bautismos llega hasta 1889 (fotograma `004306113_00429.jpg`) y la de Defunciones hasta 1902 (fotograma `004306113_01535.jpg`).

#### Vías Alternativas de Recuperación Genealógica para el Siglo XIX:
1. **Expedientes Matrimoniales del Archivo Diocesano de Ávila:** Los legajos diocesanos de informaciones matrimoniales, dispensas de consanguinidad/afinidad y despachos de soltería contienen las actas matrimoniales completas omitidas en la filmación.
2. **Cruces Canónicos Interparroquiales con `JMOL` y `NMRL`:** Numerosos vecinos de Navarredondilla contrajeron nupcias en San Juan del Molinillo o Navalmoral de la Sierra, cuyas series de casados decimonónicas sí están disponibles y preservadas.
3. **Registro Civil de Navarredondilla (desde 1871):** Vía civil ininterrumpida para matrimonios entre 1871 y 1902.

### D. Cuadernos Históricos de Pruebas y Referencia

| Nº | Título Oficial del Cuaderno | ID en NotebookLM (`notebook_id`) | Fuentes | Contenido y Estado |
| :-: | :--- | :--- | :-: | :--- |
| **21** | **`libro bautismos navarre 1594-1637`** | `d28c82d0-e15f-4d4d-8333-61f529d52815` | 91 | Cuaderno experimental inicial (nombres antiguos `S3HT-...jpg`). Auditados sus 20 turnos de chat y 3 artefactos Studio (`L-01` a `L-09`). |
| **22** | **`matrimonio navarre 1698-1761`** | `b973ffbb-0097-4b1b-a518-25aefd9a46c9` | 79 | Libro de Matrimonios de Navarredondilla (1698–1761). Histórico. |
| **23** | **`Libro personas ensenada Navarredondilla`** | `d634b10e-386d-4397-96d1-d271eb71a70d` | 91 | Cuaderno experimental previo de Ensenada Navarredondilla. |
| **24** | **`Descripcion de la Provincia y Obispado de Avila`** | `528907f8-b1f2-42eb-8a9a-622e279a8bbb` | 49 | Contexto histórico y geográfico diocesano de Ávila. |
| **25** | **`inventario libros y scripts`** | `7ff7fe9a-5237-42e8-81bb-b68d4491cb77` | 2 | Contiene `Script JavaScript para FamilySearch.pdf` con auditoría visual. |

---

## 4. CRUCE DE IMÁGENES DE `Lib. Baut. Navarre Vol. 1 (1594-1695)` CONTRA EL INVENTARIO DEL ROLLO (`DGS 004306112`)
Al cruzar las **184 imágenes** subidas en `Lib. Baut. Navarre Vol. 1 (1594-1695)` (`7967d647-8ca2-4863-a576-11843e8e8802`) con [`inventario-navarredondilla-v3.pdf`](file:///c:/TRABAJOS/personal/genealo/imagenes/inventario-navarredondilla-v3.pdf) (Apéndices 1 y 2) y con `Script JavaScript para FamilySearch.pdf`:

1. **Limpieza y saneamiento completado en `Lib. Baut. Navarre Vol. 1 (1594-1695)`:**
   - **Duplicado eliminado:** La copia duplicada de `004306112_02067.jpg` (`ec8dfcc5-819d-45b2-8821-68b8c60b71de`) ha sido borrada con éxito el 30-oct-2026. Permanece la copia canónica `02f7a1a3-2665-4b6f-96cb-26711bc826b7`.
   - **Instrucción obsoleta eliminada:** Se borró `Instrucciones_Bautismos_NombresExactos.txt` (`02ca0514-3c45-474f-a986-ac5db2763824`).
   - **Fuentes maestras inyectadas con éxito (188 fuentes en total: 183 imágenes + 5 textos):**
     - `09661ff0-77cf-4a86-ba52-e14096491907`: `00_INSTRUCCIONES_PALEOGRAFICAS_V2`
     - `e05b2cf9-18ef-4626-a92c-d09eabdee28b`: `01_DICCIONARIO_ANCLAJE_NAVARREDONDILLA` (vocabulario onomástico y toponimia local).
     - `fe09fb0d-74e1-4683-a32a-15d0e639b4df`: `02_INSTRUCCIONES_CRONOLOGICAS_NAVARREDONDILLA_1594_1695` (guía cronológica de saltos y lagunas).
     - `cbd3380b-c6c1-4c50-a2d6-666e4fdcb59d`: `03_AUTORIDADES_PALEOGRAFICAS_ALTO_ALBERCHE` (banco transversal de escribanos, ductus, tics y firmas).
     - `0b8b5196-bfbd-4a61-90c5-5c045c5411a2`: `04_JURISDICCIONES_Y_DEPENDENCIAS_PARROQUIALES` (códigos cuatriletrados, dependencia de Molinillo pre-1715).
   - **`ChatSettings` configurado:** `custom_prompt` paleográfico oficial inyectado con `response_length="longer"`.
   - **Pruebas Piloto en Vivo Validadas (30-oct-2026):** 
     - Folio 1r (`004306112_01873.jpg`): 6 partidas extraídas con cero omisiones ([`transcripciones/004306112_01873.md`](file:///c:/TRABAJOS/personal/genealo/transcripciones/004306112_01873.md)).
     - Folios 1v y 2r (`004306112_01874.jpg` + `004306112_01875.jpg`): 13 partidas extraídas en plana doble, con rescate íntegro de los pies cortados de página (padrinos, testigos y firmas de D. Rodrigo Antonio de Meneses y Francisco Ximénez) ([`transcripciones/004306112_01874_01875.md`](file:///c:/TRABAJOS/personal/genealo/transcripciones/004306112_01874_01875.md)).
     - Folios 3v y 4r (`004306112_01878.jpg` + `004306112_01879.jpg`): 11 partidas extraídas en procesal encadenada pura de Joan Martínez, con aislamiento de bleed-through, rescate del cura propio Pedro de la Llana y confirmación forense de la omisión del escribano en el último asiento ([`transcripciones/004306112_01878_01879.md`](file:///c:/TRABAJOS/personal/genealo/transcripciones/004306112_01878_01879.md)).
     - Folio 1604 (`004306112_01895.jpg`): 14 partidas extraídas en letra de Alonso Hernández, con resolución del sesgo L-01 en Diego de Encabo (1-mayo-1604: `v. diego`) ([`transcripciones/004306112_01895.md`](file:///c:/TRABAJOS/personal/genealo/transcripciones/004306112_01895.md)).
     - Fusión Tomas Hermanas Folio 1r (`004306112_01872.jpg` + `004306112_01873.jpg`): Cotejo forense del arranque fundacional de 1594, confirmando ausencia de portada y misma fractura física en ambas tomas sin duplicados.
     - Fusión Tomas Hermanas Folios 2v–3r (`004306112_01876.jpg` + `004306112_01877.jpg`): 12 partidas extraídas en plena resolución de costura apretada en lomo (*gutter shadow*), cero duplicados y rescate de Fray Francisco de Oropesa ([`transcripciones/004306112_01876_01877.md`](file:///c:/TRABAJOS/personal/genealo/transcripciones/004306112_01876_01877.md)). Total acumulado: **56 actas sacramentales**.
   - **Nuevas Directivas Operativas Incorporadas (L-20 y L-21):**
     - `L-20` (Tratamiento de Tomas Hermanas en las 10 primeras imágenes): Identificación de las 5 parejas de tomas del fotógrafo (`01872/01873`, `01874/01875`, `01876/01877`, `01878/01879`, `01880/01881`) para fusionar texto oculto (costura apretada, pie cortado) evitando duplicación masiva.
     - `L-21` (Reautenticación desatendida): Renovación automática de tokens NotebookLM MCP vía perfil persistente de Chromium sin necesidad de reintroducir credenciales.
2. **Estructura de fotogramas subidos en `Lib. Baut. Navarre Vol. 1 (1594-1695)`:**
   - **Del Elemento 12 (`01872.jpg` a `01954.jpg`, 83 imágenes):**
     - Ya se excluyeron las cartelas negras (`1870`, `1871`), el Inventario de Alhajas de feb-1637 (`1955–1957iz`) y el Libro 1º de Casados (`1957d–1986`).
     - `004306112_01872.jpg` tiene la placa `"Volumen Entero / Página Rota"` y `004306112_01873.jpg` es su toma `"Corrección"` (Folio 1r, 23 de enero de 1594).
   - **Del Elemento 13 (selección de Bautismos del Libro 2º, 1638–1695, 100 imágenes únicas + 1 duplicada):**
     - `02051.jpg` a `02056.jpg` (6 imgs): Bautismos 1638–1641 (Folios 1 a 8, Francisco Sánchez del Unar y Fray Francisco de Prado; incluye Auto de Visita de jun-1638 en `02052.jpg` izq).
     - `02023.jpg` (1 img): Mitad izquierda = Bautismos 1640–1641 (Gaspar González); **Mitad derecha = Defunciones 1631–1633 (Memoria fundacional de Juan Agustín de Fuentes)**.
     - `02043.jpg`, `02044.jpg`, `02048.jpg` a `02050.jpg` (5 imgs): Bautismos 1640–1642 (Gaspar González). **Nota:** En `02044.jpg` (arriba izq) hay defunciones de 1672–1673 y en `02044.jpg` (dcha) defunciones de 1634–1635; en `02048.jpg` (izq) hay defunciones de 1644–1647; en `02049.jpg` (dcha arriba) hay un asiento de defunción; y en `02050.jpg` hay un matrimonio (*Alonso Sánchez con Francisca Andrino*) y un entierro de párvulo intercalados con los bautismos.
     - `02060.jpg` a `02067.jpg` (8 imgs únicas + 1 copia duplicada de `02067.jpg`): Bautismos 1643 a enero de 1647 (Diego Arias y Juan Fernández). En `02067.jpg` (mitad derecha), `02068.jpg` y `02070.jpg` está el **1º Padrón de Confirmaciones (abril 1649, Obispo Argáiz)**.
     - **Saltos internos en el bloque `02068.jpg` a `02147.jpg` (80 imgs) que deben añadirse a las instrucciones cronológicas del cuaderno:**
       1. **1649–1652 (`02069`–`02072`):** El orden cronológico es `02071.jpg` (1649, Fco. Sánchez del Unar) $\rightarrow$ `02072.jpg` (1650–1651, D. Marcos Conde) $\rightarrow$ `02069.jpg` (1652, D. Marcos Conde) $\rightarrow$ `02070.jpg` y `02073.jpg` (1653+, Andrés Bautista).
       2. **Pliego de 1672 incrustado en 1658 (`02084`–`02086`):** Entre el Folio 36 (`02085.jpg` izq, año 1658) y el Folio 37 (`02086.jpg`, año 1659) se encuadernó un pliego suelto de **1672** (`02085.jpg` dcha, Gaspar González).
       3. **Crisis documental de 1664–1676 (`02100.jpg` a `02102.jpg`):**
          - `02100.jpg` izq = Bautismos oct-nov 1676 (Juan de Ribas); `02100.jpg` dcha = Bautismo abr-1664 arriba + índice en borrador a dos columnas de **1668 y 1669** abajo.
          - `02101.jpg` izq = Minutas de sacristía de **1670, 1671 y 1672**; `02101.jpg` dcha = Bautismos 1665–1666 arriba + Bautismos y **1 Defunción de 1674** (*Catalina Sánchez, viuda de Juan del Valle*, 4-jul-1674) en el centro/abajo.
          - `02102.jpg` izq = Collage de retales cosidos de **1673 a 1675**; `02102.jpg` dcha = Folio 43 formal (**Año 1666**, Domingo Hernández y Fray Mateo del Molinillo).
          - `02109.jpg` a `02111.jpg` = Auto de Visita del 4-oct-1680 y reconstrucción de partidas de 1670–1675 desde borradores.
       4. **Padrón de Confirmaciones de 1681 y desorden de 1682–1684 (`02113.jpg` a `02122.jpg`):**
          - `02113.jpg` dcha a `02117.jpg` izq = **2º Padrón de Confirmaciones (mayo 1681, Obispo Fr. Juan Asensio, 160+ confirmados)**.
          - Entre los folios 70 y 73 (años 1682–1684), el orden cronológico real es **`02121.jpg` (Fol. 70, jun-ago 1682) $\rightarrow$ `02120.jpg` (Fol. 71, ago-oct 1682 + asiento mar-1684 en hueco) $\rightarrow$ `02122.jpg` (Fol. 72, año 1683 con letra redonda de Simón Palomo Bayala) $\rightarrow$ `02119.jpg` (Fol. 73, abr-jul 1684)**.
     - **Nota sobre `004306112_02151.jpg`:** El archivo de instrucciones menciona `02151.jpg` como transición de 1696, pero el cuaderno termina en `02147.jpg` (diciembre de 1695, cierre formal del Libro 2º en el Folio 114). En la auditoría del rollo se comprobó que `02148.jpg` a `02152.jpg` son retales rotos de matrimonios, defunciones y bautismos de la década perdida de **1665–1668**.

---

## 5. REFERENCIA A ARCHIVOS DESCARGADOS Y CONVERSACIÓN PREVIA
- **ID de la conversación de auditoría previa:** `c3e046f9-007d-48a4-b436-ef8fc4282aa1`
- **Copias locales de los informes Studio y dumps en `C:\Users\rgarc\.gemini\antigravity\brain\c3e046f9-007d-48a4-b436-ef8fc4282aa1\`:**
  - Informe de auditoría comparativa: [`auditoria_cuaderno_2_y_alfabetograma.md`](file:///C:/Users/rgarc/.gemini/antigravity/brain/c3e046f9-007d-48a4-b436-ef8fc4282aa1/auditoria_cuaderno_2_y_alfabetograma.md)
  - Volcado de los 20 turnos de chat de `d28c82d0`: [`chat_history_dump.md`](file:///C:/Users/rgarc/.gemini/antigravity/brain/c3e046f9-007d-48a4-b436-ef8fc4282aa1/scratch/chat_history_dump.md)
  - Informes Studio de `Lib. Baut. Navarre Vol. 1 (1594-1695)`: [`nb2_fichero_grafocritico.md`](file:///C:/Users/rgarc/.gemini/antigravity/brain/c3e046f9-007d-48a4-b436-ef8fc4282aa1/scratch/nb2_fichero_grafocritico.md), [`nb2_estudio_escribanos.md`](file:///C:/Users/rgarc/.gemini/antigravity/brain/c3e046f9-007d-48a4-b436-ef8fc4282aa1/scratch/nb2_estudio_escribanos.md), [`nb2_informe_1594_1605.md`](file:///C:/Users/rgarc/.gemini/antigravity/brain/c3e046f9-007d-48a4-b436-ef8fc4282aa1/scratch/nb2_informe_1594_1605.md)

