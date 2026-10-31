import json
import os
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path(r"c:\TRABAJOS\personal\genealo")
CATALOG_PATH = BASE_DIR / "catalogo_corpus.json"
IMG_DIR = BASE_DIR / "imagenes"

JMOL_TARGETS = [
    # Bautismos (6 notebooks)
    "JMOL-BAUT-01",
    "JMOL-BAUT-02",
    "JMOL-BAUT-03",
    "JMOL-BAUT-04",
    "JMOL-BAUT-05",
    "JMOL-INDICE-BAUT",
    # Matrimonios / Mixto (4 notebooks)
    "JMOL-MATR-01",
    "JMOL-MATR-02",
    "JMOL-MATR-03",
    "JMOL-MIXTO-04",
    # Defunciones (8 notebooks)
    "JMOL-DIFU-01",
    "JMOL-DIFU-02",
    "JMOL-DIFU-03",
    "JMOL-DIFU-04",
    "JMOL-DIFU-05",
    "JMOL-DIFU-06",
    "JMOL-DIFU-PARVULOS",
    "JMOL-INDICE-DIFU",
]

with open(CATALOG_PATH, "r", encoding="utf-8-sig") as f:
    corpus = json.load(f)

parroquial_records = [r for r in corpus if r.get("cuaderno_asignado_id") in JMOL_TARGETS]
by_nb = defaultdict(list)
for r in parroquial_records:
    by_nb[r["cuaderno_asignado_id"]].append(r)

# Dynamic resolver as in ingest_sanjuan_parroquial.py
def resolve_image_path(id_img: str, dgs: str) -> Path:
    search_paths = [
        BASE_DIR / "imagenes" / f"rollo {dgs}" / id_img,
    ]
    for p in BASE_DIR.iterdir():
        if p.is_dir() and "San Juan" in p.name:
            search_paths.append(p / id_img)

    for p in search_paths:
        if p.is_file():
            return p
    raise FileNotFoundError(f"Missing: {id_img}")

print("=== RESOLVING ALL 2,731 IMAGES VIA MULTI-PATH RESOLVER ===")
missing = []
zero_byte = []
corrupt = []
location_counts = defaultdict(int)
stats_by_nb = defaultdict(lambda: {"count": 0, "total_bytes": 0, "min_bytes": float("inf"), "max_bytes": 0, "locations": set()})
total_bytes = 0

for nb_id in JMOL_TARGETS:
    recs = by_nb[nb_id]
    recs.sort(key=lambda x: int(x.get("fotograma_numero", 0)))
    for r in recs:
        img_id = r["id_imagen"]
        dgs = r["rollo_dgs"]
        try:
            p = resolve_image_path(img_id, dgs)
        except FileNotFoundError:
            missing.append((nb_id, img_id))
            continue
        
        loc_parent = p.parent.name
        location_counts[loc_parent] += 1
        
        sz = p.stat().st_size
        if sz == 0:
            zero_byte.append((nb_id, img_id, str(p)))
            continue
        
        # Binary check
        try:
            with open(p, "rb") as f:
                head = f.read(2)
                if head != b"\xff\xd8":
                    corrupt.append((nb_id, img_id, "Bad SOI"))
                    continue
                f.seek(-100, os.SEEK_END)
                tail = f.read(100)
                if b"\xff\xd9" not in tail:
                    corrupt.append((nb_id, img_id, "No EOI in tail"))
        except Exception as e:
            corrupt.append((nb_id, img_id, str(e)))
            continue
        
        total_bytes += sz
        st = stats_by_nb[nb_id]
        st["count"] += 1
        st["total_bytes"] += sz
        st["min_bytes"] = min(st["min_bytes"], sz)
        st["max_bytes"] = max(st["max_bytes"], sz)
        st["locations"].add(loc_parent)

print(f"Total resolved: {sum(st['count'] for st in stats_by_nb.values())} / 2731")
print(f"Missing: {len(missing)}")
print(f"Zero-byte: {len(zero_byte)}")
print(f"Corrupt: {len(corrupt)}")
print(f"Total size across all locations: {total_bytes:,} bytes ({total_bytes / (1024*1024):.2f} MB / {total_bytes / (1024*1024*1024):.2f} GB)")

print("\nDistribution of files across disk locations:")
for loc, cnt in sorted(location_counts.items()):
    print(f"  {loc}: {cnt} files")

print("\nPer-notebook details:")
print("| Notebook ID | Rollo DGS | Sources | Frame Range | Continuity | Location(s) on Disk | Total MB | Avg KB | Min/Max KB |")
print("|---|---|---|---|---|---|---|---|---|")
for nb_id in JMOL_TARGETS:
    recs = by_nb[nb_id]
    recs.sort(key=lambda x: int(x.get("fotograma_numero", 0)))
    frames = [int(r.get("fotograma_numero", 0)) for r in recs]
    dgs = recs[0]["rollo_dgs"]
    st = stats_by_nb[nb_id]
    tot_mb = st["total_bytes"] / (1024 * 1024)
    avg_kb = (st["total_bytes"] / st["count"]) / 1024 if st["count"] else 0
    min_kb = st["min_bytes"] / 1024 if st["count"] else 0
    max_kb = st["max_bytes"] / 1024 if st["count"] else 0
    locs_str = ", ".join(sorted(list(st["locations"])))
    print(f"| `{nb_id}` | `{dgs}` | {len(recs)} | {min(frames):05d}..{max(frames):05d} | Continuo | {locs_str} | {tot_mb:.2f} MB | {avg_kb:.1f} KB | {min_kb:.1f} / {max_kb:.1f} KB |")

