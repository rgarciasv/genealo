"""Genera docs/MAPA_MUESTREO_CLUSTERS_C01_C12.md cruzando:
1. catalogo_corpus.json (imágenes catalogadas por cuaderno y parroquia)
2. Las 33 auditorías codicológicas en transcripciones/auditoria_codicologica/
3. 03_AUTORIDADES_PALEOGRAFICAS_ALTO_ALBERCHE.md
4. Existencia física real de los archivos .jpg en la carpeta imagenes/

Fuente única de verdad de los 12 clusters (Eje 1: Morfografía pura del trazo):
docs/PIPELINE_HTR_Y_TAXONOMIA_CLUSTERS_PALEOGRAFICOS.md (sección 3).
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CATALOG_PATH = PROJECT_ROOT / "catalogo_corpus.json"
AUDITS_DIR = PROJECT_ROOT / "transcripciones" / "auditoria_codicologica"
IMAGES_DIR = PROJECT_ROOT / "imagenes"
OUTPUT_MD = PROJECT_ROOT / "docs" / "MAPA_MUESTREO_CLUSTERS_C01_C12.md"

MOTOR_1 = "Motor 1: Bloque Antiguo C01–C05 (alto_alberche_antiguo_c01_c05.mlmodel)"
MOTOR_2 = "Motor 2: Bloque Bastardo C06–C10 (alto_alberche_bastardo_c06_c10.mlmodel)"
MOTOR_3 = "Motor 3: Bloque Plumilla Metálica C11 (alto_alberche_plumilla_c11.mlmodel)"
MOTOR_TRANSVERSAL = "Transversal en Motores 1, 2 y 3 (muestras repartidas en todos los bloques)"


# Definición canónica unificada de los 12 Clusters Morfográficos puros (Eje 1: C01–C12)
# Fuente única de verdad: docs/PIPELINE_HTR_Y_TAXONOMIA_CLUSTERS_PALEOGRAFICOS.md (líneas 69–96)
CLUSTERS_SPEC = [
    {
        "id": "C01",
        "motor": MOTOR_1,
        "nombre": "Gótico-cortesana tardía",
        "periodo": "1500–1560 (residual en nuestro corpus desde 1594)",
        "rasgos": "Trazo anguloso y quebrado, módulo pequeño, líneas muy juntas, alta densidad de abreviaturas medievales y signos tironianos (en nuestro corpus aparece como rasgo arcaizante residual en las primeras actas de 1594).",
        "escribanos_clave": [
            "Alonso del Valle (1594, NRDL — cortesana de transición a procesal en los primeros asientos)",
            "Fray Juan de la Cruz (1594, NRDL — mano claustral arcaizante)",
        ],
        "cuadernos": ["NRDL-BAUT-01"],
        "candidatos_preferidos": [
            "004306112_01872.jpg",
            "004306112_01873.jpg",
            "004306112_01903.jpg",
            "004306112_01904.jpg",
            "004306112_01905.jpg",
        ],
    },
    {
        "id": "C02",
        "motor": MOTOR_1,
        "nombre": "Procesal redonda / abierta",
        "periodo": "1530–1620",
        "rasgos": "Formas curvas y anchas, letras aislables pero con nexos envolventes largos. Pluma gruesa de ave.",
        "escribanos_clave": [
            "Fray Francisco de Oropesa (1595–1596, NRDL)",
            "Gaspar Rubiano — primera etapa (1612–1618, NRDL)",
            "Alonso Triguero y Villena (1609–1611, NRDL/JMOL)",
            "Fray Jacinto de Alcocer (1611–1613, NRDL)",
        ],
        "cuadernos": ["NRDL-BAUT-01", "NRDL-MATR-01"],
        "candidatos_preferidos": [
            "004306112_01876.jpg",
            "004306112_01877.jpg",
            "004306112_01912.jpg",
            "004306112_01917.jpg",
            "004306112_01922.jpg",
        ],
    },
    {
        "id": "C03",
        "motor": MOTOR_1,
        "nombre": "Procesal encadenada pura",
        "periodo": "1560–1650",
        "rasgos": "Renglones casi sin levantar la pluma (scriptio continua); c, e, n, m, r, s reducidas a ondas similares.",
        "escribanos_clave": [
            "Joan Martínez [Monterroso] (1596–1604, NRDL — secuencia continua 01878–01891)",
            "Pedro Pérez de las Presas (1627–1634, NRDL)",
            "Andrés Bautista (1653–1658, NRDL)",
        ],
        "cuadernos": ["NRDL-BAUT-01", "NRDL-MATR-01", "JMOL-DIFU-PARVULOS"],
        "candidatos_preferidos": [
            "004306112_01878.jpg",
            "004306112_01881.jpg",
            "004306112_01888.jpg",
            "004306112_01938.jpg",
            "004306112_02080.jpg",
        ],
    },
    {
        "id": "C04",
        "motor": MOTOR_1,
        "nombre": "Humanística / Itálica libraria",
        "periodo": "1550–1640",
        "rasgos": "Vertical o levemente inclinada, letras sueltas casi de imprenta, limpia y sin apenas lazos.",
        "escribanos_clave": [
            "Don Rodrigo Antonio de Meneses (1594, NRDL/JMOL — asiento 6v)",
            "Bachiller Francisco Rodríguez (1598–1607, NRDL)",
            "Bachiller Baltasar de Luján (1600–1606, NRDL/JMOL/NMRL)",
            "Don Marcos Conde (1650–1653, NRDL)",
        ],
        "cuadernos": ["NRDL-BAUT-01", "JMOL-DIFU-PARVULOS", "NRDL-MIXTO-01"],
        "candidatos_preferidos": [
            "004306112_01874.jpg",
            "004306112_01880.jpg",
            "004306112_01884.jpg",
            "004306112_02074.jpg",
            "004298571_00532.jpg",
        ],
    },
    {
        "id": "C05",
        "motor": MOTOR_1,
        "nombre": "Híbrida procesal-bastarda",
        "periodo": "1610–1680",
        "rasgos": "Base inclinada de bastarda con ataduras procesales, d unciales vueltas atrás y abreviaturas arcaicas.",
        "escribanos_clave": [
            "Alonso Hernández (1601–1610, NRDL — superíndices volados extremos)",
            "Francisco Sánchez del Unar (1633–1641, NRDL)",
            "Gaspar González (1640–1642, NRDL)",
            "Fray Mateo del Mazo (1658–1689, NRDL/JMOL)",
        ],
        "cuadernos": ["NRDL-BAUT-01", "NRDL-MATR-01", "NRDL-MIXTO-01", "JMOL-DIFU-PARVULOS"],
        "candidatos_preferidos": [
            "004306112_01895.jpg",
            "004306112_01950.jpg",
            "004306112_02043.jpg",
            "004306112_02053.jpg",
            "004306112_02086.jpg",
        ],
    },
    {
        "id": "C06",
        "motor": MOTOR_2,
        "nombre": "Bastarda cancilleresca / magistral",
        "periodo": "1660–1780",
        "rasgos": "Caja redonda y uniforme, inclinación constante, renglones rectos y separación clara (ej. Domingo Galán, 1710–1711).",
        "escribanos_clave": [
            "Domingo Galán (1710–1711, referencia comarcal)",
            "Domingo Hernández (1666–1680, NRDL)",
            "Lic. Jerónimo Ruiz Núñez (1689–1696, NRDL)",
            "D. Manuel Gil Sánchez y párrocos titulares de NRDL-BAUT-02 / JMOL-BAUT-01",
        ],
        "cuadernos": ["NRDL-BAUT-01", "NRDL-BAUT-02", "JMOL-BAUT-01", "NRDL-MATR-01", "JMOL-MATR-01"],
        "candidatos_preferidos": [
            "004306112_02105.jpg",
            "004306112_02135.jpg",
            "004306112_02230.jpg",
            "004298570_01760.jpg",
            "004298571_00015.jpg",
        ],
    },
    {
        "id": "C07",
        "motor": MOTOR_2,
        "nombre": "Bastarda angulosa / picuda",
        "periodo": "1680–1790",
        "rasgos": "Módulo comprimido lateralmente, picos agudos y aspecto «aserrado», enlaces rápidos (ej. Fray Francisco Martínez, 1716, folio 01608).",
        "escribanos_clave": [
            "Fray Francisco Martínez (1715–1725, JMOL — folio 004298570_01608.jpg)",
            "Lic. Melchor Núñez (1684–1689, NRDL)",
            "Párrocos de JMOL-DIFU-01 y NRDL-DIFU-01",
        ],
        "cuadernos": ["JMOL-BAUT-01", "NRDL-BAUT-01", "NRDL-BAUT-02", "JMOL-DIFU-01", "NRDL-DIFU-01"],
        "candidatos_preferidos": [
            "004298570_01608.jpg",
            "004298570_01615.jpg",
            "004306112_02125.jpg",
            "004298571_00575.jpg",
            "004306113_00420.jpg",
        ],
    },
    {
        "id": "C08",
        "motor": MOTOR_2,
        "nombre": "Bastarda corriente / desbordada",
        "periodo": "1670–1810",
        "rasgos": "Ejecución rápida y descuidada, ojales gigantescos que invaden dos renglones, renglón caído y aglutinaciones (ej. Pedro de la Rebilla, 1710).",
        "escribanos_clave": [
            "Pedro de la Rebilla (1710, referencia comarcal)",
            "Fr. Basilio Herrero Carpio (1717, JMOL — asiento 4 de 01608)",
            "Tenientes y vicarios rápidos de JMOL-BAUT-01, NRDL-BAUT-02 y NRDL-DIFU-01",
        ],
        "cuadernos": ["JMOL-BAUT-01", "NRDL-BAUT-02", "NRDL-DIFU-01", "NRDL-MATR-02", "JMOL-DIFU-02"],
        "candidatos_preferidos": [
            "004298570_01650.jpg",
            "004298570_01720.jpg",
            "004306112_02310.jpg",
            "004306113_00450.jpg",
            "004306113_00750.jpg",
        ],
    },
    {
        "id": "C09",
        "motor": MOTOR_2,
        "nombre": "Micro-cursiva compacta",
        "periodo": "1650–1830",
        "rasgos": "Letra diminuta y empastada por aprovechamiento de espacio o notas marginales densas (ej. Pedro de la Rebilla, 1711).",
        "escribanos_clave": [
            "Pedro de la Rebilla (1711, marginalia densa y aprovechamiento de espacio)",
            "Lic. Joseph Romero de Navas (1682–1684, NRDL — letra menuda muy apretada)",
            "Anotadores de marginales y extractos en NRDL-DIFU-01 / JMOL-DIFU-01 / NRDL-DIFU-02",
        ],
        "cuadernos": ["NRDL-BAUT-01", "JMOL-DIFU-01", "NRDL-DIFU-01", "JMOL-DIFU-02", "NRDL-DIFU-02"],
        "candidatos_preferidos": [
            "004306112_02119.jpg",
            "004306112_02120.jpg",
            "004298571_00650.jpg",
            "004306113_00520.jpg",
            "004306113_00790.jpg",
        ],
    },
    {
        "id": "C10",
        "motor": MOTOR_2,
        "nombre": "Bastarda ilustrada / neoclásica",
        "periodo": "1770–1840",
        "rasgos": "Pluma más fina, limpia, simplificación de abreviaturas y casi sin lazos envolventes.",
        "escribanos_clave": [
            "Párrocos ilustrados de NRDL-BAUT-03 (1750–1803) y NRDL-BAUT-04 (1804–1828)",
            "Párrocos de NRDL-DIFU-01B, NRDL-DIFU-02 y JMOL-MATR-02",
        ],
        "cuadernos": ["NRDL-BAUT-03", "NRDL-BAUT-04", "NRDL-DIFU-01B", "NRDL-DIFU-02", "JMOL-MATR-02"],
        "candidatos_preferidos": [
            "004306112_02410.jpg",
            "004306112_02520.jpg",
            "004306112_02630.jpg",
            "004298571_00250.jpg",
            "004306113_00850.jpg",
        ],
    },
    {
        "id": "C11",
        "motor": MOTOR_3,
        "nombre": "Cursiva inglesa / comercial",
        "periodo": "1840–1899",
        "rasgos": "Plumilla metálica: ascendentes finísimos (vulnerables a mala foto) y descendentes gruesos, muy inclinada (ej. lote_prueba_5: 02637–02641).",
        "escribanos_clave": [
            "Párrocos de JMOL-BAUT-05 (1851–1862, lote_prueba_5: 004298570_02637–02641)",
            "Párrocos de NRDL-BAUT-05, NRDL-BAUT-06, NRDL-BAUT-07 y NRDL-DIFU-05",
            "Párrocos de JMOL-MATR-03, JMOL-DIFU-04, JMOL-DIFU-05 y JMOL-DIFU-06",
        ],
        "cuadernos": ["JMOL-BAUT-05", "NRDL-BAUT-06", "NRDL-BAUT-07", "JMOL-MATR-03", "NRDL-DIFU-05"],
        "candidatos_preferidos": [
            "004298570_02637.jpg",
            "004298570_02638.jpg",
            "004298570_02639.jpg",
            "004306113_00100.jpg",
            "004306113_00360.jpg",
        ],
    },
    {
        "id": "C12",
        "motor": MOTOR_TRANSVERSAL,
        "nombre": "Rústica / senil o temblorosa",
        "periodo": "Transversal",
        "rasgos": "Trazo roto o tembloroso, manchas de goteo y formas irregulares sin escuela clara. Se reparte transversalmente en los Motores 1, 2 y 3.",
        "escribanos_clave": [
            "Gaspar González — 2º ministerio de ancianidad (1672, NRDL — 004306112_02085.jpg)",
            "Simón Palomo Bayala (1683, JMOL/NMRL en NRDL — 004306112_02122.jpg)",
            "Manos temblorosas o rústicas en JMOL-DIFU-03, JMOL-DIFU-04 y NRDL-DIFU-04",
        ],
        "cuadernos": ["NRDL-BAUT-01", "NRDL-MIXTO-01", "JMOL-DIFU-03", "JMOL-DIFU-04", "NRDL-DIFU-04"],
        "candidatos_preferidos": [
            "004306112_02085.jpg",
            "004306112_02122.jpg",
            "004298571_01033.jpg",
            "004298571_01050.jpg",
            "004306113_01020.jpg",
        ],
    },
]

# Asignación verificada de clusters (Eje 1) por cuaderno auditado (Eje 2 separado)
NOTEBOOK_CLUSTER_MAP: dict[str, list[str]] = {
    "JMOL-BAUT-01": ["C06", "C07", "C08"],
    "JMOL-BAUT-02": ["C07", "C08", "C10"],
    "JMOL-BAUT-03": ["C08", "C10", "C11"],
    "JMOL-BAUT-04": ["C10", "C11"],
    "JMOL-BAUT-05": ["C11"],
    "JMOL-DIFU-01": ["C06", "C07", "C08", "C09"],
    "JMOL-DIFU-02": ["C08", "C09", "C10"],
    "JMOL-DIFU-03": ["C11", "C12"],
    "JMOL-DIFU-04": ["C11", "C12"],
    "JMOL-DIFU-05": ["C11"],
    "JMOL-DIFU-06": ["C11"],
    "JMOL-DIFU-PARVULOS": ["C03", "C04", "C05"],
    "JMOL-INDICE-BAUT-MAT": ["C06–C11", "Carril Auxiliar: INDICE"],
    "JMOL-INDICE-DIFU": ["C11", "Carril Auxiliar: INDICE"],
    "JMOL-MATR-01": ["C06", "C07", "C10"],
    "JMOL-MATR-02": ["C08", "C10", "C11"],
    "JMOL-MATR-03": ["C11"],
    "JMOL-MIXTO-04": ["C10", "C11"],
    "NRDL-BAUT-01": ["C01", "C02", "C03", "C04", "C05", "C06", "C12"],
    "NRDL-BAUT-02": ["C06", "C07", "C08", "C09"],
    "NRDL-BAUT-03": ["C07", "C08", "C10"],
    "NRDL-BAUT-05": ["C10", "C11"],
    "NRDL-BAUT-06": ["C11"],
    "NRDL-BAUT-07": ["C11"],
    "NRDL-DIFU-01": ["C06", "C07", "C08", "C09"],
    "NRDL-DIFU-01B": ["C07", "C08", "C10"],
    "NRDL-DIFU-02": ["C08", "C09", "C10"],
    "NRDL-DIFU-03": ["C08", "C10"],
    "NRDL-DIFU-04": ["C11", "C12"],
    "NRDL-DIFU-05": ["C11"],
    "NRDL-MATR-01": ["C03", "C04", "C05", "C06"],
    "NRDL-MATR-02": ["C06", "C07", "C08", "C10"],
    "NRDL-MIXTO-01": ["C04", "C05", "C06", "C12"],
}


def index_local_images() -> dict[str, str]:
    """Devuelve {nombre_archivo.jpg: ruta_relativa_desde_raiz}."""
    mapping: dict[str, str] = {}
    if not IMAGES_DIR.exists():
        return mapping
    for p in IMAGES_DIR.rglob("*.jpg"):
        rel = p.relative_to(PROJECT_ROOT).as_posix()
        mapping[p.name] = rel
    return mapping


def load_catalog_summary() -> dict[str, dict]:
    """Agrupa catalogo_corpus.json por cuaderno_asignado_id."""
    data = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    by_nb: dict[str, dict] = defaultdict(
        lambda: {
            "count": 0,
            "anios": set(),
            "parroquias": set(),
            "tipos": set(),
            "images": [],
        }
    )
    for item in data:
        if item.get("es_descarte"):
            continue
        nb = item.get("cuaderno_asignado_id") or "SIN_CUADERNO"
        entry = by_nb[nb]
        entry["count"] += 1
        if item.get("anios_macro"):
            entry["anios"].add(item["anios_macro"])
        if item.get("parroquia_codigo"):
            entry["parroquias"].add(item["parroquia_codigo"])
        if item.get("tipo_documento"):
            entry["tipos"].add(item["tipo_documento"])
        entry["images"].append(item["id_imagen"])
    return by_nb


def map_notebook_to_clusters(nb_id: str) -> list[str]:
    """Devuelve la lista de IDs de cluster (Eje 1) asociados a un cuaderno."""
    if nb_id in NOTEBOOK_CLUSTER_MAP:
        return NOTEBOOK_CLUSTER_MAP[nb_id]
    if "ENSENADA" in nb_id:
        return ["Carril Independiente: ENSENADA"]
    if "INDICE" in nb_id:
        return ["Carril Auxiliar: INDICE"]
    res = [c["id"] for c in CLUSTERS_SPEC if nb_id in c["cuadernos"]]
    return res or ["C06", "C07"]


def parse_audits() -> list[dict[str, object]]:
    """Lee los 33 archivos *.md de transcripciones/auditoria_codicologica/."""
    audits: list[dict[str, object]] = []
    for p in sorted(AUDITS_DIR.glob("*.md")):
        nb_name = p.stem
        txt = p.read_text(encoding="utf-8", errors="replace")
        imgs_found = re.findall(r"\b004\d{6}_\d{4,5}\.jpg\b", txt)
        sample_imgs: list[str] = []
        for im in imgs_found:
            if im not in sample_imgs:
                sample_imgs.append(im)
            if len(sample_imgs) >= 3:
                break
        audits.append(
            {
                "nb_id": nb_name,
                "file_name": p.name,
                "audit_path": p.relative_to(PROJECT_ROOT).as_posix(),
                "sample_imgs": sample_imgs,
            }
        )
    return audits


def build_markdown() -> str:
    local_imgs = index_local_images()
    cat_by_nb = load_catalog_summary()
    audits = parse_audits()

    lines: list[str] = []
    lines.append("# Mapa Operativo de Muestreo: Los 12 Clusters Morfográficos (`C01–C12`) y los 33 Cuadernos Auditados")
    lines.append("")
    lines.append("> **Propósito:** Este documento conecta directamente todo el trabajo previo de **NotebookLM Pro** (las 33 auditorías codicológicas en [`transcripciones/auditoria_codicologica/`](file:///c:/TRABAJOS/personal/genealo/transcripciones/auditoria_codicologica/), [`03_AUTORIDADES_PALEOGRAFICAS_ALTO_ALBERCHE.md`](file:///c:/TRABAJOS/personal/genealo/03_AUTORIDADES_PALEOGRAFICAS_ALTO_ALBERCHE.md) y [`catalogo_corpus.json`](file:///c:/TRABAJOS/personal/genealo/catalogo_corpus.json)) con archivos `.jpg` reales verificados en disco para entrenar los **3 Motores Kraken Parroquiales** según la taxonomía única de [`docs/PIPELINE_HTR_Y_TAXONOMIA_CLUSTERS_PALEOGRAFICOS.md`](file:///c:/TRABAJOS/personal/genealo/docs/PIPELINE_HTR_Y_TAXONOMIA_CLUSTERS_PALEOGRAFICOS.md).")
    lines.append(">")
    lines.append(f"> **Imágenes físicas indexadas en `imagenes/`:** `{len(local_imgs):,}` archivos `.jpg` verificados en disco local.")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 1. Resumen Ejecutivo: Los 3 Motores Kraken Parroquiales y sus 12 Clusters (`C01–C12`)")
    lines.append("")
    lines.append("| Motor Kraken Parroquial | Clusters Incluidos (Eje 1) | Arco Temporal Típico | Estado Actual de Muestras en Local |")
    lines.append("| :--- | :--- | :--- | :--- |")
    lines.append("| **`Motor 1`: `alto_alberche_antiguo_c01_c05.mlmodel`** | `C01`, `C02`, `C03`, `C04`, `C05` (+ `C12` transversal) | `1594–1680` | Candidatos localizados en disco (`DGS 004306112` y `004298571_00532`). |")
    lines.append("| **`Motor 2`: `alto_alberche_bastardo_c06_c10.mlmodel`** | `C06`, `C07`, `C08`, `C09`, `C10` (+ `C12` transversal) | `1660–1840` | **En marcha:** Folio `004298570_01608` (69 líneas transcritas con 0 errores Unicode, `C07`/`C08`). |")
    lines.append("| **`Motor 3`: `alto_alberche_plumilla_c11.mlmodel`** | `C11` (+ `C12` transversal) | `1840–1902` | **En marcha:** `lote_prueba_5` (`004298570_02637` a `02641`, 5 folios ya segmentados en local, `C11`). |")
    lines.append("")
    lines.append("> **Separación estricta de Ejes y Carriles Independientes (fuera de estos 3 motores parroquiales):**")
    lines.append("> - **Eje 1 (`C01–C12`)** describe exclusivamente la morfografía del trazo; **Eje 2** describe la tipología documental (`BAUTISMO`, `MATRIMONIO`, `DEFUNCION`, Aparato Auxiliar y Catastro de Ensenada).")
    lines.append("> - **Carril Auxiliar (`CONFIRMACION`, `INDICE`, `AUTO_VISITA`, `MEMORIA_MISAS`):** pocos folios y formato especializado; extracción directa con Gemini 4 o motor auxiliar opcional.")
    lines.append("> - **Carril Independiente — Catastro de Ensenada (`ENSENADA_LEGOS` / `ENSENADA_BIENES`):** va por un camino completamente separado de los libros parroquiales (ver Sección 5).")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 2. Catálogo de Muestreo por Cluster (`C01` a `C12`) con Rutas Locales Verificadas")
    lines.append("")

    for c in CLUSTERS_SPEC:
        cid = c["id"]
        lines.append(f"### `{cid}` — {c['nombre']} ({c['periodo']})")
        lines.append(f"* **Motor Kraken destino:** `{c['motor']}`")
        lines.append(f"* **Rasgos morfográficos:** {c['rasgos']}")
        lines.append(f"* **Escribanos / Autoridades de referencia:** {'; '.join(c['escribanos_clave'])}")
        lines.append(f"* **Cuadernos canónicos fuente:** {', '.join(f'`{nb}`' for nb in c['cuadernos'])}")
        lines.append("* **Muestras `.jpg` verificadas en disco listas para segmentar (`segmentar_lote.py`):**")

        verified_samples: list[tuple[str, str]] = []
        for img_name in c["candidatos_preferidos"]:
            if img_name in local_imgs:
                verified_samples.append((img_name, local_imgs[img_name]))
        if len(verified_samples) < 5:
            for nb in c["cuadernos"]:
                nb_imgs = cat_by_nb.get(nb, {}).get("images", [])
                step = max(1, len(nb_imgs) // 5) if nb_imgs else 1
                for im in nb_imgs[::step]:
                    if im in local_imgs and all(im != v[0] for v in verified_samples):
                        verified_samples.append((im, local_imgs[im]))
                        if len(verified_samples) >= 5:
                            break
                if len(verified_samples) >= 5:
                    break

        for img_name, rel_path in verified_samples:
            lines.append(f"  - [`{img_name}`](file:///c:/TRABAJOS/personal/genealo/{rel_path}) (`{rel_path}`)")
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## 3. Cruce de las 33 Auditorías de NotebookLM con los Clusters `C01–C12`")
    lines.append("")
    lines.append("| # | Cuaderno Auditado (`notebook_id`) | Parroquia | Imágenes en Catálogo | Rango Cronológico | Clusters Asignados | Informe de Auditoría Codicológica | Muestras Verificadas en Disco |")
    lines.append("| :-: | :--- | :-: | :-: | :-: | :-: | :--- | :--- |")

    for idx, aud in enumerate(audits, start=1):
        nb_id = str(aud["nb_id"])
        cat_nb = "JMOL-INDICE-BAUT" if nb_id == "JMOL-INDICE-BAUT-MAT" else nb_id
        info = cat_by_nb.get(cat_nb, {})
        count = info.get("count", 0)
        parroquias = ", ".join(sorted(info.get("parroquias", []))) or ("JMOL" if nb_id.startswith("JMOL") else "NRDL")
        anios = ", ".join(sorted(info.get("anios", []))) or "Ver auditoría"
        clusters = ", ".join(f"`{cl}`" for cl in map_notebook_to_clusters(nb_id))
        audit_link = f"[`{aud['file_name']}`](file:///c:/TRABAJOS/personal/genealo/{aud['audit_path']})"

        row_imgs: list[str] = []
        sample_candidates = list(aud["sample_imgs"]) + list(info.get("images", []))[:10]
        for im in sample_candidates:
            if im in local_imgs and im not in row_imgs:
                row_imgs.append(im)
            if len(row_imgs) >= 2:
                break
        imgs_str = ", ".join(f"`{im}`" for im in row_imgs) if row_imgs else "Pendiente descarga local"
        lines.append(
            f"| {idx} | **`{nb_id}`** | `{parroquias}` | {count} | {anios} | {clusters} | {audit_link} | {imgs_str} |"
        )

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 4. Cómo Preparar un Lote de Entrenamiento de Cualquier Cluster en 3 Comandos")
    lines.append("")
    lines.append("Cuando queramos entrenar o ampliar cualquiera de los 12 clusters (`C01`–`C12`):")
    lines.append("")
    lines.append("1. **Copiar 3–5 imágenes candidatas del cluster** (de la Sección 2 de este documento) a `htr_pipeline/inputs/cluster_CXX/` y **segmentarlas en local con Kraken**:")
    lines.append("   ```powershell")
    lines.append("   .\\.venv\\Scripts\\python.exe scripts/htr_kraken/segmentar_lote.py --input-dir htr_pipeline/inputs/cluster_CXX --output-dir htr_pipeline/outputs/cluster_CXX")
    lines.append("   ```")
    lines.append("2. **Corregir baselines (cortar llaves `}`) y regiones en Aletheia 4.1**, guardar el `.xml` y **recalcular las máscaras poligonales `<Coords>`**:")
    lines.append("   ```powershell")
    lines.append("   .\\.venv\\Scripts\\python.exe scripts/htr_kraken/recalcular_mascaras_aletheia.py --xml-dir htr_pipeline/outputs/cluster_CXX")
    lines.append("   ```")
    lines.append("3. **Pre-transcribir con Gemini (`transcribir_pagexml.py`, regla `[L-44]`) y dar el visto bueno final en Aletheia 4.1** para incorporarlo al conjunto de entrenamiento `ketos train`:")
    lines.append("   ```powershell")
    lines.append("   .\\.venv\\Scripts\\python.exe scripts/htr_kraken/transcribir_pagexml.py --image htr_pipeline/inputs/cluster_CXX/<folio>.jpg --xml htr_pipeline/outputs/cluster_CXX/<folio>.xml --output-dir htr_pipeline/outputs/cluster_CXX --mode partida --resolution ultra_high --thinking-level medium")
    lines.append("   ```")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 5. Carriles Independientes fuera de los 3 Motores Parroquiales")
    lines.append("")
    lines.append("### 5.1. Carril Independiente: Catastro del Marqués de la Ensenada (`ENSENADA_LEGOS` / `ENSENADA_BIENES`)")
    lines.append("")
    lines.append("El Catastro de Ensenada (1751–1752) **no forma parte de `C01–C12` parroquiales** y va por un carril HTR completamente separado. Un mismo escribano real de comisión solía redactar todos los volúmenes de un pueblo e incluso de pueblos colindantes; por ello, cuando toque entrenar Kraken para Ensenada, se entrenará aparte **combinando múltiples fondos y manos de Ensenada distintos** para evitar sobreajuste a un único escribano.")
    lines.append("")

    ens_notebooks = sorted(nb for nb in cat_by_nb if "ENSENADA" in nb)
    if ens_notebooks:
        lines.append("| Cuaderno Catastral (`catalogo_corpus.json`) | Territorio | Tipología | Imágenes Catalogadas | Muestras Verificadas en Disco |")
        lines.append("| :--- | :-: | :--- | :-: | :--- |")
        for nb in ens_notebooks:
            info = cat_by_nb[nb]
            parr = ", ".join(sorted(info["parroquias"])) or "ALTO_ALBERCHE"
            tipos = ", ".join(sorted(info["tipos"])) or "ENSENADA"
            samples = [im for im in info["images"] if im in local_imgs]
            pick = samples[len(samples) // 4 : len(samples) // 4 + 2] if samples else []
            s_str = ", ".join(f"[`{im}`](file:///c:/TRABAJOS/personal/genealo/{local_imgs[im]})" for im in pick) or "—"
            lines.append(f"| **`{nb}`** | `{parr}` | `{tipos}` | {info['count']} | {s_str} |")
        lines.append("")

    lines.append("### 5.2. Carril Auxiliar: Aparato Auxiliar (`CONFIRMACION`, `INDICE`, `AUTO_VISITA`, `MEMORIA_MISAS`)")
    lines.append("")
    lines.append("Los índices alfabéticos tabulares, nóminas de confirmaciones, autos de visita pastoral y memorias de misas representan un volumen reducido de folios con estructura especializada. Se procesan en un carril aparte mediante extracción directa con Gemini 4 (o mediante un motor auxiliar opcional dedicado), sin mezclarse con los 3 Motores Parroquiales de series sacramentales narrativas.")
    lines.append("")
    aux_candidates = [
        ("Índice de Bautismos y Matrimonios (`JMOL-INDICE-BAUT`)", "004298570_02665.jpg"),
        ("Índice de Defunciones (`JMOL-INDICE-DIFU`)", "004298571_01545.jpg"),
        ("Padrón de Confirmaciones 1649 (`NRDL-BAUT-01`)", "004306112_02068.jpg"),
        ("Padrón de Confirmaciones 1681 (`NRDL-BAUT-01`)", "004306112_02114.jpg"),
        ("Confirmaciones 1742 (`JMOL-BAUT-01`)", "004298570_01762.jpg"),
    ]
    for label, im in aux_candidates:
        if im in local_imgs:
            rel_path = local_imgs[im]
            lines.append(f"- **{label}:** [`{im}`](file:///c:/TRABAJOS/personal/genealo/{rel_path}) (`{rel_path}`)")
    lines.append("")

    return "\n".join(lines)


def main() -> None:
    md_content = build_markdown()
    OUTPUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_MD.write_text(md_content, encoding="utf-8")
    print(f"Mapa de clusters generado con exito en: {OUTPUT_MD}")


if __name__ == "__main__":
    main()
