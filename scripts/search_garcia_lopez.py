import subprocess
import sys
import time
from pathlib import Path

cli_path = Path("venv/Scripts/notebooklm.exe").resolve()
temp_file = Path("scripts/temp_genealo_query.txt").resolve()

# ONLY NAVARREDONDILLA NOTEBOOKS
targets = [
    {
        "name": "NRDL-BAUT-07 (1876-1889)",
        "id": "0a31b8ce-184b-49af-ae17-0df8446ecc5f",
        "prompt": """Busca exhaustivamente en este libro de bautismos de Navarredondilla (1876-1889):
1) Si hay algún bautismo de un niño llamado Crisanto (o Crisanto García).
2) Si hay algún bautismo de una niña llamada Martina (o Martina López).
3) Si hay alguna nota marginal al lado de cualquier partida de bautismo que mencione un matrimonio posterior con "Crisanto García" o con "Martina López".
4) Si hay algún bautismo donde los padres sean Crisanto García y Martina López.

Si encuentras cualquier mención o coincidencia, transcribe todos los datos: fecha de nacimiento, fecha de bautismo, nombre del infante, padres, los 4 abuelos (con sus naturalezas) y el texto exacto de la nota marginal."""
    },
    {
        "name": "NRDL-BAUT-06 (1852-1876)",
        "id": "9cdd4e0c-a922-4edc-acfb-4a5dee7a896d",
        "prompt": """Busca exhaustivamente en este libro de bautismos de Navarredondilla (1852-1876):
1) Si hay algún bautismo de un niño llamado Crisanto (o Crisanto García).
2) Si hay algún bautismo de una niña llamada Martina (o Martina López).
3) Si hay alguna nota marginal o legitimación que mencione a "Crisanto García" o "Martina López".

Si encuentras cualquier mención o coincidencia, transcribe todos los datos: fecha de nacimiento, fecha de bautismo, nombre del infante, padres, los 4 abuelos (con sus naturalezas) y notas marginales."""
    },
    {
        "name": "NRDL-DIFU-05 (1872-1902)",
        "id": "d73e0a6c-7fa9-4c78-aec9-6c0bfcfd2ccf",
        "prompt": """Busca en este libro de difuntos de Navarredondilla (1872-1902) si aparece alguna partida de defunción o testamento que mencione como hijos vivos o herederos a "Crisanto García" o a "Martina López", o partidas de defunción de adultos con apellido García o López donde se citen a Crisanto o Martina."""
    }
]

for t in targets:
    print(f"\n==========================================")
    print(f"CONSULTANDO: {t['name']}")
    print(f"==========================================")
    
    with open(temp_file, "w", encoding="utf-8") as f:
        f.write(t["prompt"])
        
    cmd = [
        str(cli_path),
        "ask",
        "-n", t["id"],
        "--prompt-file", str(temp_file),
        "--timeout", "240"
    ]
    
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=270)
        if res.returncode == 0:
            output = res.stdout.strip()
            # Clean header
            lines = output.split("\n")
            clean_lines = []
            skip = True
            for line in lines:
                if skip:
                    if line.startswith("Answer:"):
                        skip = False
                        continue
                    elif "conversation" in line:
                        continue
                    elif line.strip() == "":
                        continue
                    else:
                        skip = False
                clean_lines.append(line)
            result_text = "\n".join(clean_lines).strip()
            print(result_text)
            
            # Save to scratch
            out_md = Path(f"scratch/busqueda_{t['name'][:12].replace(' ', '_')}.md")
            out_md.parent.mkdir(parents=True, exist_ok=True)
            with open(out_md, "w", encoding="utf-8") as out_f:
                out_f.write(f"# Búsqueda: Crisanto García y Martina López en {t['name']}\n\n{result_text}\n")
        else:
            print(f"ERROR: {res.stderr[:200]}")
    except Exception as e:
        print(f"EXCEPTION: {e}")
        
    time.sleep(5)

print("\nBúsqueda genealógica finalizada.")
