# Original User Request

## Initial Request — 2026-10-31T18:37:12Z

Organizar, coordinar y ejecutar mediante agentes especializados la ingesta masiva, validación y verificación E2E de los 17 cuadernos restantes de San Juan del Molinillo en Google NotebookLM Pro para producción, aprovechando los aprendizajes de Navarredondilla.

Working directory: c:\TRABAJOS\personal\genealo
Integrity mode: development

## Verification Resources
- scripts/ingest_sanjuan_parroquial.py: Pipeline de ingesta desatendida con doble checkpoint atómico y resolver dinámico de rutas.
- scripts/ingest_checkpoint_jmol.json: Checkpoint atómico local para seguimiento de fuentes procesadas.
- scripts/verify_sanjuan_parroquial_sources.py: Arnés de verificación independiente para validación de 0 duplicados, 0 faltantes, 0 errores y estado 100% READY.
- catalogo_corpus.json: Catálogo canónico del corpus (2.731 imágenes totales de San Juan del Molinillo divididas en 18 cuadernos sacramentales).

## Requirements

### R1. Ingesta masiva de los 17 cuadernos sacramentales restantes
Ejecutar la ingesta desatendida de las 2.714 fuentes fotográficas restantes en 17 cuadernos sacramentales de San Juan del Molinillo (Bautismos: 6 cuadernos / 1.069 imágenes; Matrimonios y Códice Transición: 4 cuadernos / 617 imágenes; Defunciones restantes: 7 cuadernos / 1.028 imágenes, sumándose al piloto previo JMOL-DIFU-03 de 17 imágenes ya READY). Cumplir la regla de <= 300 fuentes por cuaderno [L-30]/[L-29] y utilizar el perfil persistente de Chromium [L-21].

### R2. Gestión autónoma de fallos, reintentos y persistencia
Garantizar la resiliencia del proceso mediante el checkpoint atómico local (scripts/ingest_checkpoint_jmol.json), gestionando desconexiones, reintentos con backoff y reautenticación automática desatendida sin perder el progreso ni duplicar fuentes.

### R3. Verificación independiente E2E
Ejecutar el arnés de verificación independiente scripts/verify_sanjuan_parroquial_sources.py para certificar el estado de las 2.731 fuentes fotográficas de San Juan del Molinillo en NotebookLM Pro, asegurando cero duplicados, cero faltantes y cero errores con barrera de cuadernos protegidos intacta.

## Acceptance Criteria

### Completitud del Corpus San Juan del Molinillo en NotebookLM Pro
- [ ] Los 17 cuadernos sacramentales restantes están creados e ingestados en Google NotebookLM Pro (totalizando 18 cuadernos sacramentales para San Juan del Molinillo).
- [ ] Las 2.714 fuentes adicionales alcanzan y quedan confirmadas en estado READY (totalizando 2.731 fuentes READY en conjunto con el piloto JMOL-DIFU-03).
- [ ] El archivo scripts/ingest_checkpoint_jmol.json refleja todas las fuentes completadas sin inconsistencias ni duplicados.
- [ ] La ejecución del arnés `python scripts/verify_sanjuan_parroquial_sources.py` finaliza exitosamente con resultado PASS (0 missing, 0 duplicates, 0 errors).

## Follow-up — 2026-10-31T18:45:03Z

Coordinación operativa con el background task en ejecución:
El script `scripts/ingest_sanjuan_parroquial.py` YA SE ENCUENTRA EN EJECUCIÓN en segundo plano (PID activo en background, task-2618).
Actualmente está subiendo imágenes activamente (va por la imagen 66/175 de JMOL-BAUT-01 y actualizando atómicamente scripts/ingest_checkpoint_jmol.json).

IMPORTANTE: NO lanzar un segundo proceso de subida python en paralelo para evitar colisiones de sesión o bloqueos por cuota en la cuenta de Google NotebookLM.
Los agentes del equipo deben enfocar su trabajo en:
1. Supervisar el progreso y la salud de la subida a través de scripts/ingest_checkpoint_jmol.json y scripts/ingest_sanjuan_parroquial.log.
2. Si la sesión de Google expirara por límite de 1 hora ([L-21]), refrescar tokens desatendidamente con `notebooklm login`.
3. Ejecutar y certificar la verificación E2E independiente con `scripts/verify_sanjuan_parroquial_sources.py` una vez completados los cuadernos.
