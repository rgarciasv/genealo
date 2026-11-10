import urllib.request
import json
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'escriptorium.settings')
django.setup()

from django.core.files import File
from core.models import OcrModel
from users.models import User

admin_user = User.objects.filter(is_superuser=True).first()
if not admin_user:
    admin_user = User.objects.first()

RECORDS = [
    ("10788591", "TRIDIS (Documental y Notarial s.XII-XVI)"),
    ("10066219", "CATMuS Medieval (Castellano y Latin s.XIII-XVI)"),
    ("10609341", "McCATMuS (Espanol y Romance s.XVI-XIX)"),
]

os.makedirs('/tmp/mlmodels', exist_ok=True)

for record_id, display_name in RECORDS:
    print(f"\n=== Consultando Zenodo Record {record_id} ({display_name}) ===")
    api_url = f"https://zenodo.org/api/records/{record_id}"
    req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        
        files = data.get('files', [])
        ml_files = [f for f in files if f.get('key', '').endswith('.mlmodel')]
        if not ml_files:
            print(f"No se encontro archivo .mlmodel en record {record_id}")
            continue
        
        target_file = ml_files[0]
        fname = target_file['key']
        download_url = target_file['links']['self']
        local_path = f"/tmp/mlmodels/{fname}"
        
        print(f"Descargando {fname} desde {download_url}...")
        urllib.request.urlretrieve(download_url, local_path)
        print(f"Descargado con exito: {os.path.getsize(local_path)} bytes.")
        
        # Check if already registered
        existing = OcrModel.objects.filter(name=display_name).first()
        if existing:
            print(f"El modelo '{display_name}' ya estaba registrado en eScriptorium (ID: {existing.id}).")
            continue
        
        print(f"Registrando '{display_name}' en eScriptorium...")
        with open(local_path, 'rb') as f:
            model_obj = OcrModel(
                name=display_name,
                job=OcrModel.MODEL_JOB_RECOGNIZE,
                owner=admin_user,
                script='Latin',
                public=True,
            )
            model_obj.file.save(fname, File(f), save=True)
            model_obj.file_size = os.path.getsize(local_path)
            model_obj.save()
        print(f"-> Modelo '{display_name}' registrado exitosamente con ID {model_obj.id}!")
    except Exception as e:
        print(f"Error procesando {record_id}: {e}")

print("\n=== Todos los modelos han sido procesados ===")
