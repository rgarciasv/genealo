"""
Genera 01_DICCIONARIO_ANCLAJE_JMOL.md a partir de los 7.437 registros extraídos de los
3 índices maestros de San Juan del Molinillo (Bautismos, Casados y Defunciones) y del
Censo Global de Manos (docs/CENSO_GLOBAL_MANOS_ALTO_ALBERCHE.csv).

El resultado sirve como Fuente 01 oficial de grounding en NotebookLM y para los
diccionarios NER locales de San Juan del Molinillo y sus anejos (Navandrinal y El Villarejo).
"""

import csv
import re
import unicodedata
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

BAUT_CSV = Path("htr_pipeline/outputs/indice_jmol_bautismos/JMOL_INDICE_BAUTISMOS_1750_1921_bautismos.csv")
CAS_CSV = Path("htr_pipeline/outputs/indice_jmol_casados/JMOL_INDICE_CASADOS_1716_1920_casados.csv")
DIF_CSV = Path("htr_pipeline/outputs/indice_jmol_difuntos/JMOL_INDICE_DIFUNTOS_1893_1907_difuntos.csv")
CENSO_CSV = Path("docs/CENSO_GLOBAL_MANOS_ALTO_ALBERCHE.csv")
OUT_MD = Path("01_DICCIONARIO_ANCLAJE_JMOL.md")

STOPWORDS = {
    "de", "del", "la", "las", "el", "los", "y", "e", "en", "con", "su", "al", "a",
    "s", "sn", "san", "sta", "sto", "v", "vdo", "vda", "viudo", "viuda", "soltero",
    "soltera", "exposita", "exposito", "esposita", "esposito", "expos", "exp", "madrid", "avila",
    "parvulo", "parvula", "innominado", "innominada", "hijo", "hija", "natural",
    "legitimo", "legitima", "entre", "lineas", "nota", "otro", "otra", "desconocido",
    "idem", "id", "par", "manos", "duda", "ilegible", "roto",
}


def norm_token(t: str) -> str:
    t = re.sub(r"[^A-Za-zÁÉÍÓÚÜÑáéíóúüñ]", "", t or "")
    return t.strip()


def strip_accents(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


SURNAME_OCR_NORMALIZE = {
    "lucabo": "Encabo",
    "eucabo": "Encabo",
    "audrino": "Andrino",
    "nodea": "Rodea",
}


def canon_display(t: str) -> str:
    """Normaliza tildes solo para agrupar variantes (García/Garcia) manteniendo la forma más común."""
    return strip_accents(t).capitalize()


def is_valid_name_token(t: str) -> bool:
    if len(t) < 3:
        return False
    low = strip_accents(t).lower()
    if low in STOPWORDS:
        return False
    return True


def main():
    first_names = Counter()
    surnames = Counter()
    name_forms = defaultdict(Counter)
    surname_forms = defaultdict(Counter)
    total_rows = 0

    def add_name(tok: str, w: int = 1):
        k = canon_display(tok)
        first_names[k] += w
        name_forms[k][tok.capitalize()] += w

    def add_surname(tok: str, w: int = 1):
        low = strip_accents(tok).lower()
        if low in SURNAME_OCR_NORMALIZE:
            tok = SURNAME_OCR_NORMALIZE[low]
        k = canon_display(tok)
        surnames[k] += w
        surname_forms[k][tok.capitalize()] += w

    def process_person(full_name: str, weight: int = 1):
        # Clean bracketed/doubt annotations
        clean = re.sub(r"\[[^\]]*\]|\([^)]*\)", " ", full_name or "")
        clean = clean.replace(",", " ").replace(".", " ")
        tokens = [norm_token(x) for x in clean.split()]
        tokens = [t for t in tokens if is_valid_name_token(t)]
        if not tokens:
            return
        add_name(tokens[0], weight)
        for tok in tokens[1:]:
            add_surname(tok, weight)

    if BAUT_CSV.exists():
        with open(BAUT_CSV, encoding="utf-8-sig") as f:
            for r in csv.DictReader(f, delimiter=";"):
                total_rows += 1
                process_person(r.get("nombre_bautizado", ""))
                padres = re.sub(r"\[[^\]]*\]|\([^)]*\)", " ", r.get("padres", ""))
                for part in re.split(r"\s+[ye]\s+", padres):
                    toks = [norm_token(x) for x in part.split()]
                    toks = [t for t in toks if is_valid_name_token(t)]
                    if toks:
                        add_name(toks[0], 1)

    if CAS_CSV.exists():
        with open(CAS_CSV, encoding="utf-8-sig") as f:
            for r in csv.DictReader(f, delimiter=";"):
                total_rows += 1
                process_person(r.get("novio", ""))
                process_person(r.get("novia", ""))

    if DIF_CSV.exists():
        with open(DIF_CSV, encoding="utf-8-sig") as f:
            for r in csv.DictReader(f, delimiter=";"):
                total_rows += 1
                process_person(r.get("nombre_difunto", ""))

    # Extract top JMOL scribes/clergy from Censo Global
    clergy_rows = []
    if CENSO_CSV.exists():
        by_key = defaultdict(lambda: {"name": "", "folios": 0.0, "years": [], "books": set(), "clusters": Counter()})
        with open(CENSO_CSV, encoding="utf-8-sig") as f:
            for r in csv.DictReader(f, delimiter=";"):
                if r.get("parroquia") != "JMOL" or r.get("bloque") != "PARTIDAS":
                    continue
                k = r.get("clave_canonica", "")
                if not k or k.startswith("anon_"):
                    continue
                d = by_key[k]
                d["name"] = d["name"] or r.get("redactor", "")
                try:
                    d["folios"] += float(r.get("n_folios") or 0)
                except ValueError:
                    pass
                for yc in ("anio_min", "anio_max"):
                    if (r.get(yc) or "").isdigit():
                        d["years"].append(int(r[yc]))
                d["books"].add(r.get("cuaderno", ""))
                d["clusters"][r.get("cluster_principal", "")] += 1
        clergy_rows = sorted(by_key.values(), key=lambda x: x["folios"], reverse=True)[:40]

    top_surnames = [f"{surname_forms[k].most_common(1)[0][0]} ({c})" for k, c in surnames.most_common(120)]
    top_names = [f"{name_forms[k].most_common(1)[0][0]} ({c})" for k, c in first_names.most_common(120)]

    lines = [
        "# 01_DICCIONARIO_ANCLAJE_JMOL (San Juan del Molinillo, Navandrinal y El Villarejo, 1715–1921)",
        "",
        "> **DIRECTIVA DE USO PARA NOTEBOOKLM Y PIPELINE NER (`[Reglas L-01, L-02, L-05, L-06, L-22]`):**",
        "> Este documento es un **Diccionario de Anclaje Léxico Pasivo** generado a partir de los **7.437 registros históricos** de los tres índices de San Juan del Molinillo y del Censo Global de Manos.",
        "> 1. **CUÁNDO USARLO:** Úsalo exclusivamente para **desambiguar trazos cursivos difusos** en apellidos, nombres de pila, topónimos comarcales y firmas clericales al inspeccionar visualmente una imagen.",
        "> 2. **PROHIBICIÓN ESTRICTA (`[L-01 / L-02]`):** **JAMÁS** sustituyas ni inventes un nombre, apellido o fecha ausente del trazo físico del manuscrito.",
        "",
        f"*Generado automáticamente el {datetime.now().strftime('%Y-%m-%d %H:%M')} sobre `{total_rows}` registros de índices locales.*",
        "",
        "---",
        "",
        "## 1. TOPONIMIA DE MUNDO CERRADO (`JMOL` Y ANEJOS)",
        "",
        "Parroquia matriz de **San Juan Bautista de San Juan del Molinillo** (segregada de Navalmoral de la Sierra en 1715; Diócesis de Ávila, Sit. Arch. `175/1`) y sus dos aldeas anejas:",
        "- **San Juan del Molinillo:** `san juan del molinillo`, `sn juan del molinillo`, `el molinillo`, `molinillo`, `esta villa`.",
        "- **Navandrinal:** `navandrinal`, `nabandrinal`, `navaendrinal`, `nava endrinal`.",
        "- **El Villarejo:** `el villarejo`, `villarejo`, `el billarejo`, `billarejo`.",
        "- **Comarca y referencias frecuentes:** `Navalmoral`, `Navarredondilla`, `Burgohondo`, `Navalacruz`, `Navalosa`, `Navaluenga`, `Serranillos`, `Hoyocasero`, `Cebreros`, `Ávila`, `Inclusa / Expósito de Madrid`, `Expósito de Ávila`.",
        "",
        "---",
        "",
        "## 2. TOP 120 APELLIDOS DOCUMENTADOS EN SAN JUAN DEL MOLINILLO (CON FRECUENCIA)",
        "",
        ", ".join(top_surnames) + ".",
        "",
        "> **Alertas paleográficas de apellidos locales:**",
        "> - `Encabo` ↔ a veces mal leído en cursiva como `Lucabo` o `Eucabo`.",
        "> - `Andrino` ↔ a veces mal leído (`u` por `n`) como `Audrino`.",
        "> - `Toribio` / `Torivio` ↔ en grafía antigua puede aparecer como `Foxivio` / `Fojivio`.",
        "> - `Hernández` ↔ `Fernández` (intercambio frecuente en s. XVIII–XIX).",
        "> - `Jiménez` ↔ `Ximénez` ↔ `Giménez`.",
        "> - `Blázquez` ↔ `Blásquez` ↔ `Velázquez`.",
        "> - `García de Juan` / `de la Fuente` / `del Peso` / `San Segundo` (`Sn Segundo`) / `de Juan`: apellidos compuestos habituales en la parroquia.",
        "",
        "---",
        "",
        "## 3. TOP 120 NOMBRES DE PILA DOCUMENTADOS (CON FRECUENCIA)",
        "",
        ", ".join(top_names) + ".",
        "",
        "---",
        "",
        "## 4. PRINCIPALES PÁRROCOS, TENIENTES Y ECÓNOMOS DE `JMOL` (POR VOLUMEN DE FOLIOS)",
        "",
        "| Párroco / Redactor | Años documentados | Clúster dominante | Libros | Folios aprox. |",
        "| :--- | :---: | :---: | :---: | :---: |",
    ]

    for c in clergy_rows:
        yr_str = f"{min(c['years'])}–{max(c['years'])}" if c["years"] else "-"
        cl_dom = c["clusters"].most_common(1)[0][0] if c["clusters"] else "-"
        lines.append(f"| **{c['name']}** | {yr_str} | `{cl_dom}` | {len(c['books'])} | {c['folios']:.1f} |")

    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Generado {OUT_MD} ({len(lines)} lineas | {len(surnames)} apellidos unicos | {len(first_names)} nombres unicos).")


if __name__ == "__main__":
    main()
