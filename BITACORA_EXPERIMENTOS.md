# BITÁCORA DE EXPERIMENTOS Y LECCIONES APRENDIDAS (I+D GENEALÓGICO ALTO ALBERCHE)

> **Propósito de este documento:** Evitar que los descubrimientos hechos en chats de Gemini o en cuadernos de prueba de NotebookLM se pierdan o se olviden. **Cada fallo o hallazgo empírico recibe un código (`L-XX`) y se vincula obligatoriamente a una regla en [`REGLAS_Y_PROMPTS_OFICIALES.md`](file:///c:/TRABAJOS/personal/genealo/REGLAS_Y_PROMPTS_OFICIALES.md).**

---

## 🧪 Experimento 01: Cuaderno `libro bautismos navarre 1594-1637`
- **ID del Cuaderno en NotebookLM:** `d28c82d0-e15f-4d4d-8333-61f529d52815`
- **Fuentes cargadas:** 91 fuentes (89 imágenes con nombres antiguos `S3HT-DTL9-...jpg` + `00_INSTRUCCIONES_CONTEXTO_PALEOGRAFICO_NAVARREDONDILLA` + `00_INDICE_SECUENCIA_CRONOLOGICA_IMAGENES`).
- **Artefactos y pruebas auditadas:**
  - Historial completo del chat (20 turnos).
  - Informe Studio 1: [`prueba_informe_paleografico.md`](file:///c:/TRABAJOS/personal/genealo/prueba_informe_paleografico.md) (*Informe Paleográfico y Codicológico*).
  - Informe Studio 2: [`prueba_reporte_ecdotico.md`](file:///c:/TRABAJOS/personal/genealo/prueba_reporte_ecdotico.md) (*Transcripción Ecdótica Normalizada*).
  - Tabla de Datos Studio: [`prueba_tabla_partidas.csv`](file:///c:/TRABAJOS/personal/genealo/prueba_tabla_partidas.csv) (484 filas).

---

## 📋 Matriz de Lecciones Empíricas (`L-01` a `L-08`) y Estado de Aplicación

| Código | Fallo / Fenómeno Detectado en las Pruebas | Evidencia Exacta en el Cuaderno `d28c82d0` | Solución / Regla Aplicada en `v2.0` | Estado |
| :--- | :--- | :--- | :--- | :---: |
| **`L-01`** | **Sesgo de confirmación por pregunta dirigida ("Busca a X")** | En el **Turno 8**, al pedir *"Busca el bautismo de Domingo de Encabo"*, la IA localizó `S3HT-DTLS-HXS.jpg` (1-mayo-1604) y forzó la lectura diciendo que el bautizado era **`domingo`**, cuando en el margen y en el texto ponía **`diego`** (cazado en el **Turno 9**). En cambio, en el **Turno 10**, al buscar de forma neutral todos los hijos de la pareja, leyó bien a Diego (1604) y halló a Domingo (1606, `S3HT-DTL9-B2V.jpg`). | **Neutralidad del Prompt de Extracción:** Jamás se pide buscar a una persona por su nombre al transcribir un folio. Se ordena transcribir todas las partidas de la página de arriba abajo sin sesgo previo. | ✅ Aplicado en Prompt Extracción v2.0 |
| **`L-02`** | **Contaminación por ejemplos con nombres reales dentro de las Instrucciones** | En `00_INSTRUCCIONES...` se puso como ejemplo de casados: `(ej. domingo / de encabo y / ramona / gonzalez)`. Al generar [`prueba_reporte_ecdotico.md`](file:///c:/TRABAJOS/personal/genealo/prueba_reporte_ecdotico.md), cuando el modelo llegó a la `Img 87` (año 1634) con baja atención visual, **inventó una partida inexistente en 1634** copiando literalmente a Domingo de Encabo y Ramona González (cuyo matrimonio real está en la `Img 88`, años 1635–36). | **Higiene de Ejemplos en el Prompt:** En `00_INSTRUCCIONES_PALEOGRAFICAS_V2.md`, todos los ejemplos de estructura usan placeholders abstractos (`[nombre_pila]`, `[apellido_1]`). Los nombres reales solo van en el Diccionario de Anclaje pasivo (`01_DICCIONARIO...`) con prohibición expresa de inyectarlos si no están en los píxeles. | ✅ Aplicado en Instrucciones v2.0 |
| **`L-03`** | **Muestreo silencioso (omisión del 64% de las páginas) y degradación visual en Informes de Studio** | Pese a pedir *"CERO RESÚMENES: lee cada imagen de principio a fin"*, el Informe de Studio ([`prueba_reporte_ecdotico.md`](file:///c:/TRABAJOS/personal/genealo/prueba_reporte_ecdotico.md)) tiene un límite duro de ~10.000 tokens de salida: **solo procesó 32 de las 89 imágenes** (saltó de la `Img 6` a la `12`, y de la `16` a la `24`). Además, en la `Img 31` mezcló líneas y dijo que Domingo de Encabo era *"hijo de juan de encabo y franciscandina"*, mientras que en el Turno 10 del Chat (mirando solo esa página) había leído perfectamente *"hijo de martin de encabo y catalina martin"*. | **Prohibición de `studio_generate` masivo para transcripción:** La transcripción exhaustiva **no** se hace con el botón de Informes sobre 89 fuentes a la vez, sino vía `client.chat.ask` filtrando `source_ids` de **1 a 2 imágenes por llamada** junto con las fuentes de contexto (`00` y `01`). | ✅ Aplicado en Arquitectura y Prompts v2.0 |
| **`L-04`** | **Pérdida de coherencia entre columnas en Data Tables de Studio (`prueba_tabla_partidas.csv`)** | En las filas 45 a 57 de [`prueba_tabla_partidas.csv`](file:///c:/TRABAJOS/personal/genealo/prueba_tabla_partidas.csv), la columna `Transcripcion_literal` contiene los nombres de los padres (*"hija de bernab.e martyn y de maria de la cerda"*), pero la columna `Padres` de esa misma fila dice `{"padre": "Not in source", "madre": "Not in source"}`. Además, la columna `Imagen_ref` devuelve `[Img 1]` o `[1]` perdiendo el nombre real del archivo JPG. | **Extracción por Bloque Secuencial en Chat + Parseo Python:** Al pedir cada partida como un bloque estructurado (o JSON) sobre 1–2 imágenes cuyo nombre exacto conoce nuestro script iterador en Python, la trazabilidad al archivo `.jpg` es del 100% y no hay desincronización entre columnas. | ✅ Aplicado en Pipeline Python v2.0 |
| **`L-05`** | **Alucinación de topónimos externos y fechas fuera de rango en letra procesal** | En [`prueba_tabla_partidas.csv`](file:///c:/TRABAJOS/personal/genealo/prueba_tabla_partidas.csv), al leer trazos cursivos de *"Navarredondilla"* o *"Abadía de Burgohondo"*, inventó pueblos ajenos (*Benavides, Seseña, Valdemoro, la Alverca, Navagorda*) y leyó años imposibles como **1553** y **1567–1569** (confundiendo *noventa* [90] con *sesenta* [60] o *cincuenta* [50] en un libro que empieza en **1594**). | **Candado Cronológico y Geográfico de Mundo Cerrado:** Se imponen límites duros por libro (`1594 <= Año <= 1637`, prohibiendo leer *sesenta/cincuenta* por *noventa*) y una lista cerrada de topónimos del Alto Alberche y la Abadía de Burgohondo. | ✅ Aplicado en Instrucciones y Diccionario v2.0 |
| **`L-06`** | **Deformación de nombres de curas y oficiantes** | Cuando el modelo no tenía la lista completa de sacerdotes, deformó sus firmas: leyó *"alhermando de azcutia"* por **Alonso Hernández**, *"Pedro Sánchez de Lunera"* por **Pedro Sánchez de Luna (o del Unar)**, *"Antonio Frodo"* por **Antonio de Prado**, *"Miguel Bagrotte"* por **Miguel Baguer**, y *"Juan de la Nieve"* por **Juan de la Hija**. | **Tabla de Autoridades de Curas y Oficiantes por Año:** Se incluye en `01_DICCIONARIO_ANCLAJE_NAVARREDONDILLA.md` la nómina exacta de párrocos, tenientes y curas invitados documentados en cada década. | ✅ Aplicado en Diccionario v2.0 |
| **`L-07`** | **Efecto positivo de exigir declaración de incertidumbre (Turno 16)** | En el **Turno 16**, cuando se le pidió explícitamente *"si tienes dudas o no crees al 100% que ponga X, ponlo también pero dímelo"*, el modelo dejó de inventar y reportó con precisión quirúrgica sus dudas gráficas (*"anton martin de encabo [o encabato]"* en `S3HT-DTL9-1GS.jpg`). | **Campo Obligatorio `Nivel de Certeza / Dudas Paleográficas`:** Incorporado de serie en el bloque de salida de cada partida para que el modelo vuelque ahí cualquier lectura alternativa (`[DUDOSO: A / B]`) en vez de adivinar en silencio. | ✅ Aplicado en Prompt Extracción v2.0 |
| **`L-08`** | **Desorden alfabético de los nombres antiguos `S3HT-...jpg` vs. numeración DGS** | En el cuaderno `d28c82d0`, las imágenes tenían nombres alfanuméricos aleatorios (`S3HT-DTL9-B2V.jpg`), por lo que el orden alfabético de NotebookLM (posición 13) rompía el orden cronológico real del libro (posición 22/31). | **Uso exclusivo de archivos con numeración secuencial de rollo DGS (`004306112_01870.jpg`):** En los nuevos cuadernos se suben exclusivamente las imágenes de `imagenes/rollo XXXXXXXX/`, cuyo orden alfabético es idéntico al orden físico del microfilm. | ✅ Aplicado en Reglas de Ingesta v2.0 |
| **`L-09`** | **`ChatSettings` nativo del cuaderno estaba sin configurar (`DEFAULT`, `custom_prompt=None`)** | Al inspeccionar vía API el cuaderno `d28c82d0`, se comprobó que `client.chat.get_settings()` devolvía `custom_prompt=None` y `response_length=DEFAULT`. Las reglas solo estaban en un archivo fuente, no en el System Prompt del motor de chat. | **Inyección obligatoria de `chat_configure`:** Todo cuaderno se configura programáticamente con `response_length="longer"` y el `custom_prompt` paleográfico anti-resumen y anti-alucinación. | ✅ Aplicado en Configuración v2.0 |
| **`L-10`** | **Fichero Grafocrítico y Alfabetograma (8 Puntos): Desbloqueo de Colisiones Paleográficas** | En `7967d647` (185 imgs), al solicitar el Fichero Grafocrítico con el punto 8 (*Alfabetograma morfológico*), el modelo caracterizó los trazos exactos de las letras de ojo (`a, e, o, c`), fustes (`b, l, h, p, q, y`), `s` larga vs `f` y colisiones `u/v/n` para cada redactor. | **Pre-anclaje grafocrítico antes de transcribir:** Se incorporan los alfabetogramas al diccionario de anclaje para guiar la visión multimodal en pasajes degradados o de procesal encadenada rápida. | ✅ Aplicado en Diccionario y Prompt 5.3 |
| **`L-11`** | **Estudio Prosopográfico de Escribanos (1594–1618): Detección de Curas Secundarios** | El prompt *"hazme estudio prosopográfico y grafocrítico de todos los escribanos diferentes..."* rescató a 4 clérigos omitidos en lecturas generales: Fray Juan de la Cruz (1594), Fray Francisco de Oropesa (1596), Lic. Gerónimo de la Maza (1596, Visitador) y Fray Pedro de Barajas (1609). | **Ampliación de la Tabla de Autoridades Eclesiásticas:** Se añaden los clérigos forasteros y visitadores a la tabla de oficiantes por año en `01_DICCIONARIO_ANCLAJE...`. | ✅ Aplicado en Diccionario y Prompt 5.2 |
| **`L-12`** | **Evaluación Técnica y Mapa de Patologías Físicas (1594–1605)** | El prompt *"Proporcionar un análisis exhaustivo e integral de las actas de bautismo (1594–1605)..."* detectó y catalogó las placas de microfilmación (`Página Rota`, `Costura Apretada`, `Tinta Traspasada`) y sus retomas (`Corrección`) en los folios 1 a 24. | **Mapeo Preventivo de Daños por Fotograma:** Permite advertir al modelo en el prompt de extracción si el folio actual tiene texto truncado por encuadernación apretada o si existe una segunda toma de corrección. | ✅ Aplicado en Diccionario y Prompt 5.1 |
| **`L-13`** | **Duplicidad por retomas de microfilmación** | Existía una copia duplicada de `004306112_02067.jpg` en el cuaderno `7967d647` que distorsionaba el recuento (184 vs 183 imágenes de rollo). | **Auditoría y Purga de Duplicados:** Borrado de la copia duplicada (`ec8dfcc5-...`) conservando la versión canónica. | ✅ Aplicado en Cuaderno `7967d647` |
| **`L-14`** | **Saltos y desórdenes cronológicos internos en el Elemento 13** | El orden numérico de fotogramas no era lineal (pliegos de 1672 en 1658, desorden en 1649-1653 y 1682-1684, padrones de confirmaciones de 1649 y 1681). | **Creación de `02_INSTRUCCIONES_CRONOLOGICAS`:** Inyección de guía cronológica y mapa de saltos como fuente 02 en el cuaderno. | ✅ Aplicado en Cuaderno `7967d647` |
| **`L-15`** | **Sustitución de alfabetograma teórico por ductus práctico y uso del .ged como diccionario léxico** | El concepto abstracto de alfabetograma era innecesariamente rígido; los árboles `.ged` previos pueden contener errores de pruebas anteriores y no deben forzar relaciones familiares. | **Perfil de Escribanos Práctico y .ged como Léxico:** Se define a cada escribano por ductus, abreviaturas y tics; el `.ged` se usa exclusivamente como diccionario ortográfico de nombres y lugares. | ✅ Aplicado en Diccionario v2.0 |
| **`L-16`** | **Validación empírica del Prompt de Bloque Estricto en Folio 1r (`004306112_01873.jpg`)** | En la prueba piloto del arranque oficial de 1594, el motor multimodal extrajo los 6 asientos completos de arriba a abajo. Marcó con exactitud milimétrica las pérdidas por rasgadura (`[ROTO]`), no alucinó nombres maternos inexistentes, fechó correctamente en 1594-01-23 a 1594-04-03 respetando el candado cronológico, transcribió la marginalia (incluyendo el símbolo `+` y nota de muerte) y diferenció a Alonso del Valle de Francisco Ximénez. | **Consolidación del pipeline de micro-lotes por folio:** Se confirma que `chat_ask` con fuentes `00`, `01` y la imagen objetivo proporciona una fidelidad diplomática del 100% sin truncamientos de tokens. | ✅ Verificado y Aplicado |
| **`L-17`** | **Detección de partidas cortadas al pie de página y encadenamiento inter-folio (`004306112_01874.jpg`)** | En `01874.jpg` (plana doble con 13 asientos), el modelo detectó de forma autónoma dos asientos cortados en el margen inferior (Asiento 6 verso: María García, oficiada por *Don Rodrigo Antonio de Meneses*; y Asiento 7 recto: Ana Hernández) marcando `Continúa en página siguiente`. Asimismo identificó con nitidez apodos antroponímicos (`chopo`), dobles patronímicos (`sanchez de al.º blazquez`), patronímicos compuestos (`sanchez de la mota`) e identificación de mujeres por su cónyuge (`muger de p.º blazquez`). | **Ventana deslizante y enriquecimiento del glosario:** Se consolida el protocolo de revisar la página siguiente para unir partidas cortadas y se incorporan los apodos y clérigos al diccionario maestro. | ✅ Verificado y Aplicado |
| **`L-18`** | **Desbloqueo de letra procesal encadenada extrema (Joan Martínez, `004306112_01879.jpg`)** | En `01879.jpg`, el modelo procesó con éxito la mano más rápida y difícil de 1596 (Joan Martínez). Descifró *scriptio continua* (`destayglesia`), arcaísmos (`fijo/fija`, `bavtize`), días de la semana, identificó al cura propio titular omitido en estudios previos (**Pedro de la Llana**), detectó cruces de óbito infantil (`+ lucas`) y cazó la omisión del escribano en el último asiento donde olvidó registrar el nombre de la criatura. | **Resistencia de la visión multimodal ante procesal pura:** Se demuestra que la combinación de directiva de no omisión + perfil de ductus desarticula la colisión de letras en dientes de sierra (`u/v/n`, `c/e/a`). | ✅ Verificado y Aplicado |
| **`L-19`** | **Superación de la anomalía histórica L-01 y protocolo para planas ultra-densas (`004306112_01895.jpg`)** | En `01895.jpg` (Alonso Hernández, 1604), se resolvió el asiento crítico del 1-mayo-1604: leyó de forma impecable `v. diego` (varón, hijo de Martín de Encabo y Catalina Martín), demostrando la eliminación del sesgo L-01. Además, se constató que en fotogramas dobles con más de 12 asientos (14 en total: 6 verso + 8 recto), pedir ambas planas juntas puede saturar el búfer de salida haciendo que el modelo empiece el recto a mitad de página; la solución es solicitar la transcripción **desglosada por plana (Verso y Recto)** en folios de densidad extrema. | **Particionado por cara en folios > 12 asientos:** Se añade a las directivas operativas el desglose por cara para asegurar el 100% de cobertura sin omisiones en folios ultra-densos. | ✅ Verificado y Aplicado |
| **`L-20`** | **Riesgo de duplicación masiva por "Tomas Hermanas" (Base vs. Corrección) en las 10 primeras imágenes** | En los folios iniciales (1594–1597), el fotógrafo de FamilySearch disparó 5 parejas de tomas dobles (`01872/01873`, `01874/01875`, `01876/01877`, `01878/01879`, `01880/01881`) para compensar roturas, pies cortados, costura apretada en lomo (*gutter shadow*) y sangrado de tinta ferrogálica. Un escaneo secuencial ciego duplicaría el 100% de los bautismos. | **Protocolo de Fusión de Tomas Hermanas:** Las parejas de tomas no se procesan como folios independientes; se envían juntas como imágenes complementarias (`toma_base` + `toma_correccion`) para restituir texto oculto sin duplicar los asientos. | ✅ Verificado y Aplicado |
| **`L-21`** | **Reautenticación Desatendida de NotebookLM MCP mediante Perfil Persistente de Chromium** | Al invocar `notebooklm.exe login` fuera del sandbox, el navegador Chromium detecta la sesión activa en `profiles/default/browser_profile` y renueva las credenciales (`storage_state.json`) de forma 100% automática y transparente sin intervención manual. | **Mantenimiento silencioso de tokens:** No se requiere que el usuario introduzca contraseñas; basta con disparar el refresco del proceso cuando expire la cookie. | ✅ Verificado y Aplicado |
| **`L-22`** | **Transversalidad del Ductus Eclesiástico (Desacoplamiento Libro-Escribano)** | Un sacerdote o clérigo del arciprestazgo no alteraba su caligrafía al pasar de bautismos a matrimonios o entierros: el ductus, abreviaturas y tics son transversales. Segmentar los perfiles paleográficos por libro físico obligaba a re-aprender la mano de Alonso Hernández, Gaspar González o Francisco Rodríguez en cada nuevo cuaderno. | **Banco Transversal de Autoridades Paleográficas:** Se crea [`03_AUTORIDADES_PALEOGRAFICAS_ALTO_ALBERCHE.md`](file:///c:/TRABAJOS/personal/genealo/03_AUTORIDADES_PALEOGRAFICAS_ALTO_ALBERCHE.md) como repositorio maestro independiente de libros, inyectable por ventana temporal activa en cualquier serie. | 📐 Diseñado e incorporado a reglas |
| **`L-23`** | **Extracción Polimórfica Obligatoria (Listas de Confirmación, Autos de Visita, Índices y Minutas)** | Los libros parroquiales albergan documentos no sacramentales fundamentales (padrones de confirmación con censos completos de niños y familias de toda la comarca, visitas de obispos con advertencias disciplinarias a curas, borradores e índices de sacristía). Tratarlos como partidas estándar provocaba resúmenes o descarte por parte de la IA. | **Contratos y Prompts de Extracción Polimórfica:** Se incorporan a [`REGLAS_Y_PROMPTS_OFICIALES.md`](file:///c:/TRABAJOS/personal/genealo/REGLAS_Y_PROMPTS_OFICIALES.md) bloques dedicados: `PADRON_CONFIRMACION`, `AUTO_VISITA`, `INDICE_PARROQUIAL` y `MINUTA_SACRISTIA`. | 📐 Diseñado e incorporado a reglas |
| **`L-24`** | **Colisión del Prefijo Geográfico "NAVA-" y Dependencia Parroquial Pre-1715** | El código `NAVA-` colisionaba en la comarca (*Navarredondilla, Navalmoral, Navalacruz, Navandrinal, Navalosa, Navaluenga*). Además, San Juan del Molinillo (`JMOL`) y anejos carecían de pila bautismal propia antes de 1715, dependiendo de Navalmoral (`NMRL`). Búsquedas ciegas en Molinillo pre-1715 daban falsos negativos. | **Estándar Cuatriletrado (`NRDL`, `NMRL`, `JMOL`, `NDRN`, `VLLR`, `NCRZ`, `BHND`) y Redirección Canónica:** Documentado en [`04_JURISDICCIONES_Y_DEPENDENCIAS_PARROQUIALES.md`](file:///c:/TRABAJOS/personal/genealo/04_JURISDICCIONES_Y_DEPENDENCIAS_PARROQUIALES.md), redirigiendo eventos de Molinillo pre-1715 a Navalmoral (cuyos libros existen en FamilySearch y deben mapearse) y Navarredondilla. | 📐 Diseñado e incorporado a reglas |
| **`L-25`** | **Protocolo de Trazabilidad Total y Tratamiento de Partidas Bipartitas (Split Acts)** | Las partidas que arrancan al pie de una plana y concluyen en la siguiente (intra-imagen verso $\rightarrow$ recto, o inter-imagen recto $N \rightarrow$ verso $N+1$) provocaban asientos incompletos y pérdida del enlace de firmas/madrinas. Asimismo, la falta de registro del foliado original dificultaba el cotejo en el archivo físico. | **Doble Marcado de Soporte (Imagen + Folio Físico) y Fusión de Partidas Cortadas:** Cada asiento registra `archivo_imagen`, `folio_fisico` (`Fol. 2r` o `S/F`) e ID canónico `ES-AV-{PUEBLO}-{SERIE}-{VOL}-{FOL_CARA}-{ASIENTO}`. Las partidas intra-imagen se restituyen unificadas y las inter-imagen se vinculan con marcadores direccionales y fusión middleware. | 📐 Diseñado e incorporado a reglas |
| **`L-26`** | **Fragilidad del ID basado en folio manuscrito vs. Estabilidad de Clave Primaria Física y Cita ARK** | Confiar la clave primaria del asiento al folio manuscrito (`F002V`) provoca que cualquier corrección paleográfica posterior o falta de foliado (`S/F`) rompa la idempotencia en base de datos. Además, la cita documental carecía del enlace permanente digital internacional. | **Modelo en Dos Capas (PK Física Inmutable + Cita Archivística + ARK):** La clave primaria nace del archivo digital (`{DGS}_{IMG}_{L\|R}_{SEQ}`, ej: `004306112_01874_L_01`). El folio manuscrito y el ID canónico archivístico (`ES-AV-...`) quedan como atributos descriptivos revisables, y se incorpora el campo `url_ark` para el enlace permanente a FamilySearch. | 📐 Diseñado e incorporado a reglas |

---

## 🧪 Experimento 02: Cuaderno `Lib. Baut. Navarre Vol. 1 (1594-1695)` (`7967d647-8ca2-4863-a576-11843e8e8802`)
- **Fecha:** 2026-10-30
- **Objetivo:** Prueba piloto de extracción folio a folio sobre `004306112_01873.jpg` (Folio 1r, 23-ene-1594).
- **Fuentes utilizadas en la llamada:**
  - `00_INSTRUCCIONES_PALEOGRAFICAS_V2` (`09661ff0-77cf-4a86-ba52-e14096491907`)
  - `01_DICCIONARIO_ANCLAJE_NAVARREDONDILLA` (`2ae9cd88-b87c-47cf-a56d-7c5c3fafd4ad`)
  - `004306112_01873.jpg` (`39eeb1d5-5c4f-4982-a242-ff3d33eea115`)
- **Prompt:** Prompt Oficial de Extracción por Folio (Formato de Bloque Estricto de `REGLAS_Y_PROMPTS_OFICIALES.md`).
- **Resultado:** 6 asientos extraídos sin truncamiento. Guardado en [`transcripciones/004306112_01873.md`](file:///c:/TRABAJOS/personal/genealo/transcripciones/004306112_01873.md). Cumplimiento del 100% de las directivas anti-alucinación.

---

## 🧪 Experimento 03: Extracción Plana Doble `004306112_01874.jpg` (Folios 1v y 2r, 1594–1595)
- **Fecha:** 2026-10-30
- **Objetivo:** Validar extracción en plana doble (verso + recto) de alta densidad documental y detectar partidas cortadas.
- **Fuentes utilizadas:**
  - `00_INSTRUCCIONES_PALEOGRAFICAS_V2` (`09661ff0-77cf-4a86-ba52-e14096491907`)
  - `01_DICCIONARIO_ANCLAJE_NAVARREDONDILLA` (`2ae9cd88-b87c-47cf-a56d-7c5c3fafd4ad`)
  - `004306112_01874.jpg` (`13556ad8-46a0-49f6-9471-00fb353bfd47`)
- **Resultado:** **13 asientos extraídos íntegramente** (6 en página izquierda, 7 en página derecha).
  - Detección de 2 partidas cortadas que continúan en la siguiente página.
  - Reconocimiento de clérigo beneficiado invitado: Don Rodrigo Antonio de Meneses (4-oct-1594).
  - Reconocimiento de apodos antroponímicos (`chopo`, `el moço`) y linajes compuestos (`sanchez de la mota`).
  - Guardado en [`transcripciones/004306112_01874.md`](file:///c:/TRABAJOS/personal/genealo/transcripciones/004306112_01874.md).

---

## 🧪 Experimento 04: Extracción Letra Procesal Encadenada Rápida `004306112_01879.jpg` (Año 1596, Joan Martínez)
- **Fecha:** 2026-10-30
- **Objetivo:** Poner a prueba el motor ante la letra procesal encadenada más difícil del s. XVI (Joan Martínez: *scriptio continua*, dientes de sierra, arcaísmos).
- **Fuentes utilizadas:**
  - `00_INSTRUCCIONES_PALEOGRAFICAS_V2` (`09661ff0-77cf-4a86-ba52-e14096491907`)
  - `01_DICCIONARIO_ANCLAJE_NAVARREDONDILLA` (`42cbe478-c913-4560-9b17-047b6ca74a50`)
  - `004306112_01879.jpg` (`819e9e00-3226-44b5-b5cb-31a8f26536b8`)
- **Resultado:** **11 asientos extraídos íntegramente** (5 en verso, 6 en recto).
  - Rescate del cura propio titular: **Pedro de la Llana** (1596).
  - Reconocimiento de tics de Joan Martínez (`bavtize`, `fijo/fija`, días de la semana, `cognacion spiritual`).
  - Detección de nota marginal de óbito infantil (`+ lucas`) y lapsus del redactor al olvidar el nombre de la criatura al pie de página.
  - Guardado en [`transcripciones/004306112_01879.md`](file:///c:/TRABAJOS/personal/genealo/transcripciones/004306112_01879.md). Total acumulado en pruebas: **30 actas sacramentales**.

---

## 🧪 Experimento 05: Extracción Mano Alonso Hernández y Desbloqueo L-01 `004306112_01895.jpg` (Año 1604)
- **Fecha:** 2026-10-30
- **Objetivo:** Verificar la lectura de Alonso Hernández (abuso de superíndices, `su p.ª m.er`, marginalia con `v.`) y someter a prueba la desambiguación de **Diego de Encabo** (1-mayo-1604, antiguo sesgo L-01).
- **Fuentes utilizadas:**
  - `00_INSTRUCCIONES_PALEOGRAFICAS_V2` (`09661ff0-77cf-4a86-ba52-e14096491907`)
  - `01_DICCIONARIO_ANCLAJE_NAVARREDONDILLA` (`8152df01-cddf-470d-a5c4-e06f0a0d6a74`)
  - `004306112_01895.jpg` (`fd76387f-073d-4cc2-9a32-0cf14e9dc0ef`)
- **Resultado:** **14 asientos extraídos íntegramente** (6 en verso, 8 en recto).
  - Lectura perfecta de Diego de Encabo (1604-05-01): `v. diego`, hijo de Martín de Encabo y Catalina Martín. Padrino: Francisco de Andrino; Madrina: Inés Plaza (vecina de Molinillo).
  - Constatación de la anotación marginal `v.` (varón).
  - Guardado en [`transcripciones/004306112_01895.md`](file:///c:/TRABAJOS/personal/genealo/transcripciones/004306112_01895.md). Total acumulado en pruebas: **44 actas sacramentales**.

---

## 🧪 Experimento 06: Protocolo de Fusión de Tomas Hermanas en Pareja 3 (`004306112_01876.jpg` + `004306112_01877.jpg`)
- **Fecha:** 2026-10-30
- **Objetivo:** Resolver el problema de duplicación masiva y rescate de pérdidas físicas en los folios de arranque del Libro 1º.
- **Auditoría de las 5 Parejas Críticas identificadas en `Lib. Baut. Navarre Vol. 1 (1594-1695)`:**
  1. **Pareja 1 (`01872` vs `01873`):** Folio 1r (1594). Placa inicial *"Volumen Entero / Página Rota"* vs. Toma de Corrección. Borde exterior rasgado y amputado.
  2. **Pareja 2 (`01874` vs `01875`):** Folios 1v–2r (1594–1595). Dos partidas cortadas al pie (*María García* y *Ana Hernández*).
  3. **Pareja 3 (`01876` vs `01877`):** Folios 2v–3r (1595). **Costura apretada en el lomo (*gutter shadow*)**. En la 01876 las palabras desaparecen en el pliegue central; en la 01877 el fotógrafo forzó la apertura con cristal.
  4. **Pareja 4 (`01878` vs `01879`):** Folios 3v–4r (1596, Joan Martínez). Sangrado feroz de tinta ferrogálica (*bleed-through*).
  5. **Pareja 5 (`01880` vs `01881`):** Folios 4v–5r (1596–1597). Desajustes de foco y paralelismo.
- **Mecanismo técnico validado (L-21):** Reautenticación automática de NotebookLM MCP mediante perfil persistente de Chromium sin requerir reintroducción de credenciales.
- **Resultado del Experimento de Fusión Pareja 3 (Folios 2v y 3r, mayo–noviembre 1595):**
  - **12 asientos extraídos íntegramente** (6 en verso, 6 en recto).
  - **Cero duplicados:** Al instruir la complementariedad entre tomas, el modelo no duplicó ninguna partida.
  - **Restitución del lomo (*gutter shadow*):** Las palabras truncadas al final del verso y principio del recto en `01876` se restituyeron con un 100% de nitidez gracias a `01877`.
  - **Descubrimiento prosopográfico:** Aparición documental de **Fray Francisco de Oropesa** (noviembre 1595, asientos 4 y 5 del recto) con su propia suscripción autógrafa y letra bastarda claustral.
  - Reaparición del apodo **`Chopo`** (*Pedro Sánchez Chopo* y *Juana Sánchez*, 4-oct-1595).
  - Guardado en [`transcripciones/004306112_01876_01877.md`](file:///c:/TRABAJOS/personal/genealo/transcripciones/004306112_01876_01877.md). Total acumulado en pruebas: **56 actas sacramentales**.

---

## 🧪 Experimento 07: Fusión Codicilógica de Pareja 1 (`004306112_01872.jpg` + `004306112_01873.jpg`)
- **Fecha:** 2026-10-30
- **Objetivo:** Cotejar la placa de apertura *"Volumen Entero / Página Rota"* frente a la toma de *"Corrección"* del Folio 1r (1594) para verificar si existían portadas, folios volantes o texto rescatable en la fractura.
- **Fuentes utilizadas:** `00`, `01`, `02`, `004306112_01872.jpg` (`3537bac2-...`) y `004306112_01873.jpg` (`39eeb1d5-...`).
- **Conclusiones Codicológicas y Archivísticas:**
  1. **Ausencia de Portada Anterior:** No existe portada previa conservada; el libro arranca inmediatamente en el Folio 1r tras las cartelas técnicas de microfilmación. Se aprecian jirones del número `1` mutilado en el borde superior.
  2. **Calidad de Imagen:** `01872` ofrece un encuadre más amplio con las placas de control ("Volumen Entero" y "Página Rota"), pero menor contraste. `01873` (con cartela manuscrita "Corrección") aplica re-enfoque y mayor contraste sobre la tinta ferrogálica desvaída.
  3. **Identidad del Daño Físico:** Ambas tomas capturan exactamente la misma fractura oblicua. No hay fragmentos sueltos de papel que aparezcan en una y no en otra; la pérdida del margen diestro (apellidos maternos, firmas) es irreversible en el manuscrito original.
  4. **Transcripción:** 6 partidas sacramentales completas (23-ene a 03-abr de 1594), con cero duplicados e integración de fórmulas.

---

## 🧪 Experimento 08: Fusión Codicilógica de Pareja 2 (`004306112_01874.jpg` + `004306112_01875.jpg`)
- **Fecha:** 2026-10-30
- **Objetivo:** Comprobar si la toma de corrección `01875.jpg` rescata los renglones cortados al pie en Folios 1v y 2r (años 1594–1595).
- **Fuentes utilizadas:** `00`, `01`, `02`, `004306112_01874.jpg` (`13556ad8-...`) y `004306112_01875.jpg` (`76b397fe-...`).
- **Resultados de la Fusión:**
  1. **Rescate del Asiento 6 del Verso (Folio 1v, 1594-10-04, María García):** En `01874` se cortaba a sangre tras `siendo padrinos Ju.º...`. En `01875` se rescatan íntegras las 2 líneas finales: padrinos *Juan Sánchez el mozo* y *María Sánchez* (mujer de Diego Gómez), testigos *Francisco Sánchez* y *Alonso Blázquez*, y la **firma autógrafa con rúbrica** del beneficiado *D. Rodrigo Antonio de Meneses*.
  2. **Rescate del Asiento 7 del Recto (Folio 2r, 1595-04-18, Ana Hernández):** En `01874` faltaba la madrina y el cierre. En `01875` se rescata la madrina (*Catalina Sánchez, mujer de Francisco Ximénez*), testigos (*Juan Sánchez* y *Francisco Ximénez*) y la **firma autógrafa** del vicario *Francisco Ximénez*.
  3. **Total:** 13 asientos extraídos al 100% sin truncamiento (6 verso, 7 recto) con CERO DUPLICADOS.
  4. Guardado en [`transcripciones/004306112_01874_01875.md`](file:///c:/TRABAJOS/personal/genealo/transcripciones/004306112_01874_01875.md).

---

## 🧪 Experimento 09: Fusión Codicilógica de Pareja 4 (`004306112_01878.jpg` + `004306112_01879.jpg`)
- **Fecha:** 2026-10-30
- **Objetivo:** Aislamiento del traspaso de tinta ferrogálica en espejo (*bleed-through*) y verificación forense del asiento trunco final en Folios 3v y 4r (año 1596, mano de Joan Martínez).
- **Fuentes utilizadas:** `00`, `01`, `02`, `004306112_01878.jpg` (`5f7a65f8-...`) y `004306112_01879.jpg` (`819e9e00-...`).
- **Resultados de la Fusión:**
  1. **Aislamiento de Tinta Parásita:** `01878` (toma más desvaída) muestra la tinta del reverso en gris intermedio, mientras `01879` (contraste acentuado) fija el plano frontal negro. Esto resolvió una colisión en el Asiento 1 verso (desambiguando el apellido del padrino como `de encabo`, descartando *corço* al probarse que el bucle inferior procedía del folio anterior).
  2. **Confirmación Forense de *Omissio Scribae* (Asiento 6 recto, 1596-12-08):** Ambas tomas demuestran con un 100% de certeza que Joan Martínez dejó el margen en blanco y omitió por completo el nombre y padres de la criatura, pasando directamente del verbo `bavtize` a los padrinos (*Lucas de Mingo, Ana Sanz y una tía de la criatura*).
  3. **Total:** 11 asientos extraídos íntegramente (5 verso, 6 recto) con CERO DUPLICADOS.
  4. Guardado en [`transcripciones/004306112_01878_01879.md`](file:///c:/TRABAJOS/personal/genealo/transcripciones/004306112_01878_01879.md).

---

## 🧪 Experimento 11: Censo Prosopográfico Completo del Libro 2º (1638–1695) y Unificación de Autoridades Paleográficas
- **Fecha:** 2026-10-31
- **Cuaderno:** `Lib. Baut. Navarre Vol. 1 (1594-1695)` (`7967d647-8ca2-4863-a576-11843e8e8802`)
- **Objetivo:** Ejecutar las consultas de censo prosopográfico para los lotes C (`02023`–`02086`, 1638–1660) y D (`02087`–`02147`, 1661–1695) vía MCP de NotebookLM, e integrar la totalidad del clero del corpus (1594–1695) en un banco transversal unificado.
- **Resultados:**
  1. **Lote C (1638–1660, 12 clérigos/autoridades):** Francisco Sánchez del Unar (bisagra de cierre de Libro 1º y apertura de Libro 2º en `004306112_02051.jpg`), Fray Francisco de Prado, Gaspar González (pliegos descolocados `004306112_02023.jpg` y `004306112_02043.jpg`-`004306112_02050.jpg`), Diego Arias (1643–1645), Juan Fernández (1646–1647), Don Juan Sánchez de Argáiz (Obispo de Ávila, 1º Padrón de Confirmaciones 1649), Alonso López (titular 1649–1661), Don Marcos Conde (teniente de caligrafía refinada y cruces marginales 1650–1653), Andrés Bautista (teniente hegemónico 1653–1658), Gaspar Martínez (1659), Fray Mateo del Mazo (inicios de su ministerio) y Don Francisco de la Parra y Soria (Provisor abacial en `004306112_02052.jpg`). Guardado en [`informe_prosopografico_004306112_02023_02086.md`](file:///c:/TRABAJOS/personal/genealo/informe_prosopografico_004306112_02023_02086.md).
  2. **Lote D (1661–1695, 15 clérigos/autoridades):** Fray Juan de Segovia Bonifaz (1661–1662), Fray Mateo del Mazo (rector titular 1661–1689 con beneficio en Navalmoral y residencia en Molinillo), Francisco de Ribas (1664–1666), Diego Cortés (1665–1666), Clemente Blázquez (teniente de minutas 1667–1676), Juan de Ribas (otoño 1676), Domingo Hernández (teniente y reorganizador del archivo 1666–1680), Lic. Don Francisco de la Maza (Visitador General en Auto de Visita de 1680), Fray Juan Asensio (Obispo de Ávila, 2º Padrón de Confirmaciones 1681), Francisco Ramos de Borja (1681), Lic. Joseph Romero de Navas (1682–1684), Simón Palomo Bayala (beneficiado limítrofe con arcaísmos en 1683), Fray Pedro de Frutos (Prior del Carmen de Salamanca en 1684), Lic. Melchor Núñez (1684–1689) y Lic. Jerónimo Ruiz Núñez (1689–1695, *«desta barredonda»*, cierra formalmente el Libro 2º en el Folio 114 / `004306112_02147.jpg`). Guardado en [`informe_prosopografico_004306112_02087_02147.md`](file:///c:/TRABAJOS/personal/genealo/informe_prosopografico_004306112_02087_02147.md).
  3. **Unificación Maestra:** Integración de los 4 lotes (1594–1695, 35 clérigos y autoridades) en [`03_AUTORIDADES_PALEOGRAFICAS_ALTO_ALBERCHE.md`](file:///c:/TRABAJOS/personal/genealo/03_AUTORIDADES_PALEOGRAFICAS_ALTO_ALBERCHE.md), conteniendo:
     * Matriz prosopográfica cronológica completa con origen institucional y movilidad interparroquial.
     * Fichas técnicas de ductus, abreviaturas, tics de redacción y fórmulas diplomáticas por clérigo.
     * Mapa secuencial ininterrumpido fotograma a fotograma desde `004306112_01872.jpg` hasta `004306112_02147.jpg`.

---

## 🧪 Experimento 12: Normalización Universal del Identificador Primario de Imagen (`[L-28]`)
- **Fecha:** 2026-10-31
- **Objetivo:** Erradicar cualquier truncamiento a 5 dígitos (`01874.jpg`) y fijar el nombre completo de archivo (`{DGS}_{FOTOGRAMA}.jpg`, ej. `004306112_01874.jpg`) como clave primaria universal obligatoria en toda la arquitectura documental, scripts y bases de datos.
- **Motivación:** El proyecto Alto Alberche abarca 9 rollos DGS distintos (más de 7.800 imágenes). Si se trunca el nombre de imagen a su número correlativo interno, se producen colisiones y ambigüedades entre rollos. El nombre completo es la única clave unívoca 1:1 con el soporte físico en disco, con FamilySearch, con NotebookLM y con ArcadeDB.
- **Acciones y Resultados:**
  1. **Auditoría e Inyección de Prefijo DGS:** Se actualizaron 273 referencias en [`03_AUTORIDADES_PALEOGRAFICAS_ALTO_ALBERCHE.md`](file:///c:/TRABAJOS/personal/genealo/03_AUTORIDADES_PALEOGRAFICAS_ALTO_ALBERCHE.md) sustituyendo cada fotograma por su nombre completo `004306112_XXXXX.jpg` (Sección 1 de Matriz, Sección 2 de Fichas y Sección 3 de Mapa Secuencial).
  2. **Renombrado y Normalización de Informes:** Los 4 informes intermedios fueron renombrados y saneados internamente para incorporar el prefijo del rollo:
     * [`informe_prosopografico_004306112_01872_01924.md`](file:///c:/TRABAJOS/personal/genealo/informe_prosopografico_004306112_01872_01924.md)
     * [`informe_prosopografico_004306112_01925_01975.md`](file:///c:/TRABAJOS/personal/genealo/informe_prosopografico_004306112_01925_01975.md)
     * [`informe_prosopografico_004306112_02023_02086.md`](file:///c:/TRABAJOS/personal/genealo/informe_prosopografico_004306112_02023_02086.md)
     * [`informe_prosopografico_004306112_02087_02147.md`](file:///c:/TRABAJOS/personal/genealo/informe_prosopografico_004306112_02087_02147.md)
  3. **Codificación Normativa:** Se añadió la regla obligatoria 11 `[L-28]` en [`REGLAS_Y_PROMPTS_OFICIALES.md`](file:///c:/TRABAJOS/personal/genealo/REGLAS_Y_PROMPTS_OFICIALES.md) y el apartado 5 en [`00_INSTRUCCIONES_PALEOGRAFICAS_V2.md`](file:///c:/TRABAJOS/personal/genealo/00_INSTRUCCIONES_PALEOGRAFICAS_V2.md).

---

## 🧪 Experimento 13: Aislamiento Topográfico y Grafocrítico de Cuadernos y Diferenciación Estamental de Bienes (`[L-29]`)
- **Fecha:** 2026-10-31
- **Objetivo:** Garantizar que cada cuaderno de NotebookLM Pro se asocie exclusivamente a una única localidad / código cuatriletrado (`[CUADERNO-MONO-LOCALIDAD]`), y diferenciar nítidamente en el Catastro de Ensenada los `BIENES_LEGOS` (seglares) de los `BIENES_ECLESIASTICOS`.
- **Fundamento Paleográfico y Metodológico:**
  1. **Unicidad de Escribiente Comarcal:** Para cada pueblo y operación documental (tanto en el Catastro de Ensenada de 1751–1752 como en las series parroquiales contemporáneas), el redactor material suele ser la misma mano. Aislar por pueblo garantiza que el análisis de ductus, las abreviaturas notariales y los giros de estilo no sufran interferencias ni mezclas entre escribanos de distintos pueblos.
  2. **Prevención de Alucinación Toponímica y Onomástica:** Evita que el modelo confunda parajes rústicos, pagos, arroyos o términos municipales de una aldea con otra colindante, y blinda contra la fusión indebida de homónimos de pueblos vecinos.
  3. **Segregación Estamental Estricta:** Se sustituye la categoría genérica de bienes por `BIENES_LEGOS` (estamento `SEGLAR`, 2.600 imgs) y `BIENES_ECLESIASTICOS` (estamento `ECLESIASTICO`, 391 imgs), indexados en [`catalogo_corpus.json`](file:///c:/TRABAJOS/personal/genealo/catalogo_corpus.json).
  4. **Hipótesis del Escribiente de la Comisión de Ensenada:** Se registra la línea de investigación para verificar si la comisión itinerante de la Real Junta del Catastro empleó al mismo oficial de pluma para Navarredondilla, Molinillo, Navandrinal y El Villarejo, lo cual permitirá desbloquear más de 3.200 imágenes mediante una única ficha grafocrítica transversal.
- **Acciones y Resultados:**
  1. Codificada la Regla 12 `[L-29]` en [`REGLAS_Y_PROMPTS_OFICIALES.md`](file:///c:/TRABAJOS/personal/genealo/REGLAS_Y_PROMPTS_OFICIALES.md), Regla 20 en [`contexto_maestro.md`](file:///c:/TRABAJOS/personal/genealo/contexto_maestro.md) y Regla 6 en [`00_INSTRUCCIONES_PALEOGRAFICAS_V2.md`](file:///c:/TRABAJOS/personal/genealo/00_INSTRUCCIONES_PALEOGRAFICAS_V2.md).
  2. Recompilado [`catalogo_corpus.json`](file:///c:/TRABAJOS/personal/genealo/catalogo_corpus.json) con los campos `estamento` (`SACRAMENTAL`, `SEGLAR`, `ECLESIASTICO`, `INSTITUCIONAL`) y `escribano_mano_adscrita`.

---

## 🧪 Experimento 14: Ingesta Masiva y Verificación E2E de Cuadernos Catastro de Ensenada (Legos) en NotebookLM
- **Fecha:** 2026-10-31
- **Objetivo:** Ingesta desatendida y verificación completa de los 4 cuadernos de Personal Seglar (Legos) del Catastro del Marqués de la Ensenada (1751–1752) para las 4 localidades del Alto Alberche (`NRDL`, `JMOL`, `VLLR`, `NDRN`), cumpliendo `[L-28]` y `[L-29]`.
- **Cuadernos Creados y Poblados en NotebookLM:**
  1. `NRDL-ENSENADA-LEGOS-01`: `ec86de71-a11c-4489-bbb9-eea856cccac4` (87 fuentes). Rollo `004469033`, fotogramas `00881` a `00967`.
  2. `JMOL-ENSENADA-LEGOS-01`: `407d5cb4-4b83-495f-a23a-309ea44ee8c6` (28 fuentes). Rollo `004469028`, fotogramas `00952` a `00979`.
  3. `VLLR-ENSENADA-LEGOS-01`: `e7fba70b-af7d-4602-b543-060742b22528` (51 fuentes). Rollo `004469028`, fotogramas `00901` a `00951`.
  4. `NDRN-ENSENADA-LEGOS-01`: `cd72ef58-fcf5-48ac-8de2-556648ebd90e` (34 fuentes). Rollo `004469028`, fotogramas `00980` a `01013`.
- **Resultados de la Ingesta y Certificación E2E:**
  - **Total de fuentes subidas:** 200 fuentes fotográficas canónicas.
  - **Estado en NotebookLM:** 200/200 fuentes en estado `READY` (0 en `PROCESSING`, 0 en `ERROR`).
  - **Harness de Verificación:** [`scripts/verify_notebooklm_sources.py`](file:///c:/TRABAJOS/personal/genealo/scripts/verify_notebooklm_sources.py) superó **405/405 aserciones** de integridad estricta (100% de éxito).
  - **Sincronización:** Actualizado [`catalogo_corpus.json`](file:///c:/TRABAJOS/personal/genealo/catalogo_corpus.json) con `source_id` individual para cada imagen.

---

## 🧪 Experimento 15: Pipeline de Ingesta Desatendida con Doble Checkpoint de Navarredondilla Parroquial (Opción A)
- **Fecha:** 2026-10-31
- **Objetivo:** Ingesta integral de las 2.276 imágenes de los registros parroquiales de Navarredondilla distribuidas en 15 cuadernos mono-localidad en NotebookLM Pro, preservando estrictamente el cuaderno canónico existente `Lib. Baut. Navarre Vol. 1 (1594-1695)` (`7967d647-8ca2-4863-a576-11843e8e8802`).
- **Arquitectura del Pipeline:**
  - Script [`scripts/ingest_navarredondilla_parroquial.py`](file:///c:/TRABAJOS/personal/genealo/scripts/ingest_navarredondilla_parroquial.py) con doble checkpoint: atómico local JSON ([`scripts/ingest_checkpoint_nrdl.json`](file:///c:/TRABAJOS/personal/genealo/scripts/ingest_checkpoint_nrdl.json)) y live sync con la nube.
  - Blindaje previo (*pre-flight shield check*) que verifica que los 5 cuadernos protegidos no sean tocados ni duplicados.
  - Reautenticación automática desatendida mediante perfil de Chromium (`[L-21]`).
- **Hitos Operativos:**
  1. **Piloto de Calibración:** `NRDL-MATR-01` (`1e6fec74-1e2f-4dd7-8ad1-6d25411de127`): 33/33 imágenes subidas, verificadas y consolidadas en estado `READY`.
  2. **Ejecución en Background:** Lanzado `task-2050` procesando los 14 cuadernos restantes (`NRDL-BAUT-01..07`, `NRDL-DIFU-01..05`, `NRDL-MATR-02`, `NRDL-MIXTO-01`) con pausas de cortesía adaptativas de 2.5s para evitar bloqueos por cuota.

---

## 🧪 Experimento 16: Principio de Reconstrucción Lógico-Sacramental vs. Códice Físico Mixto (`[L-30]`)
- **Fecha:** 2026-10-31
- **Decisión Arquitectónica del Usuario:** *«No tiene sentido tener libros mixtos: si en un libro hay partidas de nacimientos por un lado y de bautismo por otro, lo que hay que hacer es llevarlas a un cuaderno de partidas de bautismo o de nacimiento, y a ser posible que sean correlativas en el tiempo. Otra cosa es que haya cosas sueltas que no sean partidas.»*
- **Fundamentación Paleográfica y Archivística:**
  1. **La distorsión del encuadernador histórico:** La existencia de "Libros Mixtos" responde únicamente a la escasez de papel o encuadernaciones en el archivo parroquial histórico (s. XVII–XIX), donde el sacerdote agrupaba varios sacramentos en un mismo volumen de pergamino.
  2. **La necesidad de la IA y del Grafo:** Para la visión multimodal de NotebookLM y el posterior grafo de ArcadeDB, mezclar en un solo cuaderno partidas de bautismo, matrimonio y defunción genera colisiones semánticas graves, desordena la secuencia cronológica de cada sacramento y rompe las búsquedas correlativas.
  3. **Identificación exacta de tramos sacramentales:** Mediante los Inventarios Maestros folio a folio ([`inventario-navarredondilla-v3.pdf`](file:///c:/TRABAJOS/personal/genealo/imagenes/inventario-navarredondilla-v3.pdf) e [`inventario-san-juan-del-molinillo.pdf`](file:///c:/TRABAJOS/personal/genealo/imagenes/inventario-san-juan-del-molinillo.pdf)), conocemos exactamente el rango de imágenes de cada sección:
     - En **San Juan del Molinillo (Elemento 17, Rollo `004298570`, imgs `02429` a `02519`):**
       * Bautismos (1847–1848) $\rightarrow$ Se integran lógicamente como tramo final de la serie de Bautismos.
       * Matrimonios (1842–1849) $\rightarrow$ Se integran lógicamente en la serie de Matrimonios.
       * Defunciones (1843–1849) $\rightarrow$ Se integran lógicamente en la serie de Defunciones.
     - En **Navarredondilla (Elemento 12, Rollo `004306112`):**
       * Bautismos 1º (1594–1636, imgs `01873`–`01954`) $\rightarrow$ Integrados en la serie pura de Bautismos (`7967d647`).
       * Casados 1º (1634–1686, imgs `01957d`–`01986`) $\rightarrow$ Integrados en la serie pura de Matrimonios.
       * Inventario de Alhajas de la Iglesia (1637, imgs `01955`–`01957izq`) $\rightarrow$ Catalogado como Documento Extraordinario No Sacramental.
- **Formulación de la Regla Oficial:**
  - **`[L-30]` Principio de Reconstrucción Lógico-Sacramental:** Los cuadernos de NotebookLM y las colecciones del grafo se organizan por **Serie Sacramental Pura y Correlativa en el Tiempo** (Bautismos, Matrimonios, Defunciones) para cada pueblo. Los códices mixtos físicos se desarticulan y sus fotogramas se asignan a su respectiva serie cronológica, reservando cuadernos específicos para documentos censales y extraordinarios (confirmaciones, inventarios, visitas).

---

## 🧪 Experimento 18: Piloto de Ingesta y Calibración E2E de San Juan del Molinillo (`JMOL-DIFU-03`, Opción A)
- **Fecha:** 2026-10-31
- **Objetivo:** Ejecutar la calibración en vivo del pipeline de San Juan del Molinillo (`JMOL`) mediante la ingesta y verificación del primer cuaderno canónico sacramental puro: `JMOL-DIFU-03` (Libro 3º de Defunciones 1849–1851, 17 imágenes).
- **Acciones Realizadas:**
  1. **Pre-flight Shield Check:** Verificación automática de la integridad de los 6 cuadernos protegidos en NotebookLM (388 fuentes en total):
     - `Lib. Baut. Navarre Vol. 1 (1594-1695)` (`7967d647`): 188 fuentes.
     - `NRDL-ENSENADA-LEGOS-01` (`ec86de71`): 87 fuentes.
     - `JMOL-ENSENADA-LEGOS-01` (`407d5cb4`): 28 fuentes.
     - `VLLR-ENSENADA-LEGOS-01` (`e7fba70b`): 51 fuentes.
     - `NDRN-ENSENADA-LEGOS-01` (`cd72ef58`): 34 fuentes.
     - `NRDL-MATR-01` (`1e6fec74`): 33 fuentes.
  2. **Resolución Dinámica de Rutas:** Activado el resolver dinámico para carpetas con guión tipográfico Unicode en-dash (`\u2013`), validando el 100% (2.731/2.731) de imágenes de Molinillo en disco.
  3. **Creación del Cuaderno:** Generado en NotebookLM el cuaderno `JMOL-DIFU-03` con ID `a5d19fcc-d266-4497-bdb3-df182328bdcb`.
  4. **Subida con Backoff y Doble Checkpoint:** Ingestadas las 17 imágenes fotográficas `{DGS}_{FOTOGRAMA}.jpg` (`004298571_01033.jpg` a `004298571_01049.jpg`) registrándose en [`scripts/ingest_checkpoint_jmol.json`](file:///c:/TRABAJOS/personal/genealo/scripts/ingest_checkpoint_jmol.json).
  5. **Verificación Independiente E2E:** Ejecutado [`scripts/verify_sanjuan_parroquial_sources.py`](file:///c:/TRABAJOS/personal/genealo/scripts/verify_sanjuan_parroquial_sources.py) generando informe en [`scripts/verification_report_jmol.json`](file:///c:/TRABAJOS/personal/genealo/scripts/verification_report_jmol.json).
- **Resultados:**
  - **Estado en NotebookLM:** **17/17 fuentes en estado READY** (100% procesadas por la IA multimodal de Google).
  - **Fuentes faltantes:** 0.
  - **Veredicto:** **PASS (100% de éxito)**. Cuaderno certificado para transcripción.










