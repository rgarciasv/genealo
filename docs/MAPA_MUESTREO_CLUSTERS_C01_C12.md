# Mapa Operativo de Muestreo: Los 12 Clusters Paleográficos (`C01–C12`) y los 33 Cuadernos Auditados

> **Propósito:** Este documento conecta directamente todo el trabajo previo de **NotebookLM Pro** (las 33 auditorías codicológicas en [`transcripciones/auditoria_codicologica/`](file:///c:/TRABAJOS/personal/genealo/transcripciones/auditoria_codicologica/), [`03_AUTORIDADES_PALEOGRAFICAS_ALTO_ALBERCHE.md`](file:///c:/TRABAJOS/personal/genealo/03_AUTORIDADES_PALEOGRAFICAS_ALTO_ALBERCHE.md) y [`catalogo_corpus.json`](file:///c:/TRABAJOS/personal/genealo/catalogo_corpus.json)) con archivos `.jpg` reales verificados en disco para entrenar los **4 Motores Kraken**.
>
> **Imágenes físicas indexadas en `imagenes/`:** `7,860` archivos `.jpg` verificados en disco local.

---

## 1. Resumen Ejecutivo: Los 4 Motores Kraken y sus 12 Clusters (`C01–C12`)

| Motor Kraken Consolidado | Clusters Incluidos | Arco Temporal | Estado Actual de Muestras en Local |
| :--- | :--- | :--- | :--- |
| **`Motor 1`: `alto_alberche_procesal_1590_1660.mlmodel`** | `C01`, `C02`, `C03` | `1594–1660` | Candidatos localizados en disco (`DGS 004306112` y `004298571_00532`). |
| **`Motor 2`: `alto_alberche_bastarda_1660_1790.mlmodel`** | `C04`, `C05`, `C06`, `C07` | `1660–1790` | **En marcha:** Folio `004298570_01608` (69 líneas transcritas con 0 errores Unicode, `C04`/`C05`). |
| **`Motor 3`: `alto_alberche_decimononico_1790_1902.mlmodel`** | `C08`, `C09`, `C10`, `C11` | `1790–1902` | **En marcha:** `lote_prueba_5` (`004298570_02637` a `02641`, 5 folios ya segmentados en local, `C09`). |
| **`Motor 4`: `alto_alberche_aparato_auxiliar.mlmodel`** | `C12` | `1649–1914` | Candidatos localizados (`JMOL-INDICE-BAUT`, `JMOL-INDICE-DIFU` y Padrones de Confirmación). |

---

## 2. Catálogo de Muestreo por Cluster (`C01` a `C12`) con Rutas Locales Verificadas

### `C01` — Procesal Encadenada Pura y Cortesana Tardía (1594–1635)
* **Motor Kraken destino:** `Motor 1: Procesal y Transición (1590–1660)`
* **Rasgos morfográficos:** Trazos ligados sin levantar pluma, bucles envolventes, ojos cerrados, abreviaturas por suspensión y sobrelineado continuo.
* **Escribanos / Autoridades de referencia:** Joan Martínez [Monterroso] (1596–1604, NRDL); Francisco Ximénez (1594–1595, NRDL); Alonso Hernández (1601–1610, NRDL); Pedro Pérez de las Presas (1627–1634, NRDL)
* **Cuadernos canónicos fuente:** `NRDL-BAUT-01`, `Lib. Baut. Navarre Vol. 1 (1594-1695)`
* **Muestras `.jpg` verificadas en disco listas para segmentar (`segmentar_lote.py`):**
  - [`004306112_01874.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004306112/004306112_01874.jpg) (`imagenes/rollo 004306112/004306112_01874.jpg`)
  - [`004306112_01878.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004306112/004306112_01878.jpg) (`imagenes/rollo 004306112/004306112_01878.jpg`)
  - [`004306112_01881.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004306112/004306112_01881.jpg) (`imagenes/rollo 004306112/004306112_01881.jpg`)
  - [`004306112_01895.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004306112/004306112_01895.jpg) (`imagenes/rollo 004306112/004306112_01895.jpg`)
  - [`004306112_01938.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004306112/004306112_01938.jpg) (`imagenes/rollo 004306112/004306112_01938.jpg`)

### `C02` — Procesal Redonda / Semigótica / Claustral de Transición (1594–1650)
* **Motor Kraken destino:** `Motor 1: Procesal y Transición (1590–1660)`
* **Rasgos morfográficos:** Módulo amplio y redondo, letras más sueltas que la encadenada, influencia humanística o monástica (Burgohondo/Oropesa).
* **Escribanos / Autoridades de referencia:** Alonso del Valle (1594, NRDL); Fray Francisco de Oropesa (1595–1596, NRDL); Gaspar Rubiano (1612–1626, NRDL); Gaspar González (1640–1642, NRDL)
* **Cuadernos canónicos fuente:** `NRDL-BAUT-01`, `NRDL-MATR-01`, `NRDL-DIFU-S17 (1631-1701)`
* **Muestras `.jpg` verificadas en disco listas para segmentar (`segmentar_lote.py`):**
  - [`004306112_01873.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004306112/004306112_01873.jpg) (`imagenes/rollo 004306112/004306112_01873.jpg`)
  - [`004306112_01876.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004306112/004306112_01876.jpg) (`imagenes/rollo 004306112/004306112_01876.jpg`)
  - [`004306112_01922.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004306112/004306112_01922.jpg) (`imagenes/rollo 004306112/004306112_01922.jpg`)
  - [`004306112_01960.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004306112/004306112_01960.jpg) (`imagenes/rollo 004306112/004306112_01960.jpg`)
  - [`004306112_02043.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004306112/004306112_02043.jpg) (`imagenes/rollo 004306112/004306112_02043.jpg`)

### `C03` — Humanística / Itálica Temprana y Bastarda de Transición (1635–1675)
* **Motor Kraken destino:** `Motor 1: Procesal y Transición (1590–1660)`
* **Rasgos morfográficos:** Inclinación derecha moderada, desaparición del bucle procesal envolvente, astas altas limpias, separación clara de palabras.
* **Escribanos / Autoridades de referencia:** Francisco Sánchez del Unar (1633–1641, NRDL); Don Marcos Conde (1650–1653, NRDL); Andrés Bautista (1653–1658, NRDL); Fray Mateo del Mazo (1658–1689, NRDL/JMOL)
* **Cuadernos canónicos fuente:** `NRDL-BAUT-01`, `NRDL-MATR-01`, `JMOL-DIFU-PARVULOS`
* **Muestras `.jpg` verificadas en disco listas para segmentar (`segmentar_lote.py`):**
  - [`004306112_01950.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004306112/004306112_01950.jpg) (`imagenes/rollo 004306112/004306112_01950.jpg`)
  - [`004306112_02053.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004306112/004306112_02053.jpg) (`imagenes/rollo 004306112/004306112_02053.jpg`)
  - [`004306112_02074.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004306112/004306112_02074.jpg) (`imagenes/rollo 004306112/004306112_02074.jpg`)
  - [`004306112_02080.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004306112/004306112_02080.jpg) (`imagenes/rollo 004306112/004306112_02080.jpg`)
  - [`004298571_00532.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004298571/004298571_00532.jpg) (`imagenes/rollo 004298571/004298571_00532.jpg`)

### `C04` — Bastarda Española Clásica de Párroco (Fines s. XVII – 1ª mitad s. XVIII) (1675–1745)
* **Motor Kraken destino:** `Motor 2: Bastarda Española y Cancilleresca (1660–1790)`
* **Rasgos morfográficos:** Letra bastarda asentada, contraste medio de pluma, superíndices volados constantes (franᶜº, lexᵐª, vºˢ), caja regular.
* **Escribanos / Autoridades de referencia:** Domingo Hernández (1666–1680, NRDL); Lic. Melchor Núñez (1684–1689, NRDL); Lic. Jerónimo Ruiz Núñez (1689–1696, NRDL); Fray Francisco Martínez (1715–1725, JMOL — Folios tipo 01608)
* **Cuadernos canónicos fuente:** `NRDL-BAUT-01`, `NRDL-BAUT-02`, `JMOL-BAUT-01`, `JMOL-MATR-01`, `JMOL-DIFU-01`
* **Muestras `.jpg` verificadas en disco listas para segmentar (`segmentar_lote.py`):**
  - [`004298570_01608.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004298570/004298570_01608.jpg) (`imagenes/rollo 004298570/004298570_01608.jpg`)
  - [`004306112_02105.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004306112/004306112_02105.jpg) (`imagenes/rollo 004306112/004306112_02105.jpg`)
  - [`004306112_02135.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004306112/004306112_02135.jpg) (`imagenes/rollo 004306112/004306112_02135.jpg`)
  - [`004306112_02230.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004306112/004306112_02230.jpg) (`imagenes/rollo 004306112/004306112_02230.jpg`)
  - [`004298571_00015.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004298571/004298571_00015.jpg) (`imagenes/rollo 004298571/004298571_00015.jpg`)

### `C05` — Bastarda Cursiva / Barroca Densa y Tenientes Auxiliares (1680–1765)
* **Motor Kraken destino:** `Motor 2: Bastarda Española y Cancilleresca (1660–1790)`
* **Rasgos morfográficos:** Mayor velocidad de trazo, astas ascendentes y descendentes largas que invaden líneas contiguas, tinta a veces pálida o ferrogálica densa.
* **Escribanos / Autoridades de referencia:** Fr. Basilio Herrero Carpio (1717, JMOL — Partida 4 de 01608); Tenientes y vicarios de NRDL-BAUT-02 y NRDL-DIFU-01; Escribanos de JMOL-BAUT-01 (tramo 1730–1752) y JMOL-DIFU-01
* **Cuadernos canónicos fuente:** `JMOL-BAUT-01`, `NRDL-BAUT-02`, `NRDL-DIFU-01`, `NRDL-MATR-02`
* **Muestras `.jpg` verificadas en disco listas para segmentar (`segmentar_lote.py`):**
  - [`004298570_01650.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004298570/004298570_01650.jpg) (`imagenes/rollo 004298570/004298570_01650.jpg`)
  - [`004298570_01720.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004298570/004298570_01720.jpg) (`imagenes/rollo 004298570/004298570_01720.jpg`)
  - [`004306112_02310.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004306112/004306112_02310.jpg) (`imagenes/rollo 004306112/004306112_02310.jpg`)
  - [`004306113_00450.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004306113/004306113_00450.jpg) (`imagenes/rollo 004306113/004306113_00450.jpg`)
  - [`004306113_00750.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004306113/004306113_00750.jpg) (`imagenes/rollo 004306113/004306113_00750.jpg`)

### `C06` — Bastarda Cancilleresca de Escribano Real (Catastro de Ensenada) (1751–1752)
* **Motor Kraken destino:** `Motor 2: Bastarda Española y Cancilleresca (1660–1790)`
* **Rasgos morfográficos:** Caligrafía profesional de escribano de comisión: márgenes amplios con llaves y linderos (L., P., M., N.), guarismos de fanegas/celemines y reales.
* **Escribanos / Autoridades de referencia:** Escribanos Reales del Catastro de Ensenada (Navarredondilla, Molinillo, Navandrinal, El Villarejo, Navalmoral)
* **Cuadernos canónicos fuente:** `NRDL-ENSENADA-LEGOS-01`, `JMOL-ENSENADA-LEGOS-01`, `NDRN-ENSENADA-LEGOS-01`, `VLLR-ENSENADA-LEGOS-01`, `NMRL-ENSENADA-LEGOS-01`
* **Muestras `.jpg` verificadas en disco listas para segmentar (`segmentar_lote.py`):**
  - [`004469033_00890.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004469033/004469033_00890.jpg) (`imagenes/rollo 004469033/004469033_00890.jpg`)
  - [`004469028_00910.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004469028/004469028_00910.jpg) (`imagenes/rollo 004469028/004469028_00910.jpg`)
  - [`004469028_00960.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004469028/004469028_00960.jpg) (`imagenes/rollo 004469028/004469028_00960.jpg`)
  - [`004469028_00990.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004469028/004469028_00990.jpg) (`imagenes/rollo 004469028/004469028_00990.jpg`)
  - [`004469027_01840.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004469027/004469027_01840.jpg) (`imagenes/rollo 004469027/004469027_01840.jpg`)

### `C07` — Bastarda Ilustrada Estandarizada (2ª mitad s. XVIII) (1752–1803)
* **Motor Kraken destino:** `Motor 2: Bastarda Española y Cancilleresca (1660–1790)`
* **Rasgos morfográficos:** Letra limpia, escolarizada según arte de Palomares/Anduaga, renglones muy rectos, estructura de partida con abuelos paternos y maternos.
* **Escribanos / Autoridades de referencia:** Párrocos ilustrados de NRDL-BAUT-03 (1750–1803) y JMOL-BAUT-02 (1752–1800); Párrocos de NRDL-DIFU-01B / NRDL-DIFU-02 y JMOL-DIFU-02
* **Cuadernos canónicos fuente:** `NRDL-BAUT-03`, `JMOL-BAUT-02`, `NRDL-DIFU-01B`, `JMOL-MATR-01`, `JMOL-DIFU-02`
* **Muestras `.jpg` verificadas en disco listas para segmentar (`segmentar_lote.py`):**
  - [`004306112_02410.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004306112/004306112_02410.jpg) (`imagenes/rollo 004306112/004306112_02410.jpg`)
  - [`004306112_02520.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004306112/004306112_02520.jpg) (`imagenes/rollo 004306112/004306112_02520.jpg`)
  - [`004298571_00600.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004298571/004298571_00600.jpg) (`imagenes/rollo 004298571/004298571_00600.jpg`)
  - [`004306112_02375.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004306112/004306112_02375.jpg) (`imagenes/rollo 004306112/004306112_02375.jpg`)
  - [`004306112_02421.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004306112/004306112_02421.jpg) (`imagenes/rollo 004306112/004306112_02421.jpg`)

### `C08` — Bastarda Tardía / Transición Liberal (1800–1840) (1800–1840)
* **Motor Kraken destino:** `Motor 3: Decimonónico e Inglesa (1790–1902)`
* **Rasgos morfográficos:** Transición entre la pluma de ave tardía y las primeras plumillas metálicas; aparición frecuente de llaves marginales '}' separando el índice.
* **Escribanos / Autoridades de referencia:** Párrocos de NRDL-BAUT-04 (1804–1828) y JMOL-BAUT-03 (1801–1826); Párrocos de JMOL-MATR-02 (1790–1852) y NRDL-DIFU-02 (1802–1831)
* **Cuadernos canónicos fuente:** `NRDL-BAUT-04`, `JMOL-BAUT-03`, `JMOL-MATR-02`, `NRDL-DIFU-02`
* **Muestras `.jpg` verificadas en disco listas para segmentar (`segmentar_lote.py`):**
  - [`004306112_02630.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004306112/004306112_02630.jpg) (`imagenes/rollo 004306112/004306112_02630.jpg`)
  - [`004306112_02740.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004306112/004306112_02740.jpg) (`imagenes/rollo 004306112/004306112_02740.jpg`)
  - [`004298571_00250.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004298571/004298571_00250.jpg) (`imagenes/rollo 004298571/004298571_00250.jpg`)
  - [`004306113_00850.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004306113/004306113_00850.jpg) (`imagenes/rollo 004306113/004306113_00850.jpg`)
  - [`004306112_02606.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004306112/004306112_02606.jpg) (`imagenes/rollo 004306112/004306112_02606.jpg`)

### `C09` — Cursiva Inglesa / Comercial Aguda con Llave Marginal '}' (Mediados s. XIX) (1835–1870)
* **Motor Kraken destino:** `Motor 3: Decimonónico e Inglesa (1790–1902)`
* **Rasgos morfográficos:** Plumilla metálica fina, inclinación marcada a la derecha, llaves '}' entre margen_indice y cuerpo_partida (como el lote_prueba_5: 02637–02641).
* **Escribanos / Autoridades de referencia:** D. Marcelino Tore Díaz y sucesores en JMOL-BAUT-04 (1827–1852) y JMOL-BAUT-05 (1851–1862); Expediente Episcopal JMOL-SACRAMENTAL-1842-1850; Párrocos de NRDL-BAUT-05 (1829–1852) y NRDL-BAUT-06 (1852–1865)
* **Cuadernos canónicos fuente:** `JMOL-BAUT-04`, `JMOL-BAUT-05`, `JMOL-SACRAMENTAL-1842-1850`, `NRDL-BAUT-05`, `NRDL-BAUT-06`
* **Muestras `.jpg` verificadas en disco listas para segmentar (`segmentar_lote.py`):**
  - [`004298570_02637.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004298570/004298570_02637.jpg) (`imagenes/rollo 004298570/004298570_02637.jpg`)
  - [`004298570_02638.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004298570/004298570_02638.jpg) (`imagenes/rollo 004298570/004298570_02638.jpg`)
  - [`004298570_02639.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004298570/004298570_02639.jpg) (`imagenes/rollo 004298570/004298570_02639.jpg`)
  - [`004298570_02460.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004298570/004298570_02460.jpg) (`imagenes/rollo 004298570/004298570_02460.jpg`)
  - [`004306113_00100.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004306113/004306113_00100.jpg) (`imagenes/rollo 004306113/004306113_00100.jpg`)

### `C10` — Cursiva Rápida / Filiforme o de Mano Anciana (s. XIX) (1840–1895)
* **Motor Kraken destino:** `Motor 3: Decimonónico e Inglesa (1790–1902)`
* **Rasgos morfográficos:** Trazo filiforme muy rápido o tembloroso, vocales aplastadas (m/n/u/i indistinguibles sin contexto léxico), abreviaturas decimonónicas.
* **Escribanos / Autoridades de referencia:** Manos rápidas de JMOL-DIFU-03 (1849–1851), JMOL-DIFU-04 (1851–1883) y NRDL-DIFU-03 / 04
* **Cuadernos canónicos fuente:** `JMOL-DIFU-03`, `JMOL-DIFU-04`, `NRDL-DIFU-03`, `NRDL-DIFU-04`
* **Muestras `.jpg` verificadas en disco listas para segmentar (`segmentar_lote.py`):**
  - [`004298571_00945.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004298571/004298571_00945.jpg) (`imagenes/rollo 004298571/004298571_00945.jpg`)
  - [`004298571_01050.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004298571/004298571_01050.jpg) (`imagenes/rollo 004298571/004298571_01050.jpg`)
  - [`004306113_01020.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004306113/004306113_01020.jpg) (`imagenes/rollo 004306113/004306113_01020.jpg`)
  - [`004306113_01200.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004306113/004306113_01200.jpg) (`imagenes/rollo 004306113/004306113_01200.jpg`)
  - [`004298571_01033.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004298571/004298571_01033.jpg) (`imagenes/rollo 004298571/004298571_01033.jpg`)

### `C11` — Redondilla Escolar / Administrativa de Restauración (Fines s. XIX – 1902) (1870–1902)
* **Motor Kraken destino:** `Motor 3: Decimonónico e Inglesa (1790–1902)`
* **Rasgos morfográficos:** Letra muy clara y reglada, numeración de partidas, mención a juzgados municipales y Registro Civil, páginas pautadas.
* **Escribanos / Autoridades de referencia:** Párrocos de NRDL-BAUT-07 (1865–1889), NRDL-DIFU-05 (1880–1902); Párrocos de JMOL-MATR-03 (1851–1899), JMOL-DIFU-05 (1872–1881) y JMOL-DIFU-06 (1881–1892)
* **Cuadernos canónicos fuente:** `NRDL-BAUT-07`, `NRDL-DIFU-05`, `JMOL-MATR-03`, `JMOL-DIFU-05`, `JMOL-DIFU-06`
* **Muestras `.jpg` verificadas en disco listas para segmentar (`segmentar_lote.py`):**
  - [`004306113_00360.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004306113/004306113_00360.jpg) (`imagenes/rollo 004306113/004306113_00360.jpg`)
  - [`004306113_01420.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004306113/004306113_01420.jpg) (`imagenes/rollo 004306113/004306113_01420.jpg`)
  - [`004298571_00450.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004298571/004298571_00450.jpg) (`imagenes/rollo 004298571/004298571_00450.jpg`)
  - [`004298571_01300.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004298571/004298571_01300.jpg) (`imagenes/rollo 004298571/004298571_01300.jpg`)
  - [`004298571_01450.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004298571/004298571_01450.jpg) (`imagenes/rollo 004298571/004298571_01450.jpg`)

### `C12` — Abecedarios, Índices Tabulares, Listas de Confirmación y Guarismos (1649–1914)
* **Motor Kraken destino:** `Motor 4: Aparato Auxiliar, Índices y Tablas (1594–1914)`
* **Rasgos morfográficos:** Disposición en columnas (Nombre, Padres, Folio, Año), líneas cortas con puntos guía '......', guarismos arábigos de folios y años.
* **Escribanos / Autoridades de referencia:** Compiladores de JMOL-INDICE-BAUT (Bautismos 1750–1914 + Casados 1716–1920); Compiladores de JMOL-INDICE-DIFU (1893–1907); Notarios de Padrones de Confirmación (1649, 1681, 1759, 1776, 1786, 1827, 1850)
* **Cuadernos canónicos fuente:** `JMOL-INDICE-BAUT`, `JMOL-INDICE-DIFU`, `NRDL-BAUT-01`, `NRDL-BAUT-03`, `JMOL-BAUT-03`
* **Muestras `.jpg` verificadas en disco listas para segmentar (`segmentar_lote.py`):**
  - [`004298570_02665.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004298570/004298570_02665.jpg) (`imagenes/rollo 004298570/004298570_02665.jpg`)
  - [`004298570_02750.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004298570/004298570_02750.jpg) (`imagenes/rollo 004298570/004298570_02750.jpg`)
  - [`004298571_01545.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004298571/004298571_01545.jpg) (`imagenes/rollo 004298571/004298571_01545.jpg`)
  - [`004306112_02068.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004306112/004306112_02068.jpg) (`imagenes/rollo 004306112/004306112_02068.jpg`)
  - [`004306112_02114.jpg`](file:///c:/TRABAJOS/personal/genealo/imagenes/rollo 004306112/004306112_02114.jpg) (`imagenes/rollo 004306112/004306112_02114.jpg`)

---

## 3. Cruce de las 33 Auditorías de NotebookLM con los Clusters `C01–C12`

| # | Cuaderno Auditado (`notebook_id`) | Parroquia | Imágenes en Catálogo | Rango Cronológico | Clusters Asignados | Informe de Auditoría Codicológica | Muestras Verificadas en Disco |
| :-: | :--- | :-: | :-: | :-: | :-: | :--- | :--- |

---

## 4. Cómo Preparar un Lote de Entrenamiento de Cualquier Cluster en 3 Comandos

Cuando queramos entrenar o ampliar cualquiera de los 12 clusters (`C01`–`C12`):

1. **Copiar 3–5 imágenes candidatas del cluster** (de la Sección 2 de este documento) a `htr_pipeline/inputs/cluster_CXX/` y **segmentarlas en local con Kraken**:
   ```powershell
   .\.venv\Scripts\python.exe segmentar_lote.py --input-dir htr_pipeline/inputs/cluster_CXX --output-dir htr_pipeline/outputs/cluster_CXX
   ```
2. **Corregir baselines (cortar llaves `}`) y regiones en Aletheia 4.1**, guardar el `.xml` y **recalcular las máscaras poligonales `<Coords>`**:
   ```powershell
   .\.venv\Scripts\python.exe recalcular_mascaras_aletheia.py --xml-dir htr_pipeline/outputs/cluster_CXX
   ```
3. **Pre-transcribir con Gemini Pro (`transcribir_pagexml.py`) y dar el visto bueno final en Aletheia 4.1** para incorporarlo al conjunto de entrenamiento `ketos train`.
