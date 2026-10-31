import os
import json
import hashlib

CORPUS_PATH = r"c:\TRABAJOS\personal\genealo\catalogo_corpus.json"
BASE = r"c:\TRABAJOS\personal\genealo"

def md5_file(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def main():
    with open(CORPUS_PATH, "r", encoding="utf-8-sig") as f:
        corpus = json.load(f)

    catastro_dir = os.path.join(BASE, "catastro ensenada Navarredondilla")
    rollo33_dir = os.path.join(BASE, "imagenes", "rollo 004469033")
    rollo28_dir = os.path.join(BASE, "imagenes", "rollo 004469028")

    nrdl_items = [x for x in corpus if x.get("cuaderno_asignado_id") == "NRDL-ENSENADA-LEGOS-01"]
    
    in_cat_only = []
    in_r33_only = []
    in_both = []

    print(f"Total NRDL items: {len(nrdl_items)}")
    for x in nrdl_items:
        fn = f"{x['rollo_dgs']}_{int(x['fotograma_numero']):05d}.jpg"
        p_cat = os.path.join(catastro_dir, fn)
        p_r33 = os.path.join(rollo33_dir, fn)
        has_cat = os.path.isfile(p_cat)
        has_r33 = os.path.isfile(p_r33)

        if has_cat and has_r33:
            md5_c = md5_file(p_cat)
            md5_r = md5_file(p_r33)
            same = (md5_c == md5_r)
            in_both.append((fn, same, os.path.getsize(p_cat), os.path.getsize(p_r33)))
        elif has_cat:
            in_cat_only.append((fn, p_cat))
        elif has_r33:
            in_r33_only.append((fn, p_r33))
        else:
            print(f"MISSING: {fn}")

    print(f"NRDL in_both: {len(in_both)} (all identical MD5? {all(x[1] for x in in_both)})")
    print(f"NRDL in_cat_only: {len(in_cat_only)}")
    print(f"NRDL in_r33_only: {len(in_r33_only)}")

    if in_both:
        print("Sample in_both (first 3):", [x[0] for x in in_both[:3]])
    if in_cat_only:
        print("Sample in_cat_only (first 3):", [x[0] for x in in_cat_only[:3]])
    if in_r33_only:
        print("Sample in_r33_only (first 3):", [x[0] for x in in_r33_only[:3]])

    # Also inspect JMOL, VLLR, NDRN
    for cid in ["JMOL-ENSENADA-LEGOS-01", "VLLR-ENSENADA-LEGOS-01", "NDRN-ENSENADA-LEGOS-01"]:
        c_items = [x for x in corpus if x.get("cuaderno_asignado_id") == cid]
        missing = []
        for x in c_items:
            fn = f"{x['rollo_dgs']}_{int(x['fotograma_numero']):05d}.jpg"
            p_r28 = os.path.join(rollo28_dir, fn)
            if not os.path.isfile(p_r28):
                missing.append(fn)
        print(f"{cid}: {len(c_items)} items, missing in rollo28: {len(missing)}")

if __name__ == "__main__":
    main()
