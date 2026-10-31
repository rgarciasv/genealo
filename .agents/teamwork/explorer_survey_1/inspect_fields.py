import json

CORPUS_PATH = r"c:\TRABAJOS\personal\genealo\catalogo_corpus.json"

def main():
    with open(CORPUS_PATH, "r", encoding="utf-8-sig") as f:
        corpus = json.load(f)

    for cid in ["NRDL-ENSENADA-LEGOS-01", "JMOL-ENSENADA-LEGOS-01", "VLLR-ENSENADA-LEGOS-01", "NDRN-ENSENADA-LEGOS-01"]:
        items = [x for x in corpus if x.get("cuaderno_asignado_id") == cid]
        print(f"\n--- Cuaderno {cid} (Sample item) ---")
        if items:
            item = items[0]
            for k, v in item.items():
                print(f"  {k}: {repr(v)}")

if __name__ == "__main__":
    main()
