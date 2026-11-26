"""Configuración ecdótica, inventario Unicode cerrado, glosario y prompts paleográficos."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_INPUT_DIR = PROJECT_ROOT / "htr_pipeline" / "inputs" / "01608"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "htr_pipeline" / "outputs" / "01608"

# Modelo por defecto especificado para transcripción de líneas.
# Gemini 4 Hydrogen (gemini-4-hydrogen) está disponible en Free Tier y reduce >5x las alucinaciones.
# Para manuscritos extremos (procesal s. XVI-XVII) se puede pasar --model gemini-4-neon (Paid Tier).
DEFAULT_MODEL = "gemini-4-hydrogen"
DEFAULT_TEMPERATURE = 0.1
DEFAULT_RESOLUTION = "high"  # "low" | "medium" | "high" (1120 tok) | "ultra_high" (2240 tok)
DEFAULT_THINKING_LEVEL = "medium"  # "low" | "medium" | "high" | "xhigh" | ""

# Parámetros de recorte poligonal
DEFAULT_MIN_LINE_WIDTH_PX = 45
DEFAULT_DILATION_PX = 4
DEFAULT_ROI_MARGIN_PX = 6

# Espacio de nombres oficial de PAGE-XML (eScriptorium)
PAGE_NS = "http://schema.primaresearch.org/PAGE/gts/pagecontent/2019-07-15"
PAGE_NSMAP = {None: PAGE_NS}

# Inventario Unicode cerrado permitido fuera de ASCII básico [0x20-0x7E]
ALLOWED_SPECIAL_UNICODE: dict[str, str] = {
    "\u00aa": "ª (ordinal femenino)",
    "\u00ba": "º (ordinal masculino)",
    "\u1d9c": "ᶜ (c volada)",
    "\u1d48": "ᵈ (d volada)",
    "\u1d49": "ᵉ (e volada)",
    "\u1d50": "ᵐ (m volada)",
    "\u207f": "ⁿ (n volada)",
    "\u02b3": "ʳ (r volada)",
    "\u02e2": "ˢ (s volada)",
    "\u1d57": "ᵗ (t volada)",
    "\u02e1": "ˡ (l volada)",
    "\u0304": "̄ (macrón combinante NFD)",
    "\u00e7": "ç",
    "\u00c7": "Ç",
    "\u00f1": "ñ",
    "\u00d1": "Ñ",
    "\u0026": "&",
    # Vocales acentuadas solo si el trazo histórico las presenta de forma inequívoca
    "\u00e1": "á",
    "\u00e9": "é",
    "\u00ed": "í",
    "\u00f3": "ó",
    "\u00fa": "ú",
    "\u00c1": "Á",
    "\u00c9": "É",
    "\u00cd": "Í",
    "\u00d3": "Ó",
    "\u00da": "Ú",
}

# Caracteres prohibidos o confusiones frecuentes detectadas en auditorías previas
FORBIDDEN_OR_CONFUSED_CHARS: dict[str, str] = {
    "\u00b0": "Símbolo de grado '°' (U+00B0); usar ordinal masculino 'º' (U+00BA).",
    "\u1d52": "Superíndice 'ᵒ' (U+1D52) fuera de inventario cerrado; usar ordinal masculino 'º' (U+00BA).",
    "\u1d43": "Superíndice 'ᵃ' (U+1D43) fuera de inventario cerrado; usar ordinal femenino 'ª' (U+00AA).",
    "\ufb01": "Ligadura tipográfica 'ﬁ'; descomponer en 'fi'.",
    "\ufb02": "Ligadura tipográfica 'ﬂ'; descomponer en 'fl'.",
    "\u017f": "s larga 'ſ' (U+017F); regularizar a 's' estándar según criterio TRIDIS.",
    "?": "Signo de interrogación '?'; prohibido para marcar duda (usar duda=true).",
}

LOCAL_GLOSSARY = """
GLOSARIO ONOMÁSTICO Y TOPONÍMICO COMARCAL (SOLO AYUDA VISUAL DE DESAMBIGUACIÓN; NUNCA FORZAR SOBRE EL TRAZO REAL):
- Localidades y jurisdicciones: San Juan del Molinillo, Molinillo, Navalmoral, San Pedro de Navalmoral, Navandrinal, Villarejo, Navalsauz, Las Berlanas, Peñalba, Serranillos, La Adrada, Piedralaves, Burgohondo.
- Párrocos y escribanos frecuentes: Fray Francisco Martínez (fray franᶜº Martinez), Domingo Galán, Pedro de la Rebilla.
- Nombres y apellidos locales: Andrino, Herranz, Toribio, Thomasa, Ximénez, Muñoz, Blázquez, Encabo, Sanz, López, Pérez, García, Martín, González.
""".strip()

SYSTEM_PROMPT = f"""Eres un paleógrafo experto en documentación eclesiástica hispánica (siglos XVI–XIX, Archivo Diocesano de Ávila).
Tu única tarea es transcribir de forma ESTRICTAMENTE PALEOGRÁFICA Y LITERAL la imagen recortada de una sola línea manuscrita.

REGLAS DE TRANSCRIPCIÓN (OBLIGATORIAS):
1. ANTI-NORMALIZACIÓN ESTRICTA:
   - Conserva la ortografía histórica exacta sin corregirla ni modernizarla (ej.: Bauptize, hixa, muger, yglesia, exorcize, chrisma, nuebe, lexitima, fee).
   - Conserva las elisiones, aglutinaciones y separaciones reales del trazo (ej.: alcaldy, destas, ypor, verdadlo, Sanjuan, delmismo).
   - Conserva el latín y los latinismos exactamente como aparecen (ej.: fecho ut supra, in solidum).
   - Usa mayúsculas SOLO cuando el trazo inicial sea inequívocamente capital.
   - Conserva la puntuación visible exacta: , ( ) = . -

2. REGULARIZACIÓN MÍNIMA (ÚNICAMENTE ESTOS 3 ALÓGRAFOS):
   - u / v según valor fonético (ej.: Navalmoral, aver, ut supra).
   - i / j según valor fonético (ej.: Juan, hija), EXCEPTO en numerales romanos finales donde se mantiene j (ej.: xvij).
   - ſ larga -> s estándar (nunca emitir 'ſ').

3. NEXOS Y ABREVIATURAS:
   - Descompón siempre los nexos cursivos (de, st, is, ct) en sus letras individuales; NUNCA uses ligaduras tipográficas como ﬁ o ﬂ.
   - NO desarrolles ni expandas ninguna abreviatura. Transcríbelas con los superíndices o macrones exactos.

4. INVENTARIO UNICODE CERRADO (NO USES OTROS SUPERÍNDICES NI SÍMBOLOS):
   - Ordinales y letras voladas permitidas:
     ª (U+00AA), º (U+00BA), ᶜ (U+1D9C), ᵈ (U+1D48), ᵉ (U+1D49), ᵐ (U+1D50), ⁿ (U+207F), ʳ (U+02B3), ˢ (U+02E2), ᵗ (U+1D57), ˡ (U+02E1)
   - Atención crítica: usa 'º' (U+00BA), JAMÁS el símbolo de grado '°' (U+00B0).
   - Macrón combinante sobre la letra abreviada: ̄ (U+0304), p. ej. q̄.
   - Otros admitidos: ç, ñ, &.
   - Pon tildes (á, é, í, ó, ú) ÚNICAMENTE si el rasgo del acento está físicamente trazado en la tinta; por defecto los manuscritos del s. XVIII casi no llevan tildes.

5. TACHADURAS E INCERTIDUMBRE:
   - Palabra tachada pero legible: enciérrala entre signos dólar, ej. $palabra$.
   - Tachadura totalmente ilegible: omítela.
   - PROHIBIDO escribir '[?]', '?' o '[ilegible]' en el campo "texto".
   - Si algún trazo está borroso, manchado o pálido y no es 100% seguro, pon la mejor lectura literal (o "" si es totalmente ilegible) y marca obligatoriamente "duda": true explicando el tramo en "motivo".

EJEMPLOS FEW-SHOT VERIFICADOS:
- Ejemplo 1 (ortografía histórica sin modernizar ni abreviar lo que está completo):
  "En la yglesia del señor San Juan del Molinillo en quinçe" -> texto: "En la yglesia del señor San Juan del Molinillo en quinçe", duda: false, motivo: ""
- Ejemplo 2 (abreviaturas con letras voladas reales del inventario cerrado):
  "hixa lexᵐª de franᶜº Perez y Mª Muños vºˢ de Navandrinal" -> texto: "hixa lexᵐª de franᶜº Perez y Mª Muños vºˢ de Navandrinal", duda: false, motivo: ""
- Ejemplo 3 (elisión y firma literal):
  "fecho ut supra= fray franᶜº Martinez" -> texto: "fecho ut supra= fray franᶜº Martinez", duda: false, motivo: ""

{LOCAL_GLOSSARY}

Devuelve exclusivamente un JSON válido conforme al esquema solicitado."""
