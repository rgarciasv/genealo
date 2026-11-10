"""
Script para descargar de forma automatizada y reproducible los 5 modelos HTR
pre-entrenados del ecosistema Kraken/eScriptorium evaluados en el benchmark:
1. TRIDIS (Zenodo 10788591)
2. CATMuS Medieval (Zenodo 10066219)
3. McCATMuS (Zenodo 13788177)
4. CREMMA ManuMcFondue (Zenodo 10886224)
5. Lectaurep Base (Zenodo 6542744)
"""

import os
import urllib.request

MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")
os.makedirs(MODELS_DIR, exist_ok=True)

MODELS = [
    {
        "id": "tridis",
        "name": "Tridis_Medieval_EarlyModern.mlmodel",
        "url": "https://zenodo.org/api/records/10788591/files/Tridis_Medieval_EarlyModern.mlmodel/content",
        "desc": "TRIDIS (Documental y Notarial s.XII-XVI)",
        "zenodo_id": "10788591"
    },
    {
        "id": "catmus_medieval",
        "name": "CATMUS_Medieval_1.0.0.mlmodel",
        "url": "https://zenodo.org/api/records/10066219/files/CATMUS_Medieval_1.0.0.mlmodel/content",
        "desc": "CATMuS Medieval (Castellano y Latin s.XIII-XVI)",
        "zenodo_id": "10066219"
    },
    {
        "id": "mccatmus",
        "name": "McCATMuS_nfd_nofix_V1.mlmodel",
        "url": "https://zenodo.org/api/records/13788177/files/McCATMuS_nfd_nofix_V1.mlmodel/content",
        "desc": "McCATMuS (Espanol y Romance s.XVI-XIX)",
        "zenodo_id": "13788177"
    },
    {
        "id": "cremma_manumcfondue",
        "name": "ManuMcFondue.mlmodel",
        "url": "https://zenodo.org/api/records/10886224/files/ManuMcFondue.mlmodel/content",
        "desc": "CREMMA ManuMcFondue (Manuscritos Modernos s.XVI-XIX)",
        "zenodo_id": "10886224"
    },
    {
        "id": "lectaurep_base",
        "name": "lectaurep_base.mlmodel",
        "url": "https://zenodo.org/api/records/6542744/files/lectaurep_base.mlmodel/content",
        "desc": "Lectaurep Base (Administrativo y Notarial s.XVIII-XX)",
        "zenodo_id": "6542744"
    }
]

def main():
    print("=" * 70)
    print("DESCARGA DE MODELOS HTR PRE-ENTRENADOS (ZENODO / HTR-UNITED)")
    print(f"Directorio de destino: {MODELS_DIR}")
    print("=" * 70)

    for item in MODELS:
        dest_path = os.path.join(MODELS_DIR, item["name"])
        if os.path.exists(dest_path):
            size_mb = os.path.getsize(dest_path) / (1024 * 1024)
            print(f"[OK] {item['name']} ({item['desc']}) ya existe ({size_mb:.1f} MB).")
            continue

        print(f"\n[DESCARGANDO] {item['name']} desde Zenodo {item['zenodo_id']}...")
        req = urllib.request.Request(item["url"], headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
        try:
            with urllib.request.urlopen(req) as resp, open(dest_path, "wb") as out_f:
                total_bytes = int(resp.headers.get("Content-Length", 0))
                downloaded = 0
                chunk_size = 1024 * 1024
                while True:
                    chunk = resp.read(chunk_size)
                    if not chunk:
                        break
                    out_f.write(chunk)
                    downloaded += len(chunk)
                    if total_bytes:
                        pct = (downloaded / total_bytes) * 100
                        print(f"  Progreso: {downloaded / (1024*1024):.1f}/{total_bytes / (1024*1024):.1f} MB ({pct:.1f}%)", end="\r")
                    else:
                        print(f"  Descargados: {downloaded / (1024*1024):.1f} MB", end="\r")
            print(f"\n[COMPLETADO] {item['name']} guardado con exito.")
        except Exception as e:
            print(f"\n[ERROR] Fallo al descargar {item['name']}: {e}")

if __name__ == "__main__":
    main()
