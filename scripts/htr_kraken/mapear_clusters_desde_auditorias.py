"""Genera docs/MAPA_MUESTREO_CLUSTERS_C01_C12.md cruzando:
1. catalogo_corpus.json (8.515+ imágenes catalogadas)
2. Las 33 auditorías codicológicas en transcripciones/auditoria_codicologica/
3. 03_AUTORIDADES_PALEOGRAFICAS_ALTO_ALBERCHE.md
4. Existencia física real de los archivos .jpg en la carpeta imagenes/
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


# Definición canónica de los 12 Clusters Morfográficos y su asignación a los 4 Motores Kraken
CLUSTERS_SPEC = [
    {
        "id": "C01",
        "motor": "Motor 1: Procesal y Transición (1590–1660)",
        "nombre": "Procesal Encadenada Pura y Cortesana Tardía",
        "periodo": "1594–1635",
        "rasgos": "Trazos ligados sin levantar pluma, bucles envolventes, ojos cerrados, abreviaturas por suspensión y sobrelineado continuo.",
        "escribanos_clave": [
            "Joan Martínez [Monterroso] (1596–1604, NRDL)",
            "Francisco Ximénez (1594–1595, NRDL)",
            "Alonso Hernández (1601–1610, NRDL)",
            "Pedro Pérez de las Presas (1627–1634, NRDL)",
        ],
        "cuadernos": ["NRDL-BAUT-01", "Lib. Baut. Navarre Vol. 1 (1594-1695)"],
        "candidatos_preferidos": [
            "004306112_01874.jpg",
            "004306112_01878.jpg",
            "004306112_01881.jpg",
            "004306112_01895.jpg",
            "004306112_01938.jpg",
        ],
    },
    {
        "id": "C02",
        "motor": "Motor 1: Procesal y Transición (1590–1660)",
        "nombre": "Procesal Redonda / Semigótica / Claustral de Transición",
        "periodo": "1594–1650",
        "rasgos": "Módulo amplio y redondo, letras más sueltas que la encadenada, influencia humanística o monástica (Burgohondo/Oropesa).",
        "escribanos_clave": [
            "Alonso del Valle (1594, NRDL)",
            "Fray Francisco de Oropesa (1595–1596, NRDL)",
            "Gaspar Rubiano (1612–1626, NRDL)",
            "Gaspar González (1640–1642, NRDL)",
        ],
        "cuadernos": ["NRDL-BAUT-01", "NRDL-MATR-01", "NRDL-DIFU-S17 (1631-1701)"],
        "candidatos_preferidos": [
            "004306112_01873.jpg",
            "004306112_01876.jpg",
            "004306112_01922.jpg",
            "004306112_01960.jpg",
            "004306112_02043.jpg",
        ],
    },
    {
        "id": "C03",
        "motor": "Motor 1: Procesal y Transición (1590–1660)",
        "nombre": "Humanística / Itálica Temprana y Bastarda de Transición",
        "periodo": "1635–1675",
        "rasgos": "Inclinación derecha moderada, desaparición del bucle procesal envolvente, astas altas limpias, separación clara de palabras.",
        "escribanos_clave": [
            "Francisco Sánchez del Unar (1633–1641, NRDL)",
            "Don Marcos Conde (1650–1653, NRDL)",
            "Andrés Bautista (1653–1658, NRDL)",
            "Fray Mateo del Mazo (1658–1689, NRDL/JMOL)",
        ],
        "cuadernos": ["NRDL-BAUT-01", "NRDL-MATR-01", "JMOL-DIFU-PARVULOS"],
        "candidatos_preferidos": [
            "004306112_01950.jpg",
            "004306112_02053.jpg",
            "004306112_02074.jpg",
            "004306112_02080.jpg",
            "004298571_00532.jpg",
        ],
    },
    {
        "id": "C04",
        "motor": "Motor 2: Bastarda Española y Cancilleresca (1660–1790)",
        "nombre": "Bastarda Española Clásica de Párroco (Fines s. XVII – 1ª mitad s. XVIII)",
        "periodo": "1675–1745",
        "rasgos": "Letra bastarda asentada, contraste medio de pluma, superíndices volados constantes (franᶜº, lexᵐª, vºˢ), caja regular.",
        "escribanos_clave": [
            "Domingo Hernández (1666–1680, NRDL)",
            "Lic. Melchor Núñez (1684–1689, NRDL)",
            "Lic. Jerónimo Ruiz Núñez (1689–1696, NRDL)",
            "Fray Francisco Martínez (1715–1725, JMOL — Folios tipo 01608)",
        ],
        "cuadernos": ["NRDL-BAUT-01", "NRDL-BAUT-02", "JMOL-BAUT-01", "JMOL-MATR-01", "JMOL-DIFU-01"],
        "candidatos_preferidos": [
            "004298570_01608.jpg",
            "004306112_02105.jpg",
            "004306112_02135.jpg",
            "004306112_02230.jpg",
            "004298571_00015.jpg",
        ],
    },
    {
        "id": "C05",
        "motor": "Motor 2: Bastarda Española y Cancilleresca (1660–1790)",
        "nombre": "Bastarda Cursiva / Barroca Densa y Tenientes Auxiliares",
        "periodo": "1680–1765",
        "rasgos": "Mayor velocidad de trazo, astas ascendentes y descendentes largas que invaden líneas contiguas, tinta a veces pálida o ferrogálica densa.",
        "escribanos_clave": [
            "Fr. Basilio Herrero Carpio (1717, JMOL — Partida 4 de 01608)",
            "Tenientes y vicarios de NRDL-BAUT-02 y NRDL-DIFU-01",
            "Escribanos de JMOL-BAUT-01 (tramo 1730–1752) y JMOL-DIFU-01",
        ],
        "cuadernos": ["JMOL-BAUT-01", "NRDL-BAUT-02", "NRDL-DIFU-01", "NRDL-MATR-02"],
        "candidatos_preferidos": [
            "004298570_01650.jpg",
            "004298570_01720.jpg",
            "004306112_02310.jpg",
            "004306113_00450.jpg",
            "004306113_00750.jpg",
        ],
    },
    {
        "id": "C06",
        "motor": "Motor 2: Bastarda Española y Cancilleresca (1660–1790)",
        "nombre": "Bastarda Cancilleresca de Escribano Real (Catastro de Ensenada)",
        "periodo": "1751–1752",
        "rasgos": "Caligrafía profesional de escribano de comisión: márgenes amplios con llaves y linderos (L., P., M., N.), guarismos de fanegas/celemines y reales.",
        "escribanos_clave": [
            "Escribanos Reales del Catastro de Ensenada (Navarredondilla, Molinillo, Navandrinal, El Villarejo, Navalmoral)",
        ],
        "cuadernos": [
            "NRDL-ENSENADA-LEGOS-01",
            "JMOL-ENSENADA-LEGOS-01",
            "NDRN-ENSENADA-LEGOS-01",
            "VLLR-ENSENADA-LEGOS-01",
            "NMRL-ENSENADA-LEGOS-01",
        ],
        "candidatos_preferidos": [
            "004469033_00890.jpg",
            "004469028_00910.jpg",
            "004469028_00960.jpg",
            "004469028_00990.jpg",
            "004469027_01840.jpg",
        ],
    },
    {
        "id": "C07",
        "motor": "Motor 2: Bastarda Española y Cancilleresca (1660–1790)",
        "nombre": "Bastarda Ilustrada Estandarizada (2ª mitad s. XVIII)",
        "periodo": "1752–1803",
        "rasgos": "Letra limpia, escolarizada según arte de Palomares/Anduaga, renglones muy rectos, estructura de partida con abuelos paternos y maternos.",
        "escribanos_clave": [
            "Párrocos ilustrados de NRDL-BAUT-03 (1750–1803) y JMOL-BAUT-02 (1752–1800)",
            "Párrocos de NRDL-DIFU-01B / NRDL-DIFU-02 y JMOL-DIFU-02",
        ],
        "cuadernos": ["NRDL-BAUT-03", "JMOL-BAUT-02", "NRDL-DIFU-01B", "JMOL-MATR-01", "JMOL-DIFU-02"],
        "candidatos_preferidos": [
            "004306112_02410.jpg",
            "004306112_02520.jpg",
            "004298570_01820.jpg",
            "004298570_01950.jpg",
            "004298571_00600.jpg",
        ],
    },
    {
        "id": "C08",
        "motor": "Motor 3: Decimonónico e Inglesa (1790–1902)",
        "nombre": "Bastarda Tardía / Transición Liberal (1800–1840)",
        "periodo": "1800–1840",
        "rasgos": "Transición entre la pluma de ave tardía y las primeras plumillas metálicas; aparición frecuente de llaves marginales '}' separando el índice.",
        "escribanos_clave": [
            "Párrocos de NRDL-BAUT-04 (1804–1828) y JMOL-BAUT-03 (1801–1826)",
            "Párrocos de JMOL-MATR-02 (1790–1852) y NRDL-DIFU-02 (1802–1831)",
        ],
        "cuadernos": ["NRDL-BAUT-04", "JMOL-BAUT-03", "JMOL-MATR-02", "NRDL-DIFU-02"],
        "candidatos_preferidos": [
            "004306112_02630.jpg",
            "004306112_02740.jpg",
            "004298570_02100.jpg",
            "004298571_00250.jpg",
            "004306113_00850.jpg",
        ],
    },
    {
        "id": "C09",
        "motor": "Motor 3: Decimonónico e Inglesa (1790–1902)",
        "nombre": "Cursiva Inglesa / Comercial Aguda con Llave Marginal '}' (Mediados s. XIX)",
        "periodo": "1835–1870",
        "rasgos": "Plumilla metálica fina, inclinación marcada a la derecha, llaves '}' entre margen_indice y cuerpo_partida (como el lote_prueba_5: 02637–02641).",
        "escribanos_clave": [
            "D. Marcelino Tore Díaz y sucesores en JMOL-BAUT-04 (1827–1852) y JMOL-BAUT-05 (1851–1862)",
            "Expediente Episcopal JMOL-SACRAMENTAL-1842-1850",
            "Párrocos de NRDL-BAUT-05 (1829–1852) y NRDL-BAUT-06 (1852–1865)",
        ],
        "cuadernos": ["JMOL-BAUT-04", "JMOL-BAUT-05", "JMOL-SACRAMENTAL-1842-1850", "NRDL-BAUT-05", "NRDL-BAUT-06"],
        "candidatos_preferidos": [
            "004298570_02637.jpg",
            "004298570_02638.jpg",
            "004298570_02639.jpg",
            "004298570_02460.jpg",
            "004306113_00100.jpg",
        ],
    },
    {
        "id": "C10",
        "motor": "Motor 3: Decimonónico e Inglesa (1790–1902)",
        "nombre": "Cursiva Rápida / Filiforme o de Mano Anciana (s. XIX)",
        "periodo": "1840–1895",
        "rasgos": "Trazo filiforme muy rápido o tembloroso, vocales aplastadas (m/n/u/i indistinguibles sin contexto léxico), abreviaturas decimonónicas.",
        "escribanos_clave": [
            "Manos rápidas de JMOL-DIFU-03 (1849–1851), JMOL-DIFU-04 (1851–1883) y NRDL-DIFU-03 / 04",
        ],
        "cuadernos": ["JMOL-DIFU-03", "JMOL-DIFU-04", "NRDL-DIFU-03", "NRDL-DIFU-04"],
        "candidatos_preferidos": [
            "004298571_00945.jpg",
            "004298571_01050.jpg",
            "004306113_01020.jpg",
            "004306113_01200.jpg",
        ],
    },
    {
        "id": "C11",
        "motor": "Motor 3: Decimonónico e Inglesa (1790–1902)",
        "nombre": "Redondilla Escolar / Administrativa de Restauración (Fines s. XIX – 1902)",
        "periodo": "1870–1902",
        "rasgos": "Letra muy clara y reglada, numeración de partidas, mención a juzgados municipales y Registro Civil, páginas pautadas.",
        "escribanos_clave": [
            "Párrocos de NRDL-BAUT-07 (1865–1889), NRDL-DIFU-05 (1880–1902)",
            "Párrocos de JMOL-MATR-03 (1851–1899), JMOL-DIFU-05 (1872–1881) y JMOL-DIFU-06 (1881–1892)",
        ],
        "cuadernos": ["NRDL-BAUT-07", "NRDL-DIFU-05", "JMOL-MATR-03", "JMOL-DIFU-05", "JMOL-DIFU-06"],
        "candidatos_preferidos": [
            "004306113_00360.jpg",
            "004306113_01420.jpg",
            "004298571_00450.jpg",
            "004298571_01300.jpg",
            "004298571_01450.jpg",
        ],
    },
    {
        "id": "C12",
        "motor": "Motor 4: Aparato Auxiliar, Índices y Tablas (1594–1914)",
        "nombre": "Abecedarios, Índices Tabulares, Listas de Confirmación y Guarismos",
        "periodo": "1649–1914",
        "rasgos": "Disposición en columnas (Nombre, Padres, Folio, Año), líneas cortas con puntos guía '......', guarismos arábigos de folios y años.",
        "escribanos_clave": [
            "Compiladores de JMOL-INDICE-BAUT (Bautismos 1750–1914 + Casados 1716–1920)",
            "Compiladores de JMOL-INDICE-DIFU (1893–1907)",
            "Notarios de Padrones de Confirmación (1649, 1681, 1759, 1776, 1786, 1827, 1850)",
        ],
        "cuadernos": ["JMOL-INDICE-BAUT", "JMOL-INDICE-DIFU", "NRDL-BAUT-01", "NRDL-BAUT-03", "JMOL-BAUT-03"],
        "candidatos_preferidos": [
            "004298570_02665.jpg",
            "004298570_02750.jpg",
            "004298571_01545.jpg",
            "004306112_02068.jpg",
            "004306112_02114.jpg",
        ],
    },
]


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
    """Devuelve la lista de IDs de cluster asociados a un cuaderno."""
    res = []
    for c in CLUSTERS_SPEC:
        if nb_id in c["cuadernos"]:
            res.append(c["id"])
    if not res:
        if "ENSENADA" in nb_id:
            res.append("C06")
        elif "INDICE" in nb_id:
            res.append("C12")
    return res or ["C04/C07"]


def parse_audits() -> list[dict[str, str]]:
    """Lee los 33 archivos de transcripciones/auditoria_codicologica/."""
    audits = []
    for p in sorted(AUDITS_DIR.glob("AUDITORIA_*.md")):
        nb_name = p.stem.replace("AUDITORIA_", "")
        txt = p.read_text(encoding="utf-8", errors="replace")
        # Extraer primera línea de resumen o rango de imágenes si aparece
        imgs_found = re.findall(r"\b004\d{6}_\d{4,5}\.jpg\b", txt)
        sample_imgs = []
        for im in imgs_found:
            if im not in sample_imgs:
                sample_imgs.append(im)
            if len(sample_imgs) >= 3:
                break
        audits.append(
            {
                "nb_id": nb_name,
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
    lines.append("# Mapa Operativo de Muestreo: Los 12 Clusters Paleográficos (`C01–C12`) y los 33 Cuadernos Auditados")
    lines.append("")
    lines.append("> **Propósito:** Este documento conecta directamente todo el trabajo previo de **NotebookLM Pro** (las 33 auditorías codicológicas en [`transcripciones/auditoria_codicologica/`](file:///c:/TRABAJOS/personal/genealo/transcripciones/auditoria_codicologica/), [`03_AUTORIDADES_PALEOGRAFICAS_ALTO_ALBERCHE.md`](file:///c:/TRABAJOS/personal/genealo/03_AUTORIDADES_PALEOGRAFICAS_ALTO_ALBERCHE.md) y [`catalogo_corpus.json`](file:///c:/TRABAJOS/personal/genealo/catalogo_corpus.json)) con archivos `.jpg` reales verificados en disco para entrenar los **4 Motores Kraken**.")
    lines.append(">")
    lines.append(f"> **Imágenes físicas indexadas en `imagenes/`:** `{len(local_imgs):,}` archivos `.jpg` verificados en disco local.")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 1. Resumen Ejecutivo: Los 4 Motores Kraken y sus 12 Clusters (`C01–C12`)")
    lines.append("")
    lines.append("| Motor Kraken Consolidado | Clusters Incluidos | Arco Temporal | Estado Actual de Muestras en Local |")
    lines.append("| :--- | :--- | :--- | :--- |")
    lines.append("| **`Motor 1`: `alto_alberche_procesal_1590_1660.mlmodel`** | `C01`, `C02`, `C03` | `1594–1660` | Candidatos localizados en disco (`DGS 004306112` y `004298571_00532`). |")
    lines.append("| **`Motor 2`: `alto_alberche_bastarda_1660_1790.mlmodel`** | `C04`, `C05`, `C06`, `C07` | `1660–1790` | **En marcha:** Folio `004298570_01608` (69 líneas transcritas con 0 errores Unicode, `C04`/`C05`). |")
    lines.append("| **`Motor 3`: `alto_alberche_decimononico_1790_1902.mlmodel`** | `C08`, `C09`, `C10`, `C11` | `1790–1902` | **En marcha:** `lote_prueba_5` (`004298570_02637` a `02641`, 5 folios ya segmentados en local, `C09`). |")
    lines.append("| **`Motor 4`: `alto_alberche_aparato_auxiliar.mlmodel`** | `C12` | `1649–1914` | Candidatos localizados (`JMOL-INDICE-BAUT`, `JMOL-INDICE-DIFU` y Padrones de Confirmación). |")
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
        # Si faltara alguno o para completar hasta 5, tomar del catálogo de sus cuadernos
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
        nb_id = aud["nb_id"]
        info = cat_by_nb.get(nb_id, {})
        count = info.get("count", 0)
        parroquias = ", ".join(sorted(info.get("parroquias", []))) or "NRDL/JMOL"
        anios = ", ".join(sorted(info.get("anios", []))) or "Ver auditoría"
        clusters = ", ".join(f"`{cl}`" for cl in map_notebook_to_clusters(nb_id))
        audit_link = f"[`AUDITORIA_{nb_id}.md`](file:///c:/TRABAJOS/personal/genealo/{aud['audit_path']})"

        # Determinar 2 imágenes verificadas en disco para esa fila
        row_imgs = []
        for im in aud["sample_imgs"] + info.get("images", [])[:10]:
            if im in local_imgs and im not in row_imgs:
                row_imgs.append(im)
            if len(row_imgs) >= 2:
                break
        imgs_str = ", ".join(f"`{im}`" for im in row_imgs) if row_imgs else "—"
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
    lines.append("3. **Pre-transcribir con Gemini Pro (`transcribir_pagexml.py`) y dar el visto bueno final en Aletheia 4.1** para incorporarlo al conjunto de entrenamiento `ketos train`.")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    md_content = build_markdown()
    OUTPUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_MD.write_text(md_content, encoding="utf-8")
    print(f"Mapa de clusters generado con exito en: {OUTPUT_MD}")


if __name__ == "__main__":
    main()
