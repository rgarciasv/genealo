# 00_INSTRUCCIONES_PALEOGRAFICAS_V2: REGLAS DE LECTURA Y TRANSCRIPCIÓN

## DIRECTIVA PRINCIPAL PARA EL MOTOR MULTIMODAL
Este documento establece las reglas paleográficas y diplomáticas para transcribir las imágenes manuscritas adjuntas (siglos XVI–XIX, Diócesis de Ávila). El motor debe realizar una **relectura visual directa de alta resolución sobre la imagen**, ignorando interpretaciones modernas erróneas del OCR base.

## 1. ESTRUCTURA FORMULARIA Y TIPOLOGÍAS DOCUMENTALES
1. **Partidas de Bautismo:**
   - **Margen izquierdo (Marginalia):** Contiene el nombre de pila del bautizado, anotaciones de óbito infantil (`+`, `murió`) o notas de dispensa/confirmación.
   - **Cuerpo de la partida:** Fecha expresada en letra (`En [día] dias del mes de [mes] de mill y...`) -> Nombre y cargo del sacerdote oficiante -> Acción (`baptizé / batize a...`) -> Nombre del bautizado -> Filiación (`hijo/a de [Padre] y de su [primera/segunda/legítima] muger [Madre]`, y en el s. XVIII incluye abuelos paternos y maternos) -> Padrinos (`fueron sus padrinos...`), aviso de parentesco espiritual, testigos y firma autógrafa del cura.
2. **Partidas de Matrimonio / Desposorios:**
   - **Margen izquierdo:** Nombres de ambos contrayentes apilados verticalmente (`[contrayente_varón] / y / [contrayente_mujer]`). *(NOTA [L-02]: No reutilizar jamás nombres de ejemplo; leer exclusivamente el margen real del folio).*
   - **Cuerpo:** Fecha -> Oficiante -> Mención a las tres amonestaciones tridentinas -> Acción (`desposé por palabras de presente...` y/o `velé`) -> Nombres de los contrayentes, estado civil previo (soltero/a o viudo/a de `[cónyuge_anterior]`) y filiación de cada uno -> Testigos y firma.
3. **Partidas de Defunción / Entierro:**
   - **Margen izquierdo:** Nombre del difunto, condición (`párvulo`, `pobre`) o cuantía de misas.
   - **Cuerpo:** Fecha de fallecimiento/entierro -> Nombre del difunto, estado civil/filiación -> Recepción de sacramentos, si otorgó testamento o memoria (y ante qué escribano/testigos), sepultura y firma.
4. **Inventarios, Padrones de Confirmación y Autos de Visita:**
   - Listas de alhajas/ornamentos, listas nominales de confirmados (`[confirmado], hijo de [padre] y [madre], padrino [padrino]`) y decretos episcopales en letra procesal notarial.
5. **Distinción Obligatoria entre Redactor Material, Oficiante y Firmas ([L-27]):**
   - Distinguir siempre quién escribe físicamente la partida (**redactor material**) de quién administra el sacramento (**oficiante**). En bautismos oficiados por sacerdotes foráneos o frailes con licencia, el cuerpo del texto suele redactarlo el cura o teniente local, y el oficiante únicamente suscribe al pie. La atribución de ductus corresponde exclusivamente al redactor material.

## 2. NORMAS CALIGRÁFICAS Y ORTOGRÁFICAS (SIGLOS XVI–XVIII)
1. **Alternancia de grafías:** Respetar en la transcripción literal el uso original de `u/v` (`bavtize`), `b/v` betacista (`del balle`), `i/j/y` (`muxer`, `hixo`, `jullio`, `marja`, `m[art]yn`), `c/z/ç` y consonantes dobles (`ss`, `ff`, `tt`).
2. **Soldaduras léxicas:** Mantener en la transcripción literal las uniones de preposición/artículo (`deste`, `destayglesia`, `deldicho`) o separarlas con criterio constante sin alterar las letras.
3. **Abreviaturas de época:** Conservar las abreviaturas con punto o letra volada o desarrollarlas entre corchetes `[ ]`:
   - `dho / dha`: dicho / dicha
   - `Xpo / Xpto / Xpoval`: Cristo / Cristóbal
   - `bap.ze / bap.do`: bauticé / bautizado
   - `igla / ygl[esi]a`: iglesia
   - `v.º / v.ª / v.os`: vecino / vecina / vecinos
   - `fran.co / fran.ca`: Francisco / Francisca
   - `ju.º`: Juan | `al.º`: Alonso | `p.º`: Pedro | `b.me / bar.me`: Bartolomé | `m[art]yn / m.nz`: Martín / Martínez
   - `b.er`: bachiller | `lic.do`: licenciado | `fr.`: fray

## 3. REGLAS ANTI-ALUCINACIÓN Y GESTIÓN DE DAÑOS FÍSICOS (`[L-01, L-05, L-07]`)
1. **Aislamiento del plano frontal:** Ignora el traspaso de tinta ferrogálica invertida procedente del reverso de la hoja (*bleed-through*) y las tarjetas negras/blancas de control de microfilmación (`Página Rota`, `Volumen Entero`).
2. **Prohibición de adivinar en roturas:** Donde falte soporte físico de papel por rotura o roedores, escribe estrictamente **`[ROTO]`**. Donde una mancha de humedad o borrón impida leer, escribe **`[ILEGIBLE]`**.
3. **Declaración obligatoria de dudas (`[L-07]`):** Si una palabra o apellido admite dos lecturas paleográficas razonables por ligadura cursiva, transcríbela como **`[DUDOSO: lectura_1 / lectura_2]`** y explícalo en el campo `Dudas Paleográficas`.
4. **Verificación contra Fuente 01 (`01_DICCIONARIO_ANCLAJE...`):** Antes de dar por válido un año, topónimo o nombre de sacerdote, verifica que cumple el Candado Cronológico y Geográfico de la Fuente 01.
5. **Identificación Inmutable por Nombre Completo de Archivo (`[L-28]`):** La clave primaria y única de cada imagen es su nombre completo de archivo (`{DGS}_{FOTOGRAMA}.jpg`, ej. `004306112_01874.jpg`). Queda terminantemente prohibido truncar o abreviar la referencia al mero número de fotograma (ej. `01874.jpg`), ya que el corpus está distribuido en 9 rollos DGS y la identificación unívoca exige el prefijo del rollo.
6. **Aislamiento por Localidad y Diferenciación de Bienes (`[L-29]`):** Cada cuaderno de trabajo agrupa exclusivamente fuentes de un solo pueblo (`NRDL`, `JMOL`, `NDRN`, `VLLR`, `NMRL`) para preservar la coherencia del escribiente y evitar contaminación toponímica. En el Catastro de Ensenada, los bienes se dividen estrictamente en `BIENES_LEGOS` (seglares) y `BIENES_ECLESIASTICOS` (rentas del clero).
7. **Series Sacramentales Puras y Desarticulación de Códices Mixtos (`[L-30]`):** Cada cuaderno de trabajo corresponde a una serie sacramental única (Bautismos, Matrimonios o Defunciones) correlativa en el tiempo. Si un códice físico histórico contenía varios sacramentos encuadernados juntos, cada sección se procesa en su serie correspondiente; y los documentos extraordinarios no sacramentales (padrones de confirmación, inventarios de bienes de la iglesia, autos de visitas) se tratan como anexos censales e institucionales.
