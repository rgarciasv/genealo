"""
Script de inspección de codecs y espacios de caracteres (Softmax/CTC) en modelos Kraken (.mlmodel).
Diseñado para auditar la presencia de variantes alfabéticas críticas como la s larga ('ſ' U+017F),
letras voladas ('º', 'ª'), diacríticos y contracciones paleográficas.
"""

import sys
import os

def inspect_model(model_path):
    if not os.path.exists(model_path):
        print(f"Error: El archivo {model_path} no existe.")
        return

    try:
        import torch
    except ImportError:
        print("Error: PyTorch no esta instalado en este entorno.")
        return

    print("=" * 70)
    print(f"INSPECCION FORENSE DEL CODEC: {os.path.basename(model_path)}")
    print("=" * 70)

    try:
        data = torch.load(model_path, map_location='cpu', weights_only=False)
    except Exception as e:
        print(f"Error al cargar el modelo con torch: {e}")
        return

    codec = data.get('codec', {})
    if hasattr(codec, 'c2l'):
        c2l = codec.c2l
    elif isinstance(codec, dict):
        c2l = codec
    else:
        print(f"Estructura de codec no reconocida: {type(codec)}")
        return

    chars = sorted(list(c2l.keys()), key=lambda c: (len(c), ord(c[0]) if c else 0))
    print(f"Total caracteres/etiquetas entrenadas: {len(chars)}")

    ascii_chars = [c for c in chars if len(c) == 1 and ord(c) < 128]
    non_ascii = [c for c in chars if not (len(c) == 1 and ord(c) < 128)]

    print(f"Caracteres ASCII estandar: {len(ascii_chars)}")
    print(f"Caracteres Especiales / No-ASCII: {len(non_ascii)}")

    # Comprobaciones criticas
    has_long_s = 'ſ' in chars or any('ſ' in c for c in chars)
    has_normal_s = 's' in chars
    has_masc_ordinal = 'º' in chars
    has_fem_ordinal = 'ª' in chars

    print("\n--- AUDITORIA DE GLIFOS CRITICOS ---")
    print(f"  * 's' estandar (U+0073):      {'PRESENTE' if has_normal_s else 'AUSENTE'}")
    print(f"  * 'ſ' larga (U+017F):         {'PRESENTE' if has_long_s else 'AUSENTE (Unificado a s)'}")
    print(f"  * 'º' ordinal masc (U+00BA):   {'PRESENTE' if has_masc_ordinal else 'AUSENTE'}")
    print(f"  * 'ª' ordinal fem (U+00AA):    {'PRESENTE' if has_fem_ordinal else 'AUSENTE'}")

    print("\n--- LISTA COMPLETA DE CARACTERES NO-ASCII ENTRENADOS ---")
    for i, c in enumerate(non_ascii):
        unicodes = " ".join([f"U+{ord(ch):04X}" for ch in c])
        print(f"  [{i+1:02d}] '{c}' -> {unicodes}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        target = sys.argv[1]
    else:
        default_model = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models", "Tridis_Medieval_EarlyModern.mlmodel")
        target = default_model

    inspect_model(target)
