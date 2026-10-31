import json
import os
import re
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

# Map records by id_imagen and by notebook
parroquial_records = [r for r in corpus if r.get("cuaderno_asignado_id") in JMOL_TARGETS]
by_nb = defaultdict(list)
for r in parroquial_records:
    by_nb[r["cuaderno_asignado_id"]].append(r)

print("=== 1. VERIFY PHYSICAL FILES ON DISK ===")
missing_files = []
zero_byte_files = []
corrupt_files = []
file_stats_by_nb = defaultdict(lambda: {"count": 0, "total_bytes": 0, "min_bytes": float("inf"), "max_bytes": 0})
total_bytes_corpus = 0

for nb_id in JMOL_TARGETS:
    recs = by_nb[nb_id]
    recs.sort(key=lambda x: int(x.get("fotograma_numero", 0)))
    for r in recs:
        img_id = r["id_imagen"]
        dgs = r["rollo_dgs"]
        expected_path = IMG_DIR / f"rollo {dgs}" / img_id
        if not expected_path.is_file():
            missing_files.append((nb_id, img_id, str(expected_path)))
            continue
        
        sz = expected_path.stat().st_size
        if sz == 0:
            zero_byte_files.append((nb_id, img_id, str(expected_path)))
            continue
        
        # Check JPEG header SOI (0xFF, 0xD8)
        try:
            with open(expected_path, "rb") as img_f:
                header = img_f.read(2)
                if header != b"\xff\xd8":
                    corrupt_files.append((nb_id, img_id, "Bad SOI"))
                    continue
                # Also check EOI (0xFF, 0xD9) in last 100 bytes
                img_f.seek(-100, os.SEEK_END)
                tail = img_f.read(100)
                if b"\xff\xd9" not in tail:
                    corrupt_files.append((nb_id, img_id, "No EOI in tail"))
        except Exception as e:
            corrupt_files.append((nb_id, img_id, str(e)))
            continue
        
        total_bytes_corpus += sz
        st = file_stats_by_nb[nb_id]
        st["count"] += 1
        st["total_bytes"] += sz
        st["min_bytes"] = min(st["min_bytes"], sz)
        st["max_bytes"] = max(st["max_bytes"], sz)

print(f"Missing files: {len(missing_files)}")
print(f"Zero-byte files: {len(zero_byte_files)}")
print(f"Corrupt files: {len(corrupt_files)}")
print(f"Total verified files on disk: {sum(st['count'] for st in file_stats_by_nb.values())} / 2731")
print(f"Total corpus size on disk: {total_bytes_corpus:,} bytes ({total_bytes_corpus / (1024*1024):.2f} MB / {total_bytes_corpus / (1024*1024*1024):.2f} GB)")

print("\n=== 2. DISK FOLDERS AUDIT (ROLLO 004298570 & ROLLO 004298571) ===")
for dgs in ["004298570", "004298571"]:
    folder = IMG_DIR / f"rollo {dgs}"
    if folder.is_dir():
        all_disk_files = [f for f in folder.iterdir() if f.is_file()]
        jpg_disk_files = [f for f in all_disk_files if f.name.endswith(".jpg")]
        catalog_recs = [r for r in corpus if r.get("rollo_dgs") == dgs]
        catalog_jmol = [r for r in parroquial_records if r.get("rollo_dgs") == dgs]
        print(f"Folder 'rollo {dgs}':")
        print(f"  Total files on disk: {len(all_disk_files)}")
        print(f"  Total .jpg on disk: {len(jpg_disk_files)}")
        print(f"  Total in catalogo_corpus.json for roll {dgs}: {len(catalog_recs)}")
        print(f"  Total JMOL parroquial in roll {dgs}: {len(catalog_jmol)}")
        
        # Check if there are non-JMOL or non-cataloged files in this folder
        catalog_filenames = {r["id_imagen"] for r in catalog_recs}
        jmol_filenames = {r["id_imagen"] for r in catalog_jmol}
        disk_filenames = {f.name for f in jpg_disk_files}
        
        extra_on_disk = disk_filenames - catalog_filenames
        extra_in_catalog = catalog_filenames - disk_filenames
        non_jmol_in_roll = catalog_filenames - jmol_filenames
        print(f"  Disk files not in catalog: {len(extra_on_disk)}")
        print(f"  Catalog files not on disk: {len(extra_in_catalog)}")
        print(f"  Catalog records in roll {dgs} belonging to other notebooks/parishes: {len(non_jmol_in_roll)}")
        if non_jmol_in_roll:
            other_nbs = defaultdict(int)
            for r in catalog_recs:
                if r["id_imagen"] in non_jmol_in_roll:
                    other_nbs[r.get("cuaderno_asignado_id") or "UNASSIGNED"] += 1
            print(f"    Other notebooks in roll {dgs}: {dict(other_nbs)}")

print("\n=== 3. ROOT 'San Juan Bautista...' FOLDERS AUDIT ===")
root_sanjuan_folders = [p for p in BASE_DIR.iterdir() if p.is_dir() and "San Juan" in p.name]
for p in root_sanjuan_folders:
    files = [f for f in p.iterdir() if f.is_file() and f.name.endswith(".jpg")]
    print(f"Root folder '{p.name}': {len(files)} .jpg files")
    # Check if files match roll 004298570 or 004298571
    in_570 = 0
    in_571 = 0
    not_in_canonical = 0
    all_canonical_ids = {r["id_imagen"] for r in parroquial_records}
    for f in files:
        if f.name in all_canonical_ids:
            if f.name.startswith("004298570"):
                in_570 += 1
            elif f.name.startswith("004298571"):
                in_571 += 1
        else:
            not_in_canonical += 1
    print(f"  Matched in canonical JMOL: {in_570} from 004298570, {in_571} from 004298571, Not in canonical JMOL: {not_in_canonical}")

print("\n=== 4. STRUCTURAL ANOMALIES & INTERLEAVING ANALYSIS ===")
# For each roll, sort notebooks by starting frame number and check ranges
for dgs in ["004298570", "004298571"]:
    print(f"\n--- Roll {dgs} Sequence Analysis ---")
    roll_nbs = [nb_id for nb_id in JMOL_TARGETS if by_nb[nb_id] and by_nb[nb_id][0].get("rollo_dgs") == dgs]
    
    nb_spans = []
    for nb_id in roll_nbs:
        recs = by_nb[nb_id]
        frames = [int(r.get("fotograma_numero", 0)) for r in recs]
        frames.sort()
        # Find contiguous segments
        segments = []
        seg_start = frames[0]
        prev = frames[0]
        for f_num in frames[1:]:
            if f_num == prev + 1:
                prev = f_num
            else:
                segments.append((seg_start, prev, prev - seg_start + 1))
                seg_start = f_num
                prev = f_num
        segments.append((seg_start, prev, prev - seg_start + 1))
        nb_spans.append({
            "nb_id": nb_id,
            "count": len(frames),
            "min_frame": min(frames),
            "max_frame": max(frames),
            "span_len": max(frames) - min(frames) + 1,
            "segments": segments,
            "is_continuous": len(segments) == 1
        })
    
    # Sort notebooks by min_frame
    nb_spans.sort(key=lambda x: x["min_frame"])
    for span in nb_spans:
        cont_str = "CONTINUOUS" if span["is_continuous"] else f"DISCONTINUOUS ({len(span['segments'])} segments: {span['segments']})"
        print(f"  {span['nb_id']}: frames {span['min_frame']:05d}..{span['max_frame']:05d} (count={span['count']}, span={span['span_len']}) -> {cont_str}")
    
    # Check overlaps between notebooks
    print("  Checking frame overlaps between notebooks in roll:")
    overlap_found = False
    for i in range(len(nb_spans)):
        for j in range(i + 1, len(nb_spans)):
            a = nb_spans[i]
            b = nb_spans[j]
            # Check if set of frames intersect
            set_a = set()
            for s, e, _ in a["segments"]:
                set_a.update(range(s, e + 1))
            set_b = set()
            for s, e, _ in b["segments"]:
                set_b.update(range(s, e + 1))
            inter = set_a.intersection(set_b)
            if inter:
                print(f"    WARNING: Overlap between {a['nb_id']} and {b['nb_id']}: {len(inter)} frames {sorted(list(inter))[:5]}...")
                overlap_found = True
            # Also check if range interleaved
            if a["max_frame"] > b["min_frame"]:
                print(f"    NOTE: Interleaved span between {a['nb_id']} (max={a['max_frame']}) and {b['nb_id']} (min={b['min_frame']})")
                overlap_found = True
    if not overlap_found:
        print("    No frame overlaps or interleaving between notebooks in this roll.")

print("\n=== 5. PER-NOTEBOOK METRICS TABLE ===")
print("| Notebook ID | Rollo DGS | Sources | Frame Range | Continuity | Total Size (MB) | Avg / Photo (KB) | Min / Max (KB) | <=300? | Title / Metadata |")
print("|---|---|---|---|---|---|---|---|---|---|")
for nb_id in JMOL_TARGETS:
    recs = by_nb[nb_id]
    recs.sort(key=lambda x: int(x.get("fotograma_numero", 0)))
    frames = [int(r.get("fotograma_numero", 0)) for r in recs]
    dgs = recs[0]["rollo_dgs"]
    st = file_stats_by_nb[nb_id]
    total_mb = st["total_bytes"] / (1024 * 1024)
    avg_kb = (st["total_bytes"] / st["count"]) / 1024 if st["count"] else 0
    min_kb = st["min_bytes"] / 1024 if st["count"] else 0
    max_kb = st["max_bytes"] / 1024 if st["count"] else 0
    
    # Continuity
    segments = []
    seg_start = frames[0]
    prev = frames[0]
    for f_num in frames[1:]:
        if f_num == prev + 1:
            prev = f_num
        else:
            segments.append((seg_start, prev))
            seg_start = f_num
            prev = f_num
    segments.append((seg_start, prev))
    cont_str = "Continuo" if len(segments) == 1 else f"Discontinuo ({len(segments)} tramos: {segments})"
    
    # Title / meta
    sample_r = recs[0]
    titulo = sample_r.get("titulo_volumen") or sample_r.get("seccion") or sample_r.get("cuaderno_asignado_titulo") or ""
    anos = f"{sample_r.get('ano_inicial', '')}-{sample_r.get('ano_final', '')}"
    sig = sample_r.get("signatura_archivo", "")
    meta_str = f"{titulo} ({anos})" if anos != "-" else titulo
    if sig:
        meta_str += f" [{sig}]"
    
    under_300 = "PASS (<=300)" if len(recs) <= 300 else "FAIL (>300)"
    
    print(f"| `{nb_id}` | `{dgs}` | {len(recs)} | {min(frames)}..{max(frames)} | {cont_str} | {total_mb:.2f} MB | {avg_kb:.1f} KB | {min_kb:.1f} / {max_kb:.1f} KB | {under_300} | {meta_str} |")
