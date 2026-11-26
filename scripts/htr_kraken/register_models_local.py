import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'escriptorium.settings')
django.setup()

from django.core.files import File
from core.models import OcrModel, Script
from users.models import User

admin_user = User.objects.filter(is_superuser=True).first() or User.objects.first()
latin_script = Script.objects.filter(name__icontains='Latin').first()

MODELS = [
    ("Tridis_Medieval_EarlyModern.mlmodel", "TRIDIS (Documental y Notarial s.XII-XVI)"),
    ("CATMUS_Medieval_1.0.0.mlmodel", "CATMuS Medieval (Castellano y Latin s.XIII-XVI)"),
    ("McCATMuS_nfd_nofix_V1.mlmodel", "McCATMuS (Espanol y Romance s.XVI-XIX)"),
]

for fname, display_name in MODELS:
    path = os.path.join('/tmp/mlmodels', fname)
    if not os.path.exists(path):
        print(f"No existe: {path}")
        continue
    
    existing = OcrModel.objects.filter(name=display_name).first()
    if existing:
        print(f"El modelo '{display_name}' ya existe (ID: {existing.id}). Actualizando a publico...")
        existing.public = True
        existing.save()
        continue
    
    with open(path, 'rb') as f:
        size = os.path.getsize(path)
        m = OcrModel(
            name=display_name,
            job=OcrModel.MODEL_JOB_RECOGNIZE,
            owner=admin_user,
            script=latin_script,
            public=True,
            file_size=size,
        )
        m.file.save(fname, File(f), save=True)
    print(f"REGISTRADO: '{display_name}' (ID: {m.id}, {m.file_size} bytes)")

print("\nModelos disponibles en eScriptorium:")
for m in OcrModel.objects.all():
    print(f" - [{m.id}] {m.name} (Job: {m.job}, Public: {m.public})")
