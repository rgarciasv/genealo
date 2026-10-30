# CONTEXTO MAESTRO: PROYECTO DE I+D GENEALÓGICO ALTO ALBERCHE

> **FUENTE ÚNICA DE VERDAD (ÍNDICE DOCUMENTAL DEL PROYECTO):**
> Para evitar dispersión de reglas entre conversaciones, todo el conocimiento del proyecto está centralizado en estos 7 archivos maestros en `c:\TRABAJOS\personal\genealo\`:
> 1. [`contexto_maestro.md`](file:///c:/TRABAJOS/personal/genealo/contexto_maestro.md) *(Este documento)*: Visión general, arquitectura y reglas de oro del sistema.
> 2. [`TODO.md`](file:///c:/TRABAJOS/personal/genealo/TODO.md): Inventario completo auditado de los **7.868 archivos** de imagen (rollos DGS) y estado de avance por fases.
> 3. [`BITACORA_EXPERIMENTOS.md`](file:///c:/TRABAJOS/personal/genealo/BITACORA_EXPERIMENTOS.md): Registro histórico de todas las pruebas hechas en NotebookLM, los fallos cazados (`L-01` a `L-25`) y qué regla soluciona cada fallo.
> 4. [`REGLAS_Y_PROMPTS_OFICIALES.md`](file:///c:/TRABAJOS/personal/genealo/REGLAS_Y_PROMPTS_OFICIALES.md): Versión oficial vigente (`v2.0`) del System Prompt (`chat_configure`), instrucciones paleográficas (`00_INSTRUCCIONES_PALEOGRAFICAS_V2.md`), Prompt de Extracción por Folio (`chat.ask`), formatos polimórficos (`PADRON_CONFIRMACION`, `AUTO_VISITA`, `INDICE_PARROQUIAL`, `MINUTA_SACRISTIA`) e ID canónico universal.
> 5. [`01_DICCIONARIO_ANCLAJE_NAVARREDONDILLA.md`](file:///c:/TRABAJOS/personal/genealo/01_DICCIONARIO_ANCLAJE_NAVARREDONDILLA.md): Candado cronológico (con todos los saltos de encuadernación), diccionario de lugares de mundo cerrado y vocabulario onomástico local (nombres, apellidos, apodos y fórmulas vecinales).
> 6. [`03_AUTORIDADES_PALEOGRAFICAS_ALTO_ALBERCHE.md`](file:///c:/TRABAJOS/personal/genealo/03_AUTORIDADES_PALEOGRAFICAS_ALTO_ALBERCHE.md): Banco transversal de escribanos, ductus, abreviaturas, tics de redacción y firmas autógrafas (1594–1683).
> 7. [`04_JURISDICCIONES_Y_DEPENDENCIAS_PARROQUIALES.md`](file:///c:/TRABAJOS/personal/genealo/04_JURISDICCIONES_Y_DEPENDENCIAS_PARROQUIALES.md): Códigos cuatriletrados unívocos, dependencia de Molinillo respecto a Navalmoral pre-1715, arranque de series, lagunas y libros bífidos/paralelos.

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
11. **`[L-20]` Protocolo de Fusión de Tomas Hermanas (Base vs. Corrección):** Las tomas duplicadas de FamilySearch (`01872/01873`, `01874/01875`, `01876/01877`, `01878/01879`, `01880/01881`) se envían de forma complementaria para rescatar texto perdido en lomos apretados y pies cortados, produciendo un único registro depurado con CERO DUPLICADOS.
12. **`[L-21]` Reautenticación Desatendida de NotebookLM MCP:** Renovación automática de credenciales mediante el perfil persistente de Chromium sin requerir intervención manual del usuario.
13. **`[L-22]` Transversalidad del Ductus Eclesiástico (Desacoplamiento Libro-Escribano):** La mano y los tics de un cura no cambian entre bautismos, matrimonios y entierros. Las fichas técnicas de caligrafía residen de forma centralizada en [`03_AUTORIDADES_PALEOGRAFICAS_ALTO_ALBERCHE.md`](file:///c:/TRABAJOS/personal/genealo/03_AUTORIDADES_PALEOGRAFICAS_ALTO_ALBERCHE.md).
14. **`[L-23]` Extracción Polimórfica Obligatoria:** Tratamiento estructurado y riguroso de documentos no sacramentales presentes en los libros: padrones de confirmaciones (`PADRON_CONFIRMACION`), decretos de visitas pastorales (`AUTO_VISITA`), índices alfabéticos (`INDICE_PARROQUIAL`) y minutas de sacristía (`MINUTA_SACRISTIA`).
15. **`[L-24]` Estándar Geográfico Cuatriletrado y Redirección Canónica Pre-1715:** Sustitución de `NAVA-` por `NRDL`, `NMRL`, `NCRZ`, `JMOL`, `NDRN`, `VLLR`, `BHND`. Redirección obligatoria de las búsquedas genealógicas de Molinillo y anejos anteriores a 1715 hacia Navalmoral de la Sierra (`NMRL`) y Navarredondilla (`NRDL`).
16. **`[L-25]` Protocolo de Trazabilidad Total y Tratamiento de Partidas Bipartitas (Split Acts):** Las partidas que arrancan al pie de una plana y concluyen en la siguiente (intra-imagen verso $\rightarrow$ recto, o inter-imagen recto $N \rightarrow$ verso $N+1$) se restituyen sin pérdida de padrinos ni firmas, vinculando mitades con marcadores direccionales.
17. **`[L-26]` Modelo de Identificación en Dos Capas (PK Física Inmutable + Cita Archivística + Metadato ARK):** Separación tajante entre la **clave primaria física de base de datos** (`{DGS}_{FOTOGRAMA}_{CARA}_{ASIENTO}`, ej. `004306112_01874_L_01`, matemática e inmutable) y el **foliado manuscrito / ID archivístico** (`ES-AV-NRDL-BAUT-L01-F001V-A01`, descriptivo y revisable). Se incorpora el metadato digital persistente **URL ARK de FamilySearch** (`https://www.familysearch.org/ark:/61903/3:1:...`) a nivel de imagen y de asiento para citas permanentes.

---

## 3. CATÁLOGO OFICIAL DE CUADERNOS EN NOTEBOOKLM (ACCESO VÍA MCP `notebooklm`)
> **Convención de Nombres Obligatoria:** Llamar siempre a cada cuaderno por su título oficial o descriptor exacto (nunca usar términos ambiguos como *"el primer cuaderno"* o *"el segundo cuaderno"*).

| Nº | Título Oficial del Cuaderno | ID en NotebookLM (`notebook_id`) | Fuentes | Contenido y Estado |
| :-: | :--- | :--- | :-: | :--- |
| **1** | **`Lib. Baut. Navarre Vol. 1 (1594-1695)`** | `7967d647-8ca2-4863-a576-11843e8e8802` | 188 | **Cuaderno principal saneado de Bautismos de Navarredondilla (1594–1695, DGS 004306112).** 183 imágenes únicas + 5 fuentes maestras (`00`, `01`, `02`, `03`, `04`). Configurado `chat_configure` con System Prompt oficial. |
| **2** | **`libro bautismos navarre 1594-1637`** | `d28c82d0-e15f-4d4d-8333-61f529d52815` | 91 | Cuaderno experimental inicial (nombres antiguos `S3HT-...jpg`). Auditados sus 20 turnos de chat y 3 artefactos Studio (`L-01` a `L-09`). |
| **3** | **`matrimonio navarre 1698-1761`** | `b973ffbb-0097-4b1b-a518-25aefd9a46c9` | 79 | Libro de Matrimonios de Navarredondilla (1698–1761). Pendiente de auditoría. |
| **4** | **`Libro personas ensenada Navarredondilla`** | `d634b10e-386d-4397-96d1-d271eb71a70d` | 91 | Catastro del Marqués de la Ensenada (1752) de Navarredondilla. |
| **5** | **`Libro de Bautismos de San Juan del Molinillo 1752 1852`** | `ac46f1ed-b0b8-4009-9a62-404171fb0281` | 72 | Bautismos de San Juan del Molinillo y anejos (1752–1852). |
| **6** | **`Libro parroquial matrimonios SJDM sept 1716 dic 1756`** | `af65bd4d-5a95-4a08-80b2-cec3180904fd` | 95 | Matrimonios de San Juan del Molinillo (1716–1756). |
| **7** | **`libros parroquiales matrimonios SJDM desde dic 1756 hasta 1789`** | `fa440cab-c682-4c86-8be2-78dacc042daf` | 92 | Matrimonios de San Juan del Molinillo (1756–1789). |
| **8** | **`Descripcion de la Provincia y Obispado de Avila`** | `528907f8-b1f2-42eb-8a9a-622e279a8bbb` | 49 | Contexto histórico y geográfico diocesano de Ávila. |
| **9** | **`inventario libros y scripts`** | `7ff7fe9a-5237-42e8-81bb-b68d4491cb77` | 2 | Contiene `Script JavaScript para FamilySearch.pdf` (source `39371fd4-7475-4882-8b1d-d1d2e411db4f`, 1.441.899 chars) con la auditoría visual fotograma a fotograma de los rollos de San Juan del Molinillo y Navarredondilla. |
| **10** | **`Navarredondilla Parish Records Inventory`** | `a6737bbe-26c8-4203-b9c2-d0ea6117241b` | 1 | Primera mitad de la auditoría de rollos (`64a6c118-fc30-45aa-a5ef-7b3dc3ba260e`, 617.528 chars). |

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

