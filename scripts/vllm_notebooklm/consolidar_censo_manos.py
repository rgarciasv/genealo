"""
Consolida los censos paleográficos individuales de transcripciones/censo_manos/*.md
en un Censo Global de Manos del Alto Alberche (docs/CENSO_GLOBAL_MANOS_ALTO_ALBERCHE.md y .csv).

Características:
- Separa limpiamente el bloque de PARTIDAS (libros sacramentales) del bloque auxiliar LISTAS
  (JMOL-INDICE-BAUT-MAT, JMOL-INDICE-DIFU, JMOL-DIFU-PARVULOS) para no distorsionar el Pareto.
- Unifica variantes ortográficas y tratamientos (Don/D./Lic./Br./Bachiller/Fray) de un mismo
  párroco/escribano a través de múltiples libros y entre ambas parroquias (JMOL + NRDL).
- Calcula curva de Pareto (cobertura acumulada 50%/70%/80%/90%), distribución por clúster C01-C12
  y por los 3 motores Kraken (M1: C01-C05, M2: C06-C10, M3: C11+C12).
- Propone un muestreo estratificado (~72 folios, 50% limpios / 50% degradados) para entrenamiento Kraken.
"""

import csv
import re
import unicodedata
from collections import defaultdict
from datetime import datetime
from pathlib import Path

CENSO_DIR = Path("transcripciones/censo_manos")
OUT_MD = Path("docs/CENSO_GLOBAL_MANOS_ALTO_ALBERCHE.md")
OUT_CSV = Path("docs/CENSO_GLOBAL_MANOS_ALTO_ALBERCHE.csv")

AUX_NOTEBOOKS = {"JMOL-INDICE-BAUT-MAT", "JMOL-INDICE-DIFU", "JMOL-DIFU-PARVULOS"}

CLUSTER_TO_ENGINE = {
    "C01": "M1_RENACENTISTA_PROCESAL (C01-C05)",
    "C02": "M1_RENACENTISTA_PROCESAL (C01-C05)",
    "C03": "M1_RENACENTISTA_PROCESAL (C01-C05)",
    "C04": "M1_RENACENTISTA_PROCESAL (C01-C05)",
    "C05": "M1_RENACENTISTA_PROCESAL (C01-C05)",
    "C06": "M2_BASTARDA_BARROCA_ILUSTRADA (C06-C10)",
    "C07": "M2_BASTARDA_BARROCA_ILUSTRADA (C06-C10)",
    "C08": "M2_BASTARDA_BARROCA_ILUSTRADA (C06-C10)",
    "C09": "M2_BASTARDA_BARROCA_ILUSTRADA (C06-C10)",
    "C10": "M2_BASTARDA_BARROCA_ILUSTRADA (C06-C10)",
    "C11": "M3_INGLESA_Y_SENIL (C11+C12)",
    "C12": "M3_INGLESA_Y_SENIL (C11+C12)",
}


def strip_accents(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def clean_md_cell(s: str) -> str:
    s = re.sub(r"\*\*|\*|`|\\", "", s or "")
    return re.sub(r"\s+", " ", s).strip()


def canonical_scribe_key(raw_name: str) -> tuple[str, str]:
    """Return (canonical_key, clean_display_name) unifying titles, tramo suffixes, and spelling."""
    disp = clean_md_cell(raw_name)
    # Remove parenthetical tramo/clarification notes
    base = re.sub(r"\([^)]*\)", " ", disp)
    base = re.sub(r"\[[^\]]*\]", " ", base)
    base = re.sub(r"\b(tramo\s*[ivx\d]+|parte\s*\d+|dislocaci[oó]n)\b.*", "", base, flags=re.I)
    base = strip_accents(base).lower()
    # Normalize common honorifics / titles
    base = re.sub(
        r"\b(don|d\.|doña|licenciado|lic\.do|lic\.|lcdo\.?|bachiller|b\.er|br\.|doctor|dr\.|"
        r"fray|fr\.|padre|p\.|presbitero|pbro\.?|cura|teniente|economo|vicario|notario\s+de\s+visita|"
        r"visitador|obispo|ilmo\.?|sr\.?|el|la|de\s+la|del|de|y)\b",
        " ",
        base,
    )
    # Historical spelling normalization (x->j, b/v, z/s, ph->f, th->t, y->i)
    base = base.replace("ximenez", "jimenez").replace("xymenez", "jimenez").replace("gimenez", "jimenez")
    base = base.replace("joseph", "jose").replace("josef", "jose")
    base = base.replace("joan", "juan").replace("phelipe", "felipe").replace("philipe", "felipe")
    base = base.replace("mathias", "matias").replace("matheo", "mateo").replace("thomas", "tomas")
    base = base.replace("blazquez", "blasquez").replace("velazquez", "velasquez")
    base = base.replace("hernandez", "fernandez") if "hernandez" not in base else base  # keep Hernandez distinct
    base = re.sub(r"[^a-z0-9\s]", " ", base)
    tokens = [t for t in base.split() if len(t) > 1]
    if not tokens or any(w in base for w in ("anonim", "sin firma", "ilegible", "desconocid", "mano ")):
        return f"anon_{'_'.join(tokens[:3]) or 'sin_identificar'}", disp
    key = " ".join(tokens[:4])
    return key, disp


def parse_folios(val: str) -> float:
    s = clean_md_cell(val).lower().replace(",", ".")
    if not s:
        return 0.0
    if "<1" in s or "1 partida" in s or "puntual" in s:
        return 0.5
    nums = [float(x) for x in re.findall(r"\d+(?:\.\d+)?", s)]
    if not nums:
        return 1.0
    if len(nums) >= 2 and ("-" in s or "–" in s or " a " in s):
        return (nums[0] + nums[1]) / 2.0
    return nums[0]


def parse_primary_cluster(val: str) -> str:
    m = re.findall(r"C(?:0[1-9]|1[0-2])", (val or "").upper())
    return m[0] if m else "SIN_CLUSTER"


def parse_years(val: str) -> tuple[int | None, int | None]:
    yrs = [int(y) for y in re.findall(r"\b(1[5-9]\d{2})\b", val or "")]
    if not yrs:
        return None, None
    return min(yrs), max(yrs)


def parse_censo_file(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8", errors="replace")
    nb_name = path.stem
    parish = "JMOL" if nb_name.startswith("JMOL") else ("NRDL" if nb_name.startswith("NRDL") else "OTRO")
    block_type = "LISTAS_AUXILIAR" if nb_name in AUX_NOTEBOOKS else "PARTIDAS"

    rows = []
    header_seen = False
    sep_seen = False
    for line in text.splitlines():
        s = line.strip()
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if not header_seen:
            if any("orden" in c.lower() for c in cells) and any("cura" in c.lower() or "redactor" in c.lower() for c in cells):
                header_seen = True
                sep_seen = False
            continue
        if not sep_seen:
            if all(set(c.replace(":", "").replace("-", "").replace(" ", "")) == set() for c in cells):
                sep_seen = True
                continue
        if header_seen and sep_seen and len(cells) >= 9:
            # Skip repeated headers if merged
            if "orden" in cells[0].lower() and "cura" in cells[1].lower():
                sep_seen = False
                continue
            if len(cells) < 10:
                cells.extend([""] * (10 - len(cells)))
            key, disp = canonical_scribe_key(cells[1])
            folios = parse_folios(cells[7])
            cluster = parse_primary_cluster(cells[8])
            y_min, y_max = parse_years(cells[4])
            rows.append(
                {
                    "cuaderno": nb_name,
                    "parroquia": parish,
                    "bloque": block_type,
                    "orden": clean_md_cell(cells[0]),
                    "clave_canonica": key,
                    "redactor": disp,
                    "variantes_firma": clean_md_cell(cells[2]),
                    "rol": clean_md_cell(cells[3]),
                    "anios": clean_md_cell(cells[4]),
                    "anio_min": y_min or "",
                    "anio_max": y_max or "",
                    "primera_img": clean_md_cell(cells[5]),
                    "ultima_img": clean_md_cell(cells[6]),
                    "n_folios": round(folios, 1),
                    "cluster_raw": clean_md_cell(cells[8]),
                    "cluster_principal": cluster,
                    "motor_kraken": CLUSTER_TO_ENGINE.get(cluster, "SIN_ASIGNAR"),
                    "observaciones": clean_md_cell(cells[9]),
                }
            )
    return rows


def main():
    md_files = sorted(CENSO_DIR.glob("*.md"))
    all_rows = []
    per_nb_counts = {}
    for p in md_files:
        r = parse_censo_file(p)
        per_nb_counts[p.stem] = len(r)
        all_rows.extend(r)

    # Save master CSV
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "cuaderno",
        "parroquia",
        "bloque",
        "orden",
        "clave_canonica",
        "redactor",
        "variantes_firma",
        "rol",
        "anios",
        "anio_min",
        "anio_max",
        "primera_img",
        "ultima_img",
        "n_folios",
        "cluster_raw",
        "cluster_principal",
        "motor_kraken",
        "observaciones",
    ]
    with open(OUT_CSV, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, delimiter=";")
        w.writeheader()
        w.writerows(all_rows)

    partidas = [r for r in all_rows if r["bloque"] == "PARTIDAS"]
    listas = [r for r in all_rows if r["bloque"] == "LISTAS_AUXILIAR"]

    # Aggregate canonical hands for PARTIDAS
    hands = defaultdict(
        lambda: {
            "folios": 0.0,
            "tramos": 0,
            "cuadernos": set(),
            "parroquias": set(),
            "clusters": defaultdict(float),
            "names": defaultdict(float),
            "years": [],
            "sample_imgs": [],
            "obs": [],
        }
    )
    for r in partidas:
        h = hands[r["clave_canonica"]]
        h["folios"] += r["n_folios"]
        h["tramos"] += 1
        h["cuadernos"].add(r["cuaderno"])
        h["parroquias"].add(r["parroquia"])
        h["clusters"][r["cluster_principal"]] += r["n_folios"]
        h["names"][r["redactor"]] += r["n_folios"]
        if r["anio_min"]:
            h["years"].append(int(r["anio_min"]))
        if r["anio_max"]:
            h["years"].append(int(r["anio_max"]))
        if r["primera_img"] and ".jpg" in r["primera_img"]:
            h["sample_imgs"].append((r["cuaderno"], r["primera_img"], r["ultima_img"], r["n_folios"]))
        if r["observaciones"]:
            h["obs"].append(r["observaciones"])

    ranked = sorted(hands.items(), key=lambda kv: kv[1]["folios"], reverse=True)
    total_folios_partidas = sum(h["folios"] for _, h in ranked)

    # Pareto thresholds
    thresholds = {}
    cum = 0.0
    for idx, (_, h) in enumerate(ranked, start=1):
        cum += h["folios"]
        pct = (cum / total_folios_partidas * 100.0) if total_folios_partidas else 0.0
        for t in (50, 70, 80, 90):
            if t not in thresholds and pct >= t:
                thresholds[t] = (idx, pct)

    # Cluster & Engine stats (PARTIDAS)
    cluster_stats = defaultdict(lambda: {"folios": 0.0, "tramos": 0, "manos": set()})
    engine_stats = defaultdict(lambda: {"folios": 0.0, "tramos": 0, "manos": set()})
    for r in partidas:
        c = r["cluster_principal"]
        e = r["motor_kraken"]
        cluster_stats[c]["folios"] += r["n_folios"]
        cluster_stats[c]["tramos"] += 1
        cluster_stats[c]["manos"].add(r["clave_canonica"])
        engine_stats[e]["folios"] += r["n_folios"]
        engine_stats[e]["tramos"] += 1
        engine_stats[e]["manos"].add(r["clave_canonica"])

    # Cross-parish hands
    cross_parish = [(k, h) for k, h in ranked if len(h["parroquias"]) >= 2]
    cross_book = [(k, h) for k, h in ranked if len(h["cuadernos"]) >= 2]

    # Build Markdown report
    lines = [
        "# Censo Global de Manos y Curva de Pareto — Corpus Parroquial Alto Alberche",
        "",
        f"- **Fecha de consolidación:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"- **Cuadernos censados:** `{len(md_files)} / 33` *(Catastro de Ensenada excluido en track independiente)*",
        f"- **Tramos redaccionales totales:** `{len(all_rows)}` (`{len(partidas)}` en `PARTIDAS` + `{len(listas)}` en `LISTAS/Auxiliar`)",
        f"- **Manos canónicas únicas en `PARTIDAS`:** **`{len(ranked)}`** (estimación total: `{total_folios_partidas:,.1f}` folios-tramo)",
        f"- **Manos presentes en 2+ libros:** `{len(cross_book)}` | **Manos compartidas entre `JMOL` y `NRDL`:** `{len(cross_parish)}`",
        f"- **Datos tabulares completos:** `docs/CENSO_GLOBAL_MANOS_ALTO_ALBERCHE.csv`",
        "",
        "---",
        "",
        "## 1. Curva de Pareto (Concentración de Folios por Mano en `PARTIDAS`)",
        "",
        "| Cobertura del Corpus (`PARTIDAS`) | N.º de Manos Necesarias | % de las Manos Totales | % Real Alcanzado |",
        "| :---: | :---: | :---: | :---: |",
    ]
    for t in (50, 70, 80, 90):
        if t in thresholds:
            n_m, p_real = thresholds[t]
            pct_m = n_m / len(ranked) * 100.0 if ranked else 0.0
            lines.append(f"| **{t}% de los folios** | **{n_m} manos** | {pct_m:.1f}% | {p_real:.1f}% |")

    lines.extend([
        "",
        "## 2. Distribución por Motor Kraken y Clúster Morfográfico (`C01–C12`, solo `PARTIDAS`)",
        "",
        "### Por Motor Kraken (3 Motores Parroquiales)",
        "| Motor Kraken | Folios Aprox. | % Corpus | Tramos | Manos Únicas |",
        "| :--- | :---: | :---: | :---: | :---: |",
    ])
    for eng in sorted(engine_stats):
        st = engine_stats[eng]
        pct = st["folios"] / total_folios_partidas * 100.0 if total_folios_partidas else 0.0
        lines.append(f"| **{eng}** | {st['folios']:.1f} | **{pct:.1f}%** | {st['tramos']} | {len(st['manos'])} |")

    lines.extend([
        "",
        "### Por Clúster Morfográfico (`C01–C12`)",
        "| Clúster | Motor | Folios Aprox. | % Corpus | Tramos | Manos Únicas |",
        "| :---: | :--- | :---: | :---: | :---: | :---: |",
    ])
    for cl in sorted(cluster_stats):
        st = cluster_stats[cl]
        pct = st["folios"] / total_folios_partidas * 100.0 if total_folios_partidas else 0.0
        lines.append(f"| `{cl}` | {CLUSTER_TO_ENGINE.get(cl, '-')} | {st['folios']:.1f} | {pct:.1f}% | {st['tramos']} | {len(st['manos'])} |")

    lines.extend([
        "",
        "---",
        "",
        "## 3. Ranking Pareto — Top 45 Manos del Alto Alberche (`PARTIDAS`)",
        "",
        "| # | Mano / Escribano Canónico | Parroquias | Libros | Años | Clúster Dominante | Folios Aprox. | % Acum. |",
        "| :-: | :--- | :---: | :---: | :---: | :---: | :---: | :---: |",
    ])
    cum = 0.0
    for idx, (k, h) in enumerate(ranked[:45], start=1):
        cum += h["folios"]
        pct_c = cum / total_folios_partidas * 100.0 if total_folios_partidas else 0.0
        best_name = max(h["names"].items(), key=lambda x: x[1])[0]
        dom_cl = max(h["clusters"].items(), key=lambda x: x[1])[0]
        yr_str = f"{min(h['years'])}–{max(h['years'])}" if h["years"] else "-"
        par_str = "+".join(sorted(h["parroquias"]))
        lines.append(
            f"| {idx} | **{best_name}** | `{par_str}` | {len(h['cuadernos'])} | {yr_str} | `{dom_cl}` | **{h['folios']:.1f}** | {pct_c:.1f}% |"
        )

    lines.extend([
        "",
        "## 4. Clero Compartido entre San Juan del Molinillo (`JMOL`) y Navarredondilla (`NRDL`)",
        "",
        "| Mano / Escribano | Libros (`JMOL` + `NRDL`) | Años | Clúster | Folios Totales |",
        "| :--- | :--- | :---: | :---: | :---: |",
    ])
    for k, h in cross_parish[:30]:
        best_name = max(h["names"].items(), key=lambda x: x[1])[0]
        dom_cl = max(h["clusters"].items(), key=lambda x: x[1])[0]
        yr_str = f"{min(h['years'])}–{max(h['years'])}" if h["years"] else "-"
        books_str = ", ".join(sorted(h["cuadernos"]))
        lines.append(f"| **{best_name}** | {books_str} | {yr_str} | `{dom_cl}` | {h['folios']:.1f} |")

    lines.extend([
        "",
        "## 5. Propuesta de Muestreo Estratificado para Entrenamiento Kraken (~72 Folios, 50% Limpios / 50% Degradados)",
        "",
        "Selección directa de las **top manos por motor** (2 folios por mano: 1 limpio + 1 degradado/tinta corrida/encadenada) cubriendo el núcleo del Pareto:",
        "",
        "| Motor Kraken | Mano Seleccionada | Cuaderno Principal | Clúster | Folios en Corpus | Muestra Propuesta | Rango `.jpg` de Referencia |",
        "| :--- | :--- | :--- | :---: | :---: | :---: | :--- |",
    ])
    selected_per_engine = defaultdict(int)
    limits = {
        "M1_RENACENTISTA_PROCESAL (C01-C05)": 10,
        "M2_BASTARDA_BARROCA_ILUSTRADA (C06-C10)": 16,
        "M3_INGLESA_Y_SENIL (C11+C12)": 10,
    }
    for k, h in ranked:
        dom_cl = max(h["clusters"].items(), key=lambda x: x[1])[0]
        eng = CLUSTER_TO_ENGINE.get(dom_cl, "")
        if eng not in limits or selected_per_engine[eng] >= limits[eng]:
            continue
        best_name = max(h["names"].items(), key=lambda x: x[1])[0]
        if h["sample_imgs"]:
            top_sample = max(h["sample_imgs"], key=lambda x: x[3])
            nb_s, img1, img2, _ = top_sample
            ref = f"`{img1}` .. `{img2}`"
        else:
            nb_s, ref = sorted(h["cuadernos"])[0], "-"
        selected_per_engine[eng] += 1
        lines.append(f"| {eng.split(' ')[0]} | **{best_name}** | `{nb_s}` | `{dom_cl}` | {h['folios']:.1f} | 2 (1L+1D) | {ref} |")

    lines.extend([
        "",
        "## 6. Bloque Auxiliar (`LISTAS`: Índices y Párvulos — Separado del Pareto)",
        "",
        "| Cuaderno | Tramos Censados | Folios Aprox. | Clústeres Detectados |",
        "| :--- | :---: | :---: | :--- |",
    ])
    for nb in sorted(AUX_NOTEBOOKS):
        sub = [r for r in listas if r["cuaderno"] == nb]
        fols = sum(r["n_folios"] for r in sub)
        cls = ", ".join(sorted({r["cluster_principal"] for r in sub})) or "-"
        lines.append(f"| `{nb}` | {len(sub)} | {fols:.1f} | {cls} |")

    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"CONSOLIDADO OK: {len(md_files)}/33 cuadernos | {len(all_rows)} tramos | {len(ranked)} manos unicas (PARTIDAS) | {total_folios_partidas:.1f} folios")
    for t in (50, 70, 80, 90):
        if t in thresholds:
            print(f"  Pareto {t}% -> {thresholds[t][0]} manos ({thresholds[t][1]:.1f}%)")
    print(f"  Salidas: {OUT_MD} y {OUT_CSV}")


if __name__ == "__main__":
    main()
