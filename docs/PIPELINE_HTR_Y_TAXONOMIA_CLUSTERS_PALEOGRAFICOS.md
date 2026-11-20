# ARQUITECTURA DE PIPELINES HTR, TAXONOMÍA MORFOGRÁFICA Y CONTROL ECDÓTICO-UNICODE

**Proyecto:** Digitalización, Ecdótica y Reconstrucción Genealógica del Alto Alberche  
**Materia:** Flujos de Trabajo HTR (Kraken / eScriptorium / Gemini Pro / VLM), Taxonomía de 12 Clústeres Paleográficos, Esquema de Layout DLA y Control de Calidad Unicode  
**Estado:** Documento Técnico de Referencia  

---

## 2. FLUJOS DE TRABAJO POSIBLES (PIPELINES)

### Flujo A: Generación asistida de ground truth (Kraken + Python + Gemini Pro)
> [!IMPORTANT]
> Gemini nunca debe generar el PAGE-XML ni sus coordenadas desde cero; la geometría la aporta Kraken/eScriptorium y Gemini solo rellena el texto de cada línea.

Existen dos variantes según el punto de intervención manual:

#### Variante A1 (eScriptorium primero — máxima limpieza):
1. Subir dobles páginas a eScriptorium y ejecutar el segmentador de TRIDIS.
2. Corregir manualmente las regiones semánticas y las baselines problemáticas (sin editar las máscaras poligonales a mano).
3. Exportar PAGE-XML vacío de texto.
4. **Script en Python:** Recorre cada `<TextLine>` por su ID, recorta la imagen a resolución nativa usando `<Coords>` con enmascaramiento de fondo y envía el recorte a Gemini Pro vía API.
5. Inyectar las respuestas en `<TextEquiv><Unicode>`, validar el inventario Unicode con `choco-mufin` y reimportar el PAGE-XML en eScriptorium para revisión rápida de líneas dudosas.

#### Variante A2 (CLI primero — menos fricción):
1. **Segmentar en lote por consola:**
   ```bash
   kraken -i imagen.jpg imagen.xml segment -bl -i modelo_seg_tridis.mlmodel
   ```
2. **Auditoría visual rápida sin abrir eScriptorium:** Generar imágenes de comprobación (overlays en Python con baselines en rojo y regiones en azul) y retocar solo los folios con fallos usando `nw-page-editor` (editor local ligero) o `Aletheia`.
3. Ejecutar el script de recorte + API de Gemini Pro + inyección en PAGE-XML + validación Unicode, y hacer una única pasada de revisión humana al final.

---

### Flujo B: Entrenamiento en Kraken (Segmentación y HTR)

#### 1. Segmentador propio (`ketos segtrain`):
* Ajustar el modelo de segmentación de TRIDIS (o `blla.mlmodel`) con 30–50 dobles páginas variadas usando `--resize both` para adaptar la capa de salida a las clases parroquiales.
* Solo importan las regiones y las baselines; las máscaras poligonales las recalcula Kraken de forma determinista (*seam carving*), permitiendo de forma natural que las máscaras se solapen cuando los caídos (`y`, `g`, `p`, `q`) cruzan a la línea inferior.

#### 2. Reconocedor HTR (`ketos train`):
* Ajuste fino sobre TRIDIS con 30–50 páginas iniciales (unas 3–4 por mano/estilo) y ciclo iterativo (*Active Learning*).
* **Parámetros obligatorios:**
  * `-u NFD` (normalización Unicode descompuesta).
  * `--augment` (clave para absorber cambios de inclinación y tamaño de un mismo escribano).
  * Parada temprana `-q early` sobre un conjunto de validación estratificado (10–15 %) que incluya todas las manos/clústeres.

#### 3. Precauciones operativas de Kraken:
* Si se aplica preprocesado de imagen (como CLAHE o aplanado de fondo), debe ser idéntico en entrenamiento e inferencia.
* Compilar el dataset a `.arrow` con `ketos compile` acelera el entrenamiento.
* Ante cortes en sesiones largas, evitar `--resume` (propenso a fallos) y reanudar convirtiendo el último checkpoint válido con `ketos convert`.

---

### Flujo C: Fine-tuning de Chandra OCR 2 (VLM con LoRA/PEFT)

1. **Script de conversión en Python de imagen + PAGE-XML a JSONL conversacional / Hugging Face Dataset:** Cada `<TextRegion>` pasa a ser un bloque de layout con su bbox (`[x1, y1, x2, y2]`) y su texto concatenado a partir de las `<TextLine>` en orden de lectura, ignorando las baselines.
2. **Recorte previo obligatorio:** No entrenar ni inferir con la doble página entera, porque el reescalado interno (*scale_to_fit*) destruye los trazos finos. Usar las coordenadas del PAGE-XML para exportar recortes por página individual (mitad izquierda / derecha) o por partida completa (`margen_indice` + `cuerpo_partida`).

---

### Flujo D: Postprocesado y reconstrucción documental

* **Orden de lectura en doble página:** Forzar ordenación espacial estricta en Python (mitad izquierda completa $\rightarrow$ mitad derecha completa) para evitar que ligeros desniveles de la fotografía intercalen regiones de ambas páginas.
* **Emparejamiento margen–partida:** Como el apunte marginal no siempre coincide con la primera línea de la partida, vincular `margen_indice` con `cuerpo_partida` buscando coincidencia aproximada del nombre dentro del cuerpo o, en su defecto, por solapamiento del punto medio vertical del polígono.
* **Partidas partidas entre páginas:** Unir el primer bloque `cuerpo_partida` de una página al último de la anterior cuando carezca de `margen_indice` asociado y de fórmula de apertura (*En...*). Excluir la región `reclamo` al concatenar para no duplicar la primera palabra de la página siguiente.

---

## 3. TIPOS DE LETRA Y TAXONOMÍA DE 12 CLÚSTERES MORFOGRÁFICOS

En un solo libro de 50 años conviven fácilmente de 6 a 10 manos distintas, y en tres municipios se superan las 60; además, un mismo cura cambia drásticamente de módulo según el espacio disponible o la pluma. Por ello, el muestreo no se organiza por individuos ni por años, sino por **12 clústeres morfográficos** basados en la geometría real del trazo:

| ID | Clúster Morfográfico | Cronología Típica | Rasgos Visuales Determinantes |
| :---: | :--- | :---: | :--- |
| **C01** | **Gótico-cortesana tardía** | 1500–1560 | Trazo anguloso y quebrado, módulo pequeño, líneas muy juntas, alta densidad de abreviaturas medievales y signos tironianos. |
| **C02** | **Procesal redonda / abierta** | 1530–1620 | Formas curvas y anchas, letras aislables pero con nexos envolventes largos. Pluma gruesa de ave. |
| **C03** | **Procesal encadenada pura** | 1560–1650 | Renglones casi sin levantar la pluma; *c, e, n, m, r, s* reducidas a ondas similares. |
| **C04** | **Humanística / Itálica libraria** | 1550–1640 | Vertical o levemente inclinada, letras sueltas casi de imprenta, limpia y sin apenas lazos. |
| **C05** | **Híbrida procesal-bastarda** | 1610–1680 | Base inclinada de bastarda con ataduras procesales, *d* unciales vueltas atrás y abreviaturas arcaicas. |
| **C06** | **Bastarda cancilleresca / magistral** | 1660–1780 | Caja redonda y uniforme, inclinación constante, renglones rectos y separación clara (ej. Domingo Galán, 1710–1711). |
| **C07** | **Bastarda angulosa / picuda** | 1680–1790 | Módulo comprimido lateralmente, picos agudos y aspecto «aserrado», enlaces rápidos (ej. Fray Francisco Martínez, 1716). |
| **C08** | **Bastarda corriente / desbordada** | 1670–1810 | Ejecución rápida y descuidada, ojales gigantescos que invaden dos renglones, renglón caído y aglutinaciones (ej. Pedro de la Rebilla, 1710). |
| **C09** | **Micro-cursiva compacta** | 1650–1830 | Letra diminuta y empastada por aprovechamiento de espacio o notas marginales (ej. Pedro de la Rebilla, 1711). |
| **C10** | **Bastarda ilustrada / neoclásica** | 1770–1840 | Pluma más fina, limpia, simplificación de abreviaturas y casi sin lazos envolventes. |
| **C11** | **Cursiva inglesa / comercial** | 1840–1899 | Plumilla metálica: ascendentes finísimos (vulnerables a mala foto) y descendentes gruesos, muy inclinada. |
| **C12** | **Rústica / senil o temblorosa** | Transversal | Trazo roto o tembloroso, manchas de goteo y formas irregulares sin escuela clara. |

### Estrategia de muestreo frente a entrenamiento

* **Muestreo equilibrado (manual o automático):** Los 12 clústeres sirven como casillas de verificación para que ninguna morfología quede subrepresentada. Como alternativa escalable antes de transcribir, se puede implementar un clustering visual automático en Python: extraer recortes de líneas de los tres municipios, calcular embeddings con un codificador visual preentrenado (CNN/ViT) y agrupar con UMAP + HDBSCAN/K-Means ($k=15\text{–}20$) para seleccionar muestras representativas de cada familia gráfica real.
* **Agrupación de motores (no entrenar 12 modelos):** Para evitar sobreajuste y fragmentación, los 12 clústeres de muestreo se entrenan agrupados en 3 o 4 motores especializados:
  * **Bloque Antiguo:** C01–C05
  * **Bloque Bastardo:** C06–C10
  * **Bloque Plumilla Metálica:** C11
  * *(Repartiendo C12 de forma transversal en todos)*  
  O bien en un único modelo provincial equilibrado. En producción, un clasificador ligero (o Gemini Flash en baja resolución) puede enrutar cada folio al motor adecuado.

---

## 4. ESQUEMA DE REGIONES SEMÁNTICAS (LAYOUT DLA)

Todas las páginas deben etiquetarse con un vocabulario cerrado de regiones, dibujando polígonos estrictamente separados para la página izquierda y la derecha en imágenes a libro abierto:

* `folio`: Numeración manuscrita de página/folio (ej. `45=`, `156`).
* `margen_indice`: Nombre del bautizado/difunto/contrayentes y número de asiento al margen.
* `margen_nota`: Añadidos posteriores de otros curas, postdatas al pie e hitos cronológicos marginales (como `Año de 1711 =`, para evitar que se mezclen con el nombre índice).
* `cuerpo_partida`: Un polígono independiente por cada asiento (ayuda al segmentador a detectar saltos entre partidas).
* `firma`: Nombre y cargo del firmante; las rúbricas ornamentales quedan siempre fuera de las baselines.
* `reclamo` y `texto_vertical` *(opcionales)*: Para aislar reclamos al pie de folio y notas marginales giradas 90°.

---

## 5. CRITERIOS DE TRANSCRIPCIÓN PALEOGRÁFICA Y CONTROL UNICODE

El criterio cerrado es **paleográfico estricto con regularización fonética mínima** solo en los tres alógrafos contextuales que alinea de forma nativa TRIDIS:

### 1. Regularizar únicamente:
* `u`/`v` según valor fonético (*Navalmoral, Nava, aver, ut supra*).
* `i`/`j` (*Juan, hija*, salvo números romanos finales como *xvij*).
* `ſ` larga $\rightarrow$ `s` estándar.

### 2. Conservar fielmente el resto:
* **Ortografía histórica:** *Bauptize, hixa, muger, dixeron, yglesia*.
* **Elisiones y uniones reales del trazo:** *alcaldy, ypor verdadlo, destas*.
* **Mayúsculas:** Solo cuando el trazo sea inequívocamente capital.
* **Puntuación visible:** `,`, `(`, `)`, `=`.
* **Latín y latinismos:** Tal como estén escritos en el folio.

### 3. Nexos y abreviaturas:
* Descomponer siempre los nexos cursivos (*de, st, is, ct*) en letras individuales (nunca usar ligaduras tipográficas como `ﬁ` o `ﬂ`).
* **No desarrollar abreviaturas:** Mantener `franᶜᵒ`, `Vᵒˢ`, `Sʳ`, `Mãn`, `q̄`.

### 4. Inventario Unicode cerrado:
* Usar solo superíndices y combinantes estándar:
  * `ª` (`U+00AA`), `º` (`U+00BA`)
  * `ᶜ` (`U+1D9C`), `ᵈ` (`U+1D48`), `ᵉ` (`U+1D49`), `ᵐ` (`U+1D50`), `ⁿ` (`U+207F`), `ʳ` (`U+02B3`), `ˢ` (`U+02E2`), `ᵗ` (`U+1D57`)
  * Macrón combinante `̄` (`U+0304`), `ç`, `ñ`, `&`.
* Si un símbolo raro aparece menos de 30–40 veces en todo el corpus, simplificarlo.
* **Validación obligatoria:** Validar siempre los XML con `choco-mufin` para detectar confusiones típicas (como el símbolo de grado `°` `U+00B0` en lugar del ordinal masculino `º` `U+00BA`).

### 5. Tachaduras e incertidumbre:
* Palabra tachada legible entre `$palabra$` (estándar de TRIDIS).
* Tachadura ilegible se omite.
* **Prohibición:** Nunca escribir `[?]`, `?` ni `[ilegible]` dentro del texto de entrenamiento: si una línea tiene manchas o trazos dudosos que no se pueden verificar con certeza, dejar su `<Unicode>` vacío para que Kraken la ignore.

---

## 6. REGLAS CRÍTICAS PARA LOS SCRIPTS DE PYTHON Y LA API DE GEMINI PRO

Las pruebas empíricas sobre las hojas de 1710–1716 demostraron que enviar la doble página completa a un VLM induce sesgo léxico y alucinaciones en nombres propios y plurales (*Theresa Encabo* por *thomasa toribio*, *de esta aldea* por *destas aldeas*, *misterios* hipercorregido a *mysterios* por el nexo cursivo *is*).

Los scripts que se construyan deben aplicar **cuatro salvaguardas obligatorias**:

1. **Recorte poligonal enmascarado a resolución nativa:**
   Extraer cada línea usando el polígono exacto `<Coords>` del PAGE-XML (nunca un bounding box rectangular simple que meta palabras de líneas vecinas), rellenar el exterior con fondo limpio y aplicar una dilatación/margen suave de 3–5 píxeles para no amputar colas ni astas. Opcionalmente, adjuntar la imagen de la región completa solo como referencia contextual de lectura.

2. **Salida JSON estructurada:**
   Exigir a la API un esquema estricto:
   ```json
   {
     "texto": "...",
     "duda": false,
     "motivo": "..."
   }
   ```
   De este modo, el texto inyectado en `<Unicode>` sale limpio y las líneas marcadas con `duda: true` pasan automáticamente a una cola de revisión humana.

3. **Prompt con lista cerrada y few-shot:**
   Incluir en el system prompt la prohibición explícita de modernizar o expandir abreviaturas, la tabla cerrada de códigos Unicode permitidos y 2–3 ejemplos reales (recorte de línea + transcripción paleográfica verificada).

4. **Glosario onomástico y toponímico local:**
   Inyectar en el contexto un listado de nombres, apellidos y localidades documentados en la comarca (ej. *Andrino, Herranz, Toribio, Thomasa, Navalmoral, Navandrinal, Villarejo, Navalsauz, Las Berlanas, Peñalba, Serranillos, La Adrada, Piedralaves*) estrictamente como ayuda de desambiguación visual, prohibiendo forzar sustituciones que contradigan el trazo.
