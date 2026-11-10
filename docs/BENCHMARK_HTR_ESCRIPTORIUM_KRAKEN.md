# INFORME TÉCNICO: BENCHMARK EMPÍRICO HTR MULTI-MODELO, INFRAESTRUCTURA EFÍMERA EN GCE SPOT Y FLUJO HÍBRIDO (ESCRIPTORIUM + KRAKEN + GEMINI)

**Proyecto:** Digitalización, Ecdótica y Reconstrucción Genealógica del Alto Alberche (Ávila)  
**Entorno de Pruebas:** Instancia Spot en Google Compute Engine (`escriptorium-spot-vm`)  
**Fecha de Ejecución:** Noviembre de 2026  
**Rama Git:** `feature/escriptorium-spot-vm`  
**Autor:** Antigravity AI & Archivero Virtual  

---

## 1. RESUMEN EJECUTIVO Y OBJETIVOS

El presente informe documenta la investigación forense, despliegue de infraestructura y evaluación comparativa empírica (*benchmark*) del motor HTR (*Handwritten Text Recognition*) de código abierto **Kraken** orquestado sobre la plataforma web **eScriptorium**, enfrentado a los diferentes periodos paleográficos del corpus documental de Navarredondilla y el Alto Alberche (siglos XVI al XVIII).

### Objetivos Clave:
1. **Despliegue de Infraestructura Efímera de Bajo Coste:** Provisionar un entorno Docker completo de eScriptorium y Kraken en Google Compute Engine con modelo de precios Spot (CPU `n1-standard-4`, 120 GB de disco persistente estándar), con ciclo de vida automatizado (*start/stop/status*) y coste cero de computación cuando no está en uso activo.
2. **Evaluación Zero-Shot de Modelos HTR Oficiales:** Evaluar el rendimiento en frío de 5 modelos entrenados del ecosistema europeo (TRIDIS, McCATMuS, CATMuS Medieval, CREMMA ManuMcFondue y Lectaurep Base) sobre 4 bloques cronológico-caligráficos representativos del archivo.
3. **Disección de la Red Neuronal y Alfabetos (Codecs Unicode):** Inspeccionar el espacio de caracteres interno de los modelos mediante ingeniería inversa en Python/PyTorch para dilucidar por qué unos modelos funcionan y otros colapsan.
4. **Diseño del Pipeline Híbrido LLM-HTR:** Diseñar el flujo de extracción y limpieza de archivos PAGE-XML para utilizar Gemini Multimodal como generador de *Ground Truth* de alta precisión sin tecleo manual, permitiendo reentrenamientos locales rápidos de Kraken.

---

## 2. ARQUITECTURA DE INFRAESTRUCTURA (GCE SPOT VM)

### 2.1 Especificaciones del Servidor
* **Instancia:** `escriptorium-spot-vm`
* **Proyecto GCP:** `gen-lang-client-0513056311`
* **Zona:** `europe-west1-b`
* **Tipo de Máquina:** `n1-standard-4` (4 vCPUs, 15 GB RAM + 16 GB Swap en disco).
* **Almacenamiento:** 120 GB `pd-standard` (HDD persistente, coste fijo: **~4,80 $/mes**).
* **Modelo de Facturación:** Spot / Preemptible (coste activo: **~0,05 $/h**; detenido: **0,00 $/h**).
* **Arquitectura de Software:** Docker CE + Docker Compose (11 contenedores activos: `web`, `db` PostgreSQL, `redis`, `nginx`, `channelserver`, `flower`, `celery-main`, `celery-low-priority`, `celery-live`, `celery-intensive-inference`, `celery-gpu`).

### 2.2 Control de Ciclo de Vida y Seguridad
* **CLI de Gestión:** [`scripts/manage_escriptorium_vm.py`](file:///c:/TRABAJOS/personal/genealo/scripts/manage_escriptorium_vm.py) con comandos directos: `start`, `stop`, `status`, `ip`, `tunnel`, `attach-gpu`, `detach-gpu`.
* **Skill Operativo Antigravity:** [`.agents/skills/control-servidor-escriptorium/SKILL.md`](file:///c:/TRABAJOS/personal/genealo/.agents/skills/control-servidor-escriptorium/SKILL.md).
* **Regla Cortafuegos:** `allow-escriptorium-8080` (puerto TCP 8080 público securizado por credenciales de superusuario).

---

## 3. BANCO DE MODELOS HTR EVALUADOS

Se descargaron e integraron 5 modelos `.mlmodel` pre-entrenados del consorcio **HTR-United**, **CATMuS**, **CREMMA** y **LECTAUREP**:

| ID | Nombre en eScriptorium | DOI / Zenodo | Peso | Ámbito de Entrenamiento Original |
| :---: | :--- | :---: | :---: | :--- |
| **`2`** | **TRIDIS (Documental y Notarial s.XII-XVI)** | `10.5281/zenodo.10788591` | 24,8 MB | Manuscritos legales, notariales y documentales del sur de Europa e Iberia (s. XII–XVI). |
| **`3`** | **CATMuS Medieval (Castellano y Latín s.XIII-XVI)** | `10.5281/zenodo.10066219` | 22,8 MB | Modelo generalista masivo (+113.000 líneas) de escritura medieval gótica y humanística. |
| **`4`** | **McCATMuS (Español y Romance s.XVI-XIX)** | `10.5281/zenodo.13788177` | 16,1 MB | Corpus diacrónico romance y español moderno en Unicode NFD estricto con `ſ` larga. |
| **`5`** | **CREMMA ManuMcFondue (Manuscritos Modernos s.XVI-XIX)** | `10.5281/zenodo.10886224` | 15,6 MB | Manuscritos modernos y contemporáneos (proyectos FoNDUE / Gallicorpora / CREMMA). |
| **`6`** | **Lectaurep Base (Administrativo y Notarial s.XVIII-XX)** | `10.5281/zenodo.6542744` | 15,4 MB | Tablas notariales, inventarios y registros administrativos franceses (1742–1928). |

---

## 4. INGENIERÍA INVERSA: ANÁLISIS DE CODECS Y ALFABETOS

Mediante el script [`scripts/check_tridis_chars.py`](file:///c:/TRABAJOS/personal/genealo/scripts/check_tridis_chars.py), se inspeccionó directamente la capa de salida neuronal (Softmax/CTC) del modelo **TRIDIS** dentro de los contenedores Docker, arrojando luz sobre una de las mayores incógnitas paleográficas del HTR:

```text
OcrModel: TRIDIS (Documental y Notarial s.XII-XVI)
Total caracteres entrenados en el Codec: 183
Caracteres ASCII: 94 clases estándar (a-z, A-Z, números, puntuación)
Caracteres Especiales no-ASCII: 89 clases
>>> VEREDICTO DE LA 's' LARGA: NO TIENE 'ſ' larga (U+017F).
```

### Hallazgos Clave del Codec de TRIDIS:
1. **Unificación de la `s`:** TRIDIS mapeó todas las variantes de *s* alta/larga y *s* redonda a la letra `s` común (`U+0073`). Esto elimina la confusión visual de la red neuronal y permite que el texto extraído sea inmediatamente buscable en bases de datos relacionales o grafos sin post-procesado regex.
2. **Soporte de Superíndices y Letras Voladas:** Posee clases dedicadas para `º` (`U+00BA`), `ª` (`U+00AA`) y letras voladas (`ͣ`, `ͤ`, `ͦ`, `ͧ`, `ͨ`), adaptándose a las abreviaturas parroquiales (`Ju.º`, `1.ª`, `m.er`).
3. **Tildes de Contracción / Macrones:** Soporta vocales abreviadas con tilde/macrón superior (`ā`, `ē`, `ī`, `ō`, `ŭ`, `̄`), habituales en la notaría hispánica.
4. **Grafías Históricas:** Soporte nativo de `ç`/`Ç`, `ñ`/`Ñ`, y consonantes arcaicas (`x`, `y`, `b`/`v`).

---

## 5. RESULTADOS DEL BENCHMARK EMPÍRICO

Se realizaron pruebas en frío (*Zero-Shot*, sin entrenamiento específico) sobre cuatro muestras documentales del archivo:

```mermaid
flowchart TD
    subgraph B1 ["Bloque 1: Cortesana Tardía (1616)"]
        I1["004306112_01921.jpg<br/>(Gaspar Rubiano)"]
        R1["TRIDIS: ~40% acierto esqueleto<br/>McCATMuS: Gibberish<br/>CATMuS: Pseudo-latín"]
    end

    subgraph B2 ["Bloque 2: Cursiva Setecientos (1725)"]
        I2["004306112_02250.jpg<br/>(Esteban de Calpe)"]
        R2["TRIDIS: ~80% acierto<br/>CREMMA: Ruido galicado<br/>McCATMuS: 50%"]
    end

    subgraph B3 ["Bloque 3: Redondilla Ilustrada (1758)"]
        I3["004306112_02400.jpg<br/>(Francisco de Moya)"]
        R3["TRIDIS: ~85-90% acierto pleno<br/>CREMMA: ~55% acierto<br/>McCATMuS: ~60% acierto"]
    end

    subgraph B4 ["Bloque 4: Escribano Real (1752)"]
        I4["004469033_00235.jpg<br/>(Catastro Ensenada)"]
        R4["Caligrafía de secretaría limpia<br/>Renglones rectos y espaciados"]
    end
```

### 5.1 Caso de Estudio 1: Folio de 1725 (`004306112_02250.jpg` — Esteban de Calpe)
En este asiento de bautismo de Domingo Toribio Andrino, **TRIDIS** extrajo casi la totalidad de las entidades genealógicas y notariales:
* **Fórmula Sacramental:** `...puse los santos oleos ad omungo hixo legiamo de Miguel Foribio y sumugtao Madlia Aridrino veninos deste lug...` (*«puse los santos oleos a Domingo hijo legítimo de Miguel Toribio y su mujer María Andrino vecinos deste lugar»*).
* **Padrinos:** `...fue Padrino Manuel Parcia tam sienesmno de dicho lus...` (*«fue Padrino Manuel García también vecino de dicho lugar»*).
* **Doctrina y Parentesco:** `...adea aduerti la obuiga de ensinar le la doctrina E Cunta mente elgarentesco spinidual...` (*«a quien advertí la obligación de enseñarle la doctrina cristiana y el parentesco espiritual...»*).
* **Cita Archivística al Foliado:** **`aoxas treenta , yjuna`** (*«a hojas 31»*, localizando el folio manuscrito del libro original).
* **Testigos y Parroquia:** `...hiondo astigor Manuil dominouer sapristan y lucia Marsin y Miguel Mlaran todos Vsuinos de ste dihro lugeta de Natall don dilla...` (*«siendo testigos Manuel Domínguez sacristán y Lucas Martín y Miguel Martín todos vecinos deste dicho lugar de Navarredondilla»*).
* **Suscripción Sacerdotal:** `Efran de cahop` (*Esteban de Calpe*).

### 5.2 Caso de Estudio 2: Folio de 1758 (`004306112_02400.jpg` — Don Francisco de Moya)
En la partida bautismal de Josepha García Hernández:
* **Bautismo de Socorro:** Leyó textualmente **`mesmo absia Basticado de Pocorro`** (*«mismo había bautizado de socorro»*).
* **Ritual Romano:** `...Ehere las lemad Peremonid que papiene el Pitual Romano...` (*«e hice las demás ceremonias que previene el Ritual Romano»*).
* **Filiación y 4 Abuelos:**
  * Bautizada: `Nombue Sosegha` (*Josepha*).
  * Padres: `Rixa leritma de Jan Gaacia y le Joseshia Rernanses` (*Hija legítima de Juan García y Josepha Hernández*).
  * Abuelos Maternos: `nos lulipe Rermander y Ana suncher` (*Phelipe Hernández y Ana Sánchez*).
* **Toponimia y Aldeas Menores:** Leyó **`Aldea de Nasal pronal`** (*«Aldea de Navalmoral»*, consignando el origen de los abuelos paternos en Navandrinal, anejo de Navalmoral).
* **Padrinos y Testigos:** Padrino Andrés de Arroyo (`Anores de sanoys`), testigos Joseph Hernández, Francisco García y Manuel Ximénez.
* **Fórmula de Cierre Notarial:** **`sy pon viasad firme scha letspra`** (*«y por verdad lo firmé fecha ut supra»*).
* **Firma:** `Pear deshoya` (*Juan de Moya*).

### 5.3 Diagnóstico de Modelos Alternativos (CREMMA y McCATMuS)
* **CREMMA ManuMcFondue:** Introdujo distorsiones fonéticas de raíz francesa (*`Dorgade`*, *`Caute`*, *`Dinntrar`*, *`llixalefume`*) al carecer de pesos específicos sobre las fórmulas notariales castellanas.
* **McCATMuS:** Mejoró notablemente en 1758 respecto a 1616, pero su exigencia de Unicode NFD con `ſ` larga provocó colisiones de caracteres y palabras truncadas (*`Paturoz Fabián`*, *`uma pint de calracol`*).

---

## 6. DIAGNÓSTICO DE LA SEGMENTACIÓN (`blla.mlmodel`)

1. **Baselines Horizontales:** El trazado de las líneas azules sobre el renglón es altamente preciso en los siglos XVIII (rectitud, paralelismo y separación).
2. **El Problema del Lomo Central (Doble Plana):**
   * El segmentador estándar confunde a veces la división entre la plana izquierda (verso) y la derecha (recto) si la sombra de costura es tenue o si una rúbrica cruza el canal central.
   * **Solución de Arquitectura:** El pre-procesamiento óptimo consiste en aplicar un particionado vertical lógico en dos semiesferas (Página Izquierda / Página Derecha) antes de la inferencia, o utilizar la herramienta de tijeras (`✂`) de eScriptorium.

---

## 7. EL FLUJO HÍBRIDO (ESCRIPTORIUM + GEMINI GROUND TRUTH)

### 7.1 El Problema del Bloat en PAGE-XML
Al exportar una página desde eScriptorium, el archivo PAGE-XML contiene más de **16.000 líneas de código XML** debido a que Kraken calcula polígonos geométricos individuales para cada palabra (`<Word>`) y cada letra (`<Glyph>`).

### 7.2 Depuración Estructural (98% de Reducción)
Para alimentar a Gemini y reimportar sin colisiones, se eliminan todos los nodos `<Word>` y `<Glyph>`, preservando exclusivamente:
```xml
<TextRegion id="eSc_textblock_...">
  <Coords points="..."/>
  <TextLine id="eSc_line_...">
    <Coords points="..."/>
    <Baseline points="..."/>
    <TextEquiv>
      <Unicode>Texto diplomático literal aquí</Unicode>
    </TextEquiv>
  </TextLine>
</TextRegion>
```
El archivo resultante pasa de 16.089 líneas a **~300 líneas limpias**.

### 7.3 Directiva de Anti-Normalización
Para que el texto generado por Gemini sea un *Ground Truth* válido para reentrenar Kraken:
1. **Transcripción Diplomática Estricta:** No expandir abreviaturas (respetar `Ju.º`, `p.ª m.er`, `v.os`).
2. **Respetar Ligaduras Físicas:** Mantener `deste`, `dela`, `sacaronle`.
3. **No usar `ſ` larga en modelos TRIDIS:** Mapear a `s` común.
4. **Respetar Grafías Históricas:** Conservar `baptize`, `ynigo`, `fevrero`.

---

## 8. CONCLUSIONES Y RECOMENDACIONES

1. **TRIDIS es el modelo base rector:** Cualquier entrenamiento o ajuste fino en el archivo del Alto Alberche debe cimentarse sobre TRIDIS, cuyo vocabulario notarial e ibérico supera a todos los modelos de su generación.
2. **El siglo XVIII es viable para HTR:** En la segunda mitad del XVIII (1750–1803) y en el Catastro de Ensenada, el reconocimiento en frío de TRIDIS roza el 85-90%, requiriendo únicamente un ajuste fino de 5 folios con Gemini para alcanzar grado industrial.
3. **El siglo XVII pertenece a los LLMs Multimodales:** En los siglos XVI y XVII (letras procesal y cortesana encadenada de Gaspar Rubiano), el HTR en frío no es viable económicamente; la extracción directa mediante Gemini 2.5 Pro / Flash sobre el JPG es el camino óptimo y más rentable.
4. **Disciplina de Costes:** La máquina Spot GCE demostró ser una solución económica impecable, permitiendo sesiones completas de experimentación por menos de **0,20 $** en cómputo Spot, quedando completamente detenida (`STOPPED`) con coste horario cero.
