---
name: auditoria-integridad-corpus
description: >-
  Auditoría forense E2E y certificación de integridad del corpus documental
  parroquial y catastral. Coteja que el 100% de las imágenes físicas en disco
  y en catalogo_corpus.json se encuentren registradas en sus cuadernos correspondientes
  de NotebookLM Pro en estado READY, detectando discrepancias, duplicados remotos
  o fuentes huérfanas.
---

# Auditoría Forense de Integridad del Corpus en NotebookLM

Esta skill proporciona el protocolo de certificación de calidad y verificación extremo a extremo (E2E) para garantizar que los cuadernos en Google NotebookLM Pro contienen de forma exacta, no redundante y completa todas las fuentes documentales requeridas.

---

## 1. Principios de la Auditoría E2E

1. **La Verdad Canónica reside en `catalogo_corpus.json`:**
   * Ningún cuaderno se considera terminado basándose en estimaciones o impresiones del modelo.
   * La validación exige un cruce exhaustivo entre las 8.515 entradas de `catalogo_corpus.json`, los archivos físicos en disco y la lista de fuentes remotas obtenida vía API RPC de NotebookLM.

2. **Criterio de Estado `READY`:**
   * Una fuente no se considera válida simplemente por estar subida; debe haber superado el procesamiento asíncrono de Google Cloud y encontrarse en estado `READY` (o `READY_WITH_WARNINGS`).
   * Las fuentes en estado `PROCESSING` deben monitorizarse con reintentos temporizados (backoff) hasta su estabilización.

3. **Inviolabilidad de Cuadernos Protegidos (`Barrier Shield`):**
   * Todo script de verificación debe comprobar primero que los cuadernos congelados (el piloto fundacional `7967d647` y los libros de Personal Seglar del Catastro de Ensenada) mantienen exactamente su recuento canónico original sin alteraciones.

---

## 2. Detección y Purga de Duplicados Remotos

Si el número de fuentes remotas en un cuaderno supera al esperado en el catálogo:
1. Extraer la lista completa de títulos de fuentes mediante `client.sources.list(notebook_id)`.
2. Contar ocurrencias por nombre de archivo `{DGS}_{FOTOGRAMA}.jpg`.
3. Para cada archivo duplicado, conservar el primer `source_id` registrado en el checkpoint y marcar los restantes para purga.
4. Ejecutar la eliminación atómica con `client.sources.delete(duplicate_source_id)`.
5. Reejecutar el conteo hasta certificar que `total_sources == unique_sources == expected_sources`.

---

## 3. Scripts de Verificación del Repositorio

* **Auditoría de Navarredondilla:**
  ```powershell
  .\venv\Scripts\python.exe scripts/verify_nrdl_parroquial_sources.py
  ```
  Verifica que `NRDL-BAUT-01` posee exactamente 193 fuentes (188 fotogramas + 5 Markdown), `NRDL-DIFU-S17` 132 fuentes, y `NRDL-MATR-01` 36 fuentes, totalizando 2.289 fuentes en los 15 cuadernos de Navarredondilla.

* **Auditoría de San Juan del Molinillo:**
  ```powershell
  .\venv\Scripts\python.exe scripts/verify_sanjuan_parroquial_sources.py
  ```
  Verifica las 2.731 fuentes fotográficas canónicas distribuidas en los 18 cuadernos de Molinillo.

* **Test de Verificación Adversarial:**
  `scripts/test_adversarial_verification.py` inyecta perturbaciones artificiales (IDs falsos, conteos alterados) para demostrar que la suite de tests falla de forma determinista ante cualquier inconsistencia.
