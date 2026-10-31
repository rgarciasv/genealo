---
name: reconstruccion-codicologica
description: >-
  Directivas e instrucciones del 'Archivero Virtual' para desarticular códices
  mixtos históricos en series sacramentales puras correlativas en el tiempo
  (Bautismos, Matrimonios, Defunciones) bajo la Regla [L-30]. Gestiona imágenes
  híbridas a doble plana sin cortes físicos JPG bajo la Regla [L-31] (duplicidad
  lógica multi-cuaderno + directiva de extracción por plana). Preserva in situ los
  decretos de Visita Pastoral bajo la Regla [L-32] e identifica lagunas y
  omisiones de microfilmación.
---

# Reconstrucción Codicológica y Desarticulación de Libros Mixtos

Esta skill define el rol del **Archivero Virtual**: la capacidad del agente para analizar la estructura material de los libros parroquiales del Antiguo Régimen, diagnosticar encuadernaciones desordenadas ("cajones de sastre") y reorganizarlos en **series sacramentales puras y cronológicas** sin alterar ni dañar los archivos digitales originales.

---

## 1. El Principio del Archivero Virtual (`[L-30]`)

En los siglos XVI al XVIII, debido a la carestía de papel y a la negligencia de los curas ecónomos, era habitual encuadernar juntos cuadernillos de distintos sacramentos (bautismos, casados y difuntos) en un solo volumen físico.

* **Regla Inmutable:** Cada cuaderno de trabajo en NotebookLM y cada colección en el grafo debe corresponder a una **serie sacramental pura y cronológica** (`BAUT`, `MATR`, `DIFU`) para una única localidad (`[L-29]`).
* **Procedimiento:**
  1. Identificar en el rollo de microfilm los tramos de cada sacramento.
  2. Subir las imágenes de defunciones al cuaderno correspondiente de Defunciones.
  3. Eliminar de los cuadernos de Bautismos los fotogramas que sean 100% defunciones puras (ej. las 57 imágenes segregadas de `NRDL-BAUT-01` hacia `NRDL-DIFU-S17`).
  4. Los inventarios de bienes de la iglesia, padrones y censos se tratan como anexos documentales independientes.

---

## 2. Tratamiento de Imágenes Híbridas (`[L-31]`)

Cuando un fotograma fue fotografiado a doble página abierta y contiene sacramentos diferentes en sus dos caras:
* **Verso (plana izquierda):** ej. últimas partidas de un año de Bautismos.
* **Recto (plana derecha):** ej. arranque de las Defunciones del año siguiente, o un matrimonio suelto.

> [!CAUTION]
> **Prohibición Terminante de Corte Físico:** Queda estrictamente prohibido cortar o dividir físicamente el archivo JPG en dos imágenes. La integridad del archivo `{DGS}_{FOTOGRAMA}.jpg` es sagrada y debe coincidir exactamente con el original de FamilySearch y la URL ARK (`[L-26]`).

* **Protocolo de Duplicidad Lógica:**
  1. La imagen íntegra se incluye como fuente en **ambos** cuadernos (ej. `004306112_02023.jpg` está presente tanto en `NRDL-BAUT-01` como en `NRDL-DIFU-S17`).
  2. En el prompt de extracción se instruye a la IA a transcribir únicamente la plana correspondiente:
     * En el cuaderno de Bautismos: *"Transcribe únicamente la mitad izquierda (verso), omitiendo las defunciones de la derecha"*.
     * En el cuaderno de Defunciones: *"Transcribe únicamente la mitad derecha (recto), omitiendo los bautismos de la izquierda"*.
  3. En la base de datos (ArcadeDB), cada partida se indexa con su metadato de localización física: `lado: "izquierda"` o `lado: "derecha"`.

---

## 3. Conservación de Autos de Visita Pastoral *In Situ* (`[L-32]`)

Los decretos y autos redactados por los visitadores generales y obispos de Ávila que aparecen intercalados en los libros:
* **NO deben moverse a cuadernos externos ni segregarse.**
* **Deben permanecer en su posición cronológica exacta** dentro de la serie sacramental.
* **Justificación archivística:** La Santa Visita es una auditoría canónica contemporánea del cura en ejercicio. Indica si el sacerdote guardaba bien los libros, si mandó poner cerrojo al sagrario, si multó a los feligreses o si mandó rehacer partidas mal redactadas, fijando una fecha topográfica indiscutible.

---

## 4. Auditoría Forense de Lagunas y Omisiones de Microfilm

Al analizar un fondo parroquial, la skill exige comparar la cobertura cronológica entre los tres sacramentos:
1. **Verificar concordancia temporal:** Si Bautismos llega a 1889 y Defunciones a 1902, pero Matrimonios termina en 1803 (como en Navarredondilla), se debe diagnosticar formalmente la **omisión del Libro de Casados del siglo XIX**.
2. **Documentar las causas archivísticas:**
   * Permanencia en el archivo parroquial/sacristía al momento de la filmación.
   * Omisión técnica por parte del fotógrafo de FamilySearch.
   * Pérdida material histórica (humedad, incendio, expolio bélico).
3. **Fijar vías de rescate genealógico:**
   * Expedientes Matrimoniales Diocesanos (Archivo Diocesano de Ávila).
   * Cruce canónico con parroquias matrices o vecinas (`JMOL`, `NMRL`).
   * Registro Civil municipal a partir de 1871.

---

## 5. Scripts de Referencia en el Repositorio

* `scripts/reorganize_nrdl_defunciones_s17.py`: Desarticulación de 57 defunciones puras y unificación de 132 imágenes en `NRDL-DIFU-S17`.
* `scripts/add_marriages_to_matr01.py`: Rescate y adición de folios sueltos de matrimonios al cuaderno `NRDL-MATR-01`.
