import json
import os
import re
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path(r"c:\TRABAJOS\personal\genealo")
CATALOG_PATH = BASE_DIR / "catalogo_corpus.json"
JMOL_TARGETS = [
    "JMOL-BAUT-01",
    "JMOL-BAUT-02",
    "JMOL-BAUT-03",
    "JMOL-BAUT-04",
    "JMOL-BAUT-05",
    "JMOL-INDICE-BAUT",
    "JMOL-MATR-01",
    "JMOL-MATR-02",
    "JMOL-MATR-03",
    "JMOL-DIFU-01",
    "JMOL-DIFU-02",
    "JMOL-DIFU-03",
    "JMOL-DIFU-04",
    "JMOL-DIFU-05",
    "JMOL-DIFU-06",
    "JMOL-DIFU-PARVULOS",
    "JMOL-INDICE-DIFU",
    "JMOL-MIXTO-04",
]

print("=== STEP 1: LOAD CANONICAL CATALOG ===")
with open(CATALOG_PATH, "r", encoding="utf-8-sig") as f:
    corpus = json.load(f)

print(f"Total entries in catalogo_corpus.json: {len(corpus)}")

# Check all entries related to JMOL
all_jmol_entries = [r for r in corpus if (r.get("cuaderno_asignado_id") or "").startswith("JMOL-")]
print(f"Total entries starting with JMOL-: {len(all_jmol_entries)}")

# Group by cuaderno_asignado_id
by_notebook = defaultdict(list)
for r in all_jmol_entries:
    by_notebook[r.get("cuaderno_asignado_id")].append(r)

print("Notebooks found starting with JMOL-:")
for nb_id, recs in sorted(by_notebook.items()):
    print(f"  {nb_id}: {len(recs)} records")

# Check Ensenada Legos or other notebooks
ensenada_jmol = by_notebook.get("JMOL-ENSENADA-LEGOS-01", [])
print(f"JMOL-ENSENADA-LEGOS-01 count: {len(ensenada_jmol)}")

# Check target 18 notebooks
parroquial_records = []
target_counts = {}
for nb_id in JMOL_TARGETS:
    recs = by_notebook.get(nb_id, [])
    target_counts[nb_id] = len(recs)
    parroquial_records.extend(recs)

print(f"\nTotal records in 18 sacramental target notebooks: {len(parroquial_records)}")
print(f"Target counts: {target_counts}")

# Check duplicate id_imagen
id_images = [r.get("id_imagen") for r in parroquial_records]
unique_id_images = set(id_images)
duplicates = len(id_images) - len(unique_id_images)
print(f"Total id_imagen: {len(id_images)}, Unique: {len(unique_id_images)}, Duplicates: {duplicates}")

# Check es_descarte
descartes = [r for r in parroquial_records if r.get("es_descarte") is True]
print(f"Descartes count: {len(descartes)}")

# Check naming L-28: ^\d{9}_\d{5}\.jpg$
l28_regex = re.compile(r"^\d{9}_\d{5}\.jpg$")
l28_violations = [img for img in id_images if not l28_regex.match(img)]
print(f"L-28 violations: {len(l28_violations)}")

# Check rollos across parroquial
rollos_parroquial = defaultdict(list)
for r in parroquial_records:
    rollos_parroquial[r.get("rollo_dgs")].append(r)

print("\nRollos present in 18 JMOL sacramental notebooks:")
for r_dgs, recs in sorted(rollos_parroquial.items()):
    print(f"  Rollo {r_dgs}: {len(recs)} records")

print("\nDone step 1.")
