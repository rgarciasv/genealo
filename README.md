# 📜 Proyecto de I+D Genealógico Alto Alberche
### *Motor de Paleografía Computacional, Reconstrucción Codicológica y Grafo Sacramental (1594–1902)*

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![Model: Gemini 3.8 Flash](https://img.shields.io/badge/LLM-Gemini%203.8%20Flash-orange.svg)](https://ai.google.dev/)
[![Engine: Google NotebookLM Pro](https://img.shields.io/badge/Grounding-NotebookLM%20Pro-green.svg)](https://notebooklm.google.com/)
[![Database: ArcadeDB Graph](https://img.shields.io/badge/Graph%20DB-ArcadeDB-purple.svg)](https://arcadedb.com/)
[![Corpus: FamilySearch & PARES](https://img.shields.io/badge/Corpus-8.500%2B%20Im%C3%A1genes-red.svg)](https://www.familysearch.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🏛️ 1. Visión y Resumen del Proyecto

El **Proyecto de I+D Genealógico Alto Alberche** es un entorno de computación aplicada, paleografía asistida por inteligencia artificial y estructuración en grafo diseñado para rescatar, transcribir y reconstruir el tejido demográfico, familiar y prosopográfico de la comarca del **Alto Valle del Alberche** (Ávila, España) entre **1594 y 1902**.

A partir de más de **8.500 fotogramas de microfilms históricos** digitalizados por FamilySearch y fondos del Catastro de Ensenada (1751–1752), el proyecto resuelve los tres grandes cuellos de botella de la investigación genealógica histórica:
1. **La dificultad paleográfica extrema:** Ductus cortesano, procesal y encadenado de los siglos XVI y XVII, abreviaturas eclesiásticas arcaicas, tintas ferrogálicas desgastadas y daños mecánicos.
2. **El desorden y descomposición codicológica:** Libros parroquiales desmembrados, códices mixtos encuadernados caóticamente ("cajones de sastre") y folios traspuestos.
3. **La homonimia y dispersión sacramental:** Comunidades cerradas con altísima endogamia, repertorio antroponímico reducido (múltiples parientes vivos con el mismo nombre y apellido) y dependencias jurisdiccionales cambiantes entre pueblos y anejos.

```
                      ARQUITECTURA GENERAL DEL SISTEMA
  +-------------------------------------------------------------------------+
  |              CORPUS DIGITALIZADO (FamilySearch & PARES)                 |
  |        8.500+ fotogramas (Rollos DGS 004306112, 004306113, etc.)        |
  +-------------------------------------------------------------------------+
                                       │
                                       ▼
  +-------------------------------------------------------------------------+
  |               SISTEMA DE GROUNDING PALEOGRÁFICO MAESTRO                 |
  |   00_Normas Ecdóticas │ 01_Diccionario Pasivo │ 02_Mapas Codicología    |
  |   03_Autoridades Manos │ 04_Jurisdicciones Canónicas                    |
  +-------------------------------------------------------------------------+
                                       │
                                       ▼
  +-------------------------------------------------------------------------+
  |            MOTOR MULTIMODAL Y RECONSTRUCCIÓN LÓGICO-SACRAMENTAL         |
  |          NotebookLM Pro (API Web MCP) + Gemini 3.8 Flash SDK            |
  |     - Desarticulación Virtual de Códices Mixtos ([L-30])                |
  |     - Preservación de Planas Híbridas sin corte de JPG ([L-31])         |
  |     - Fusión de Tomas Hermanas Base vs. Corrección ([L-20])             |
  +-------------------------------------------------------------------------+
                                       │
                                       ▼
  +-------------------------------------------------------------------------+
  |             GRAFO DE CONOCIMIENTO SACRAMENTAL (ArcadeDB)                |
  |    Vértices: Personas, Partidas, Folios, Lugares, Clérigos              |
  |    Aristas: HIJO_DE, CASADO_CON, PADRINO_DE, TESTIGO_DE, DUCTUS_DE     |
  +-------------------------------------------------------------------------+
```

---

## 🗺️ 2. Ámbito Territorial y Códigos Cuatriletrados (`[L-24]`)

El proyecto abarca el curso alto del río Alberche en la vertiente sur de la Sierra de Gredos y Paramera. Para evitar colisiones toponímicas, toda la arquitectura de bases de datos, nombres de cuadernos y scripts utiliza el **Estándar Geográfico Cuatriletrado**:

| Código | Localidad | Categoría Canónica Histórica | Serie Sacramental Preservada |
| :---: | :--- | :--- | :--- |
| **`NRDL`** | **Navarredondilla** | Parroquia independiente (Santiago Apóstol). | Bautismos (1594–1889), Matrimonios (1634–1803), Defunciones (1631–1902). |
| **`JMOL`** | **San Juan del Molinillo** | Parroquia (San Juan Bautista). Anejo de Navalmoral hasta 1715; matriz de Navandrinal y Villarejo desde 1715. | Bautismos (1623–1876), Matrimonios (1697–1875), Defunciones (1678–1876). |
| **`NDRN`** | **Navandrinal** | Anejo sin libros sacramentales propios independientes. | Documentado dentro de los libros de `NMRL` (pre-1715) y `JMOL` (post-1715). Catastro de Ensenada propio en 1751. |
| **`VLLR`** | **El Villarejo** | Anejo sin libros sacramentales propios independientes. | Documentado dentro de los libros de `NMRL` (pre-1715) y `JMOL` (post-1715). Catastro de Ensenada propio en 1751. |
| **`NMRL`** | **Navalmoral de la Sierra** | Matriz canónica fundacional del valle (hasta 1715). | Registro matriz para todas las búsquedas genealógicas anteriores a 1715. |
| **`BHND`** | **Burgohondo** | Abadía Colegiata matriz histórica del Alto Alberche. | Jurisdicción eclesiástica y registro de confirmaciones / dispensas. |

> [!IMPORTANT]
> **Regla de Redirección Canónica Pre-1715 (`[L-24]`):** Antes de 1715, Molinillo, Navandrinal y Villarejo dependían eclesiásticamente de Navalmoral de la Sierra. La búsqueda de ancestros de estas tres poblaciones anteriores a 1715 debe realizarse forzosamente en los libros de `NMRL` y `NRDL`.

---

## ⚖️ 3. Principios Fundamentales y Filosofía Archivística

El desarrollo del proyecto está gobernado por directivas metodológicas inmutables (resumidas en [`contexto_maestro.md`](contexto_maestro.md) y [`BITACORA_EXPERIMENTOS.md`](BITACORA_EXPERIMENTOS.md)):

* **`[L-30]` Principio del Archivero Virtual (Series Sacramentales Puras):** Los cuadernos de trabajo se organizan por series sacramentales puras y cronológicas (Bautismos, Matrimonios, Defunciones). Los códices físicos mixtos (volúmenes donde los curas encuadernaron juntos varios sacramentos o retales sueltos) se desarticulan lógicamente asignando cada fotograma a su serie natural sin alterar los archivos de imagen.
* **`[L-31]` Preservación Integral de Imágenes Híbridas (Prohibición de Corte Físico):** En fotogramas fotografiados a doble página que contienen sacramentos distintos en plana izquierda (verso) y derecha (recto), está estrictamente prohibido cortar físicamente el archivo JPG. La imagen original se asocia lógicamente a ambos cuadernos, instruyendo al motor de IA mediante el prompt del sistema a extraer exclusivamente la plana solicitada (`lado: izquierda` o `lado: derecha`).
* **`[L-32]` Autos de Visita Pastoral *In Situ*:** Los decretos y autos de Santa Visita Pastoral firmados por los obispos de Ávila o sus visitadores generales deben permanecer en su posición cronológica exacta dentro de los libros sacramentales, ya que operan como auditorías canónicas contemporáneas de la diligencia del párroco y fijan fechas topográficas indiscutibles.
* **`[L-20]` Protocolo de Fusión de Tomas Hermanas:** En los microfilms abundan parejas de tomas del mismo folio ("toma base" y "toma corrección") disparadas por el fotógrafo para enfocar mejor zonas curvas o tapadas por costura apretada (*gutter shadow*). Ambas tomas se cotejan en conjunto para restituir el texto íntegro, produciendo una única ficha depurada con **cero duplicados**.
* **`[L-22]` Transversalidad del Ductus Eclesiástico:** La mano y los tics caligráficos de un sacerdote no varían al escribir en bautismos, bodas o entierros. Las fichas de escribientes residen de forma desacoplada y centralizada en [`03_AUTORIDADES_PALEOGRAFICAS_ALTO_ALBERCHE.md`](03_AUTORIDADES_PALEOGRAFICAS_ALTO_ALBERCHE.md).
* **`[L-26]` Modelo de Identificación Inmutable en Dos Capas:** La clave primaria universal de toda imagen en el disco, en el grafo y en las URLs ARK es su nombre completo canónico `{DGS}_{FOTOGRAMA}.jpg` (ej. `004306112_01874.jpg`). Los atributos descriptivos (número de folio manuscrito, parroquia, sacramento) son metadatos secundarios desacoplados.

---

## 📚 4. Sistema de Grounding Paleográfico (Fuentes Maestras)

Para garantizar transcripciones 100% libres de alucinaciones antroponímicas o toponímicas, cada cuaderno de trabajo cuenta con una batería de fuentes de referencia ecdótica inyectadas en su contexto:

1. **[`00_INSTRUCCIONES_PALEOGRAFICAS_V2.md`](00_INSTRUCCIONES_PALEOGRAFICAS_V2.md):** Criterios de edición diplomática, tratamiento de lagunas (`[ROTO]`, `[ILEGIBLE]`), marginalia, partidas cortadas inter-folio (`[L-25]`) y formato JSON Schema estricto.
2. **[`01_DICCIONARIO_ANCLAJE_NAVARREDONDILLA.md`](01_DICCIONARIO_ANCLAJE_NAVARREDONDILLA.md):** Vocabulario de mundo cerrado con la toponimia menor exhaustiva (pagos, arroyos, cerros), nombres de pila y fórmulas notariales del siglo XVII.
3. **`02_INSTRUCCIONES_CRONOLOGICAS_...`:** Mapas forenses de dislocaciones codicológicas y saltos de fotogramas (ej. [`02_INSTRUCCIONES_CRONOLOGICAS_NAVARREDONDILLA_1594_1695.md`](02_INSTRUCCIONES_CRONOLOGICAS_NAVARREDONDILLA_1594_1695.md) para resolver el desorden del Elemento 13).
4. **[`03_AUTORIDADES_PALEOGRAFICAS_ALTO_ALBERCHE.md`](03_AUTORIDADES_PALEOGRAFICAS_ALTO_ALBERCHE.md):** Fichas biográficas y paleográficas de los escribanos y sacerdotes (Alonso del Valle, Diego Arias, Simón Palomo Bayala, Pedro Manso, etc.), con tipología de grafías (itálica, redondilla, procesal) y tics abreviativos.
5. **[`04_JURISDICCIONES_Y_DEPENDENCIAS_PARROQUIALES.md`](04_JURISDICCIONES_Y_DEPENDENCIAS_PARROQUIALES.md):** Marco canónico, historia institucional de las parroquias, diezmos y régimen de anejos.

---

## 🗂️ 5. Catálogo del Corpus y Estado de los Cuadernos

El repositorio gestiona **23 cuadernos de trabajo especializados** en Google NotebookLM Pro y un inventario central en [`catalogo_corpus.json`](catalogo_corpus.json):

### A. Serie Navarredondilla (`NRDL`) — 2.289 Imágenes
* **`NRDL-BAUT-01` a `07`:** Bautismos completos (1594–1889). El cuaderno inicial `NRDL-BAUT-01` cuenta con 193 fuentes (188 fotogramas purificados + 5 fuentes maestras).
* **`NRDL-MATR-01` a `02`:** Matrimonios (1634–1803). Incluye los retales dispersos de 1667–1668 rescatados del códice mixto. *(Nota: El Libro 3º de Casados 1803–1902 no fue microfilmado en FamilySearch y constituye la gran laguna del siglo XIX, documentada en el inventario de anomalías).*
* **`NRDL-DIFU-S17` y `NRDL-DIFU-01` a `05`:** Serie de difuntos (1631–1902). `NRDL-DIFU-S17 (1631-1701)` unifica 132 fotogramas del siglo XVII desarticulados del códice mixto.

### B. Serie San Juan del Molinillo (`JMOL`) — 2.731 Imágenes
* **`JMOL-BAUT-01` a `05` + `JMOL-INDICE-BAUT`:** Serie completa de Bautismos (1.080 fuentes, 100% completada y verificada). *(Nota codicológica: `JMOL-INDICE-BAUT` es un códice bífido que contiene tanto el Índice Alfabético de Bautismos 1750–1914 en fotogramas `02661`–`02748`, como el crucial **Índice Cronológico de Casados 1716–1920** en fotogramas `02749`–`02766`)*.
* **`JMOL-MATR-01` a `03`:** Matrimonios completos (1697–1875).
* **`JMOL-DIFU-01` a `06` + `JMOL-DIFU-PARVULOS` + `JMOL-INDICE-DIFU`:** Serie de Defunciones (1678–1876).
* **`JMOL-SACRAMENTAL-1842-1850`:** Expediente Judicial de Convalidación Sacramental tras la muerte del cura D. Marcelino Tore Díaz (Bautismos 1847–48 con filiación a 4 abuelos, Matrimonios 1842–49 y Defunciones 1843–49, aprobado por el Obispo de Ávila D. Manuel López Santisteban en 1850).

### C. Catastro de Ensenada (1751–1752) — Fondo Fiscal y Nominal
* **`NRDL-ENSENADA-LEGOS-01` / `BIENES-01..03`:** Censo nominal del Personal Seglar y Libros de Bienes de Navarredondilla.
* **`JMOL-ENSENADA-LEGOS-01`:** Personal Seglar de San Juan del Molinillo (28 fotogramas, verificado).
* **`NDRN-ENSENADA-LEGOS-01`:** Personal Seglar de Navandrinal (34 fotogramas, verificado).
* **`VLLR-ENSENADA-LEGOS-01`:** Personal Seglar de El Villarejo (51 fotogramas, verificado).

---

## 🛠️ 6. Estructura del Repositorio

```text
genealo/
├── .agents/skills/                                  # Suite de Skills Operativas del Archivero Virtual
│   ├── ingesta-parroquial-notebooklm/SKILL.md       # Ingesta masiva, rate-limiting y gestión [L-21]
│   ├── reconstruccion-codicologica/SKILL.md         # Desarticulación [L-30], híbridas [L-31] y visitas [L-32]
│   ├── grounding-cuadernos-parroquiales/SKILL.md    # Inyección ecdótica y ChatSettings de cascarones
│   ├── transcripcion-diplomatica-parroquial/SKILL.md# Fusión tomas hermanas [L-20] y JSON Schema
│   └── auditoria-integridad-corpus/SKILL.md         # Verificación forense E2E de fuentes READY
├── 00_INSTRUCCIONES_PALEOGRAFICAS_V2.md            # Criterios ecdóticos y diplomáticos
├── 01_DICCIONARIO_ANCLAJE_NAVARREDONDILLA.md        # Léxico cerrado y toponimia menor
├── 02_INSTRUCCIONES_CRONOLOGICAS_...md              # Guías de secuencia y saltos codicológicos
├── 03_AUTORIDADES_PALEOGRAFICAS_ALTO_ALBERCHE.md    # Corpus de manos caligráficas y párrocos
├── 04_JURISDICCIONES_Y_DEPENDENCIAS_PARROQUIALES.md # Historia institucional y canónica
├── BITACORA_EXPERIMENTOS.md                         # Registro formal de pruebas empíricas (Exp. 01 a 21)
├── INVENTARIO_DESCARGAS_Y_ANOMALIAS_DOCUMENTALES.md # Catálogo forense de lagunas y patologías de rollo
├── TODO.md                                          # Roadmap operativo y estado de tareas
├── contexto_maestro.md                              # Estado global y directivas del proyecto
├── catalogo_corpus.json                             # Metadatos canónicos de las 8.515 fuentes
│
├── scripts/                                         # Herramientas de automatización en Python
│   ├── ingest_navarredondilla_parroquial.py         # Pipeline de subida para Navarredondilla
│   ├── ingest_sanjuan_parroquial.py                 # Pipeline de subida para San Juan del Molinillo
│   ├── reorganize_nrdl_defunciones_s17.py           # Desarticulación de códices mixtos ([L-30])
│   ├── add_marriages_to_matr01.py                   # Enriquecimiento de matrimonios dispersos
│   ├── verify_nrdl_parroquial_sources.py            # Auditoría E2E de fuentes en NotebookLM (NRDL)
│   ├── verify_sanjuan_parroquial_sources.py         # Auditoría E2E de fuentes en NotebookLM (JMOL)
│   └── supervise_m1.py                              # Watchdog de sesión y salud de ingesta
│
└── transcripciones/                                 # Salidas de transcripción paleográfica verificada
```

---

## 🚀 7. Puesta en Marcha y Ejecución

### Requisitos Previos
* **Python 3.11+** (Windows / Linux / macOS).
* **Navegador Chromium / Google Chrome** con sesión iniciada en Google para autenticación persistente (`[L-21]`).
* Servidor **ArcadeDB** (si se ejecuta el módulo de sincronización a grafo).

### Instalación
```powershell
# Clonar el repositorio
git clone https://github.com/tu-usuario/genealo-alto-alberche.git
cd genealo-alto-alberche

# Crear y activar entorno virtual
python -m venv venv
.\venv\Scripts\Activate.ps1   # En Windows
# source venv/bin/activate    # En Linux/macOS

# Instalar dependencias
pip install -r requirements.txt
```

### Autenticación Desatendida (`[L-21]`)
Para renovar silenciosamente las credenciales de NotebookLM mediante el perfil persistente de Chromium:
```powershell
.\venv\Scripts\notebooklm.exe login
.\venv\Scripts\notebooklm.exe auth check
```

### Verificación de Integridad de Cuadernos
Para auditar que todos los cuadernos en la nube contienen exactamente el número de fotogramas esperados y sin duplicados:
```powershell
# Auditar serie de Navarredondilla
python scripts/verify_nrdl_parroquial_sources.py

# Auditar serie de San Juan del Molinillo
python scripts/verify_sanjuan_parroquial_sources.py
```

---

## 🔒 8. Ética, Privacidad y Licencia

* **Naturaleza Pública de los Documentos:** Todo el corpus procesado pertenece a registros parroquiales históricos (>120 años de antigüedad) o registros fiscales de la Corona de Castilla de mediados del siglo XVIII (>270 años de antigüedad), de acceso público y sin afectación por normativas de protección de datos de personas vivas (RGPD).
* **Licencia de Código:** El software, scripts de automatización y modelos de extracción están licenciados bajo la [Licencia MIT](LICENSE). Los textos históricos originales pertenecen al patrimonio documental custodiado por la Diócesis de Ávila y el Archivo General de Simancas (PARES).

---
*Proyecto concebido y ejecutado con pasión por la historia local, la precisión archivística y la genealogía del Alto Alberche.*
