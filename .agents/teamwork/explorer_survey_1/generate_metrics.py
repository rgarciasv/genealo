import json
import os

CORPUS_PATH = r"c:\TRABAJOS\personal\genealo\catalogo_corpus.json"
BASE = r"c:\TRABAJOS\personal\genealo"

CONFIGS = [
    {
        "cuaderno_id": "NRDL-ENSENADA-LEGOS-01",
        "localidad": "Navarredondilla",
        "dgs": "004469033",
        "start": 881,
        "end": 967,
        "expected_count": 87,
        "primary_dir": os.path.join(BASE, "imagenes", "rollo 004469033")
    },
    {
        "cuaderno_id": "JMOL-ENSENADA-LEGOS-01",
        "localidad": "San Juan del Molinillo",
        "dgs": "004469028",
        "start": 952,
        "end": 979,
        "expected_count": 28,
        "primary_dir": os.path.join(BASE, "imagenes", "rollo 004469028")
    },
    {
        "cuaderno_id": "VLLR-ENSENADA-LEGOS-01",
        "localidad": "El Villarejo",
        "dgs": "004469028",
        "start": 901,
        "end": 951,
        "expected_count": 51,
        "primary_dir": os.path.join(BASE, "imagenes", "rollo 004469028")
    },
    {
        "cuaderno_id": "NDRN-ENSENADA-LEGOS-01",
        "localidad": "Navandrinal",
        "dgs": "004469028",
        "start": 980,
        "end": 1013,
        "expected_count": 34,
        "primary_dir": os.path.join(BASE, "imagenes", "rollo 004469028")
    }
]

def main():
    with open(CORPUS_PATH, "r", encoding="utf-8-sig") as f:
        corpus = json.load(f)

    grand_total_bytes = 0
    grand_total_files = 0

    results = []

    for cfg in CONFIGS:
        cid = cfg["cuaderno_id"]
        corpus_items = [x for x in corpus if x.get("cuaderno_asignado_id") == cid]
        corpus_filenames = set(x["id_imagen"] for x in corpus_items)
        
        expected_filenames = [f"{cfg['dgs']}_{num:05d}.jpg" for num in range(cfg["start"], cfg["end"] + 1)]
        
        sizes = []
        file_details = []
        for fn in expected_filenames:
            p = os.path.join(cfg["primary_dir"], fn)
            exists = os.path.isfile(p)
            sz = os.path.getsize(p) if exists else 0
            sizes.append(sz)
            file_details.append({
                "filename": fn,
                "exists": exists,
                "size": sz,
                "path": p
            })
            
        total_b = sum(sizes)
        grand_total_bytes += total_b
        grand_total_files += len(expected_filenames)

        res = {
            "cuaderno_id": cid,
            "localidad": cfg["localidad"],
            "expected_count": cfg["expected_count"],
            "corpus_count": len(corpus_items),
            "corpus_matches_expected": corpus_filenames == set(expected_filenames),
            "disk_count_present": sum(1 for d in file_details if d["exists"]),
            "disk_total_bytes": total_b,
            "disk_total_mb": round(total_b / (1024 * 1024), 2),
            "min_size_bytes": min(sizes),
            "max_size_bytes": max(sizes),
            "avg_size_bytes": round(total_b / len(sizes)),
            "primary_dir": cfg["primary_dir"]
        }
        results.append(res)
        print(f"Results for {cid}:", json.dumps(res, indent=2))

    print(f"\nGrand Total Files: {grand_total_files}")
    print(f"Grand Total Bytes: {grand_total_bytes} ({grand_total_bytes / (1024*1024):.2f} MB)")

if __name__ == "__main__":
    main()
