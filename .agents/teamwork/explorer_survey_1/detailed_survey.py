import json
import os
import glob
from collections import Counter

CORPUS_PATH = r"c:\TRABAJOS\personal\genealo\catalogo_corpus.json"
BASE_DIR = r"c:\TRABAJOS\personal\genealo"

TARGET_CUADERNOS = [
    "NRDL-ENSENADA-LEGOS-01",
    "JMOL-ENSENADA-LEGOS-01",
    "VLLR-ENSENADA-LEGOS-01",
    "NDRN-ENSENADA-LEGOS-01",
]

TARGET_RANGES = {
    "NRDL-ENSENADA-LEGOS-01": ("004469033", 881, 967, 87),
    "JMOL-ENSENADA-LEGOS-01": ("004469028", 952, 979, 28),
    "VLLR-ENSENADA-LEGOS-01": ("004469028", 901, 951, 51),
    "NDRN-ENSENADA-LEGOS-01": ("004469028", 980, 1013, 34),
}

def main():
    with open(CORPUS_PATH, "r", encoding="utf-8-sig") as f:
        corpus = json.load(f)

    print(f"Total entries in catalogo_corpus.json: {len(corpus)}")

    # Check cuaderno_asignado_id distribution
    cuadernos_count = Counter(item.get("cuaderno_asignado_id") for item in corpus)
    print("\nTarget cuadernos counts in catalogo_corpus.json:")
    for c in TARGET_CUADERNOS:
        print(f"  {c}: {cuadernos_count.get(c, 0)}")

    # Collect entries per target cuaderno
    cuaderno_items = {c: [] for c in TARGET_CUADERNOS}
    for item in corpus:
        cid = item.get("cuaderno_asignado_id")
        if cid in cuaderno_items:
            cuaderno_items[cid].append(item)

    # Validate items in catalogo_corpus against target ranges
    print("\n--- Validating catalogo_corpus entries ---")
    all_target_expected_files = {} # filename -> (cuaderno, item)
    for cid, (dgs, start_f, end_f, expected_count) in TARGET_RANGES.items():
        items = cuaderno_items[cid]
        print(f"\nCuaderno: {cid}")
        print(f"  Items found: {len(items)} (Expected: {expected_count})")
        
        # Sort items by fotograma_numero
        def get_foto(x):
            try:
                return int(x.get("fotograma_numero"))
            except:
                return -1
        items.sort(key=get_foto)
        
        # Check rollos and fotogramas
        rollos = set(x.get("rollo_dgs") for x in items)
        print(f"  Rollos DGS: {rollos} (Expected: {{'{dgs}'}})")
        
        fotogramas = [get_foto(x) for x in items]
        min_f = min(fotogramas) if fotogramas else None
        max_f = max(fotogramas) if fotogramas else None
        print(f"  Fotograma range: {min_f} to {max_f} (Expected: {start_f} to {end_f})")
        
        # Expected list of filenames
        expected_files = [f"{dgs}_{f:05d}.jpg" for f in range(start_f, end_f + 1)]
        actual_files = [f"{x.get('rollo_dgs')}_{int(x.get('fotograma_numero')):05d}.jpg" for x in items if x.get('rollo_dgs') and str(x.get('fotograma_numero')).isdigit()]
        
        missing_in_corpus = set(expected_files) - set(actual_files)
        extra_in_corpus = set(actual_files) - set(expected_files)
        print(f"  Missing in corpus vs expected: {len(missing_in_corpus)} {missing_in_corpus if missing_in_corpus else ''}")
        print(f"  Extra in corpus vs expected: {len(extra_in_corpus)} {extra_in_corpus if extra_in_corpus else ''}")
        
        for exp_fn in expected_files:
            all_target_expected_files[exp_fn] = cid

    print(f"\nTotal expected target files across all 4 cuadernos: {len(all_target_expected_files)}")

    # Now search for physical files on disk
    print("\n--- Scanning physical files on disk ---")
    # Find all jpg files in BASE_DIR
    found_files = {} # filename -> list of absolute paths
    for root, dirs, files in os.walk(BASE_DIR):
        # Skip .git and venv to save time
        if ".git" in root or "venv" in root:
            continue
        for file in files:
            if file.lower().endswith((".jpg", ".jpeg")):
                full_path = os.path.join(root, file)
                if file not in found_files:
                    found_files[file] = []
                found_files[file].append(full_path)

    print(f"Total jpg files found on disk (excluding .git/venv): {sum(len(v) for v in found_files.values())}")
    print(f"Unique jpg filenames found: {len(found_files)}")

    # Check each of the 200 expected files
    print("\n--- Checking physical status of 200 expected images ---")
    status_summary = {
        "found_exact": 0,
        "missing": 0,
        "multiple_locations": 0,
        "zero_bytes": 0,
        "read_error": 0,
    }

    per_cuaderno_file_stats = {c: [] for c in TARGET_CUADERNOS}

    for fn, cid in all_target_expected_files.items():
        paths = found_files.get(fn, [])
        if not paths:
            # Let's check case-insensitive match
            lower_matches = [p for name, pl in found_files.items() if name.lower() == fn.lower() for p in pl]
            if lower_matches:
                paths = lower_matches
                print(f"  [CASE MISMATCH] {fn} found as {[os.path.basename(p) for p in paths]}")
            else:
                status_summary["missing"] += 1
                per_cuaderno_file_stats[cid].append({
                    "filename": fn,
                    "status": "MISSING",
                    "paths": [],
                    "size": 0
                })
                continue

        if len(paths) > 1:
            status_summary["multiple_locations"] += 1

        # Check first path
        first_path = paths[0]
        size = os.path.getsize(first_path)
        if size == 0:
            status_summary["zero_bytes"] += 1
            st = "ZERO_BYTES"
        else:
            # Quick integrity check: can we read first and last bytes (JPEG SOI and EOI markers)
            try:
                with open(first_path, "rb") as img_f:
                    header = img_f.read(2)
                    img_f.seek(-2, os.SEEK_END)
                    footer = img_f.read(2)
                if header != b"\xff\xd8" or footer != b"\xff\xd9":
                    st = f"CORRUPT_JPEG_MARKERS(h={header.hex()}, f={footer.hex()})"
                    status_summary["read_error"] += 1
                else:
                    st = "OK"
                    status_summary["found_exact"] += 1
            except Exception as e:
                st = f"READ_ERROR({e})"
                status_summary["read_error"] += 1

        per_cuaderno_file_stats[cid].append({
            "filename": fn,
            "status": st,
            "paths": paths,
            "size": size,
            "rel_path": os.path.relpath(first_path, BASE_DIR)
        })

    print(f"\nPhysical scan summary:")
    print(f"  Found exact & valid: {status_summary['found_exact']}/200")
    print(f"  Missing: {status_summary['missing']}")
    print(f"  Multiple locations: {status_summary['multiple_locations']}")
    print(f"  Zero bytes: {status_summary['zero_bytes']}")
    print(f"  Read/JPEG format error: {status_summary['read_error']}")

    # Report per cuaderno directory paths and size ranges
    for cid in TARGET_CUADERNOS:
        stats = per_cuaderno_file_stats[cid]
        sizes = [s["size"] for s in stats if s["size"] > 0]
        rel_dirs = set(os.path.dirname(s["rel_path"]) for s in stats if s.get("rel_path"))
        print(f"\nCuaderno {cid}:")
        print(f"  Total verified files: {len([s for s in stats if s['status'] == 'OK'])}/{len(stats)}")
        print(f"  Relative directories: {rel_dirs}")
        if sizes:
            min_mb = min(sizes) / (1024*1024)
            max_mb = max(sizes) / (1024*1024)
            total_mb = sum(sizes) / (1024*1024)
            print(f"  Size range: {min_mb:.2f} MB to {max_mb:.2f} MB (Total: {total_mb:.2f} MB)")

if __name__ == "__main__":
    main()
