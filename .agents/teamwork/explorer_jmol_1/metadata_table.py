import json
from collections import defaultdict
from pathlib import Path

BASE_DIR = Path(r"c:\TRABAJOS\personal\genealo")
CATALOG_PATH = BASE_DIR / "catalogo_corpus.json"
IMG_DIR = BASE_DIR / "imagenes"

targets = [
    # Bautismos (6)
    "JMOL-BAUT-01",
    "JMOL-BAUT-02",
    "JMOL-BAUT-03",
    "JMOL-BAUT-04",
    "JMOL-BAUT-05",
    "JMOL-INDICE-BAUT",
    # Matrimonios / Mixto (4)
    "JMOL-MATR-01",
    "JMOL-MATR-02",
    "JMOL-MATR-03",
    "JMOL-MIXTO-04",
    # Defunciones (8)
    "JMOL-DIFU-01",
    "JMOL-DIFU-02",
    "JMOL-DIFU-03",
    "JMOL-DIFU-04",
    "JMOL-DIFU-05",
    "JMOL-DIFU-06",
    "JMOL-DIFU-PARVULOS",
    "JMOL-INDICE-DIFU",
]

def resolve_path(id_img, dgs):
    p = IMG_DIR / f"rollo {dgs}" / id_img
    if p.is_file():
        return p
    for sub in BASE_DIR.iterdir():
        if sub.is_dir() and "San Juan" in sub.name:
            cand = sub / id_img
            if cand.is_file():
                return cand
    raise FileNotFoundError(id_img)

with open(CATALOG_PATH, "r", encoding="utf-8-sig") as f:
    corpus = json.load(f)

by_nb = defaultdict(list)
for r in corpus:
    cid = r.get("cuaderno_asignado_id")
    if cid in targets:
        by_nb[cid].append(r)

lines = [
    "| Cuaderno | Rollo DGS | Fuentes | Rango Fotogramas | Continuidad | Ubicación Física en Disco | Tamaño Total | Promedio / Foto | Mín / Máx Foto | Signatura Archivo | Años Macro | Descripción Elemento |",
    "|---|---|---|---|---|---|---|---|---|---|---|---|"
]

for t in targets:
    recs = by_nb[t]
    recs.sort(key=lambda x: int(x.get("fotograma_numero", 0)))
    dgs = recs[0]["rollo_dgs"]
    frames = [int(r["fotograma_numero"]) for r in recs]
    f_min, f_max = min(frames), max(frames)
    
    # Check continuity
    segments = []
    seg_start = frames[0]
    prev = frames[0]
    for f in frames[1:]:
        if f == prev + 1:
            prev = f
        else:
            segments.append((seg_start, prev))
            seg_start = f
            prev = f
    segments.append((seg_start, prev))
    cont_str = "Continuo" if len(segments) == 1 else f"Discontinuo ({segments})"
    
    # Sizes and locations
    total_b = 0
    min_b = float("inf")
    max_b = 0
    locs = set()
    for r in recs:
        p = resolve_path(r["id_imagen"], dgs)
        sz = p.stat().st_size
        total_b += sz
        min_b = min(min_b, sz)
        max_b = max(max_b, sz)
        locs.add(p.parent.name)
    
    tot_mb = total_b / (1024 * 1024)
    avg_kb = (total_b / len(recs)) / 1024
    min_kb = min_b / 1024
    max_kb = max_b / 1024
    loc_str = "<br>".join(sorted(list(locs)))
    
    r0 = recs[0]
    sig = r0.get("signatura_archivo") or "Sit. Arch. 175/1"
    anios = r0.get("anios_macro") or ""
    desc = r0.get("descripcion_elemento") or ""
    
    lines.append(f"| `{t}` | `{dgs}` | {len(recs)} | {f_min:05d}..{f_max:05d} | {cont_str} | {loc_str} | {tot_mb:.2f} MB | {avg_kb:.1f} KB | {min_kb:.1f} KB / {max_kb:.1f} KB | {sig} | {anios} | {desc} |")

out_path = Path(__file__).parent / "table_output.md"
out_path.write_text("\n".join(lines), encoding="utf-8")
print(f"Wrote {len(lines)} lines to {out_path}")

