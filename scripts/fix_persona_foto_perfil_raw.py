# Script para actualizar los enlaces de foto_perfil en Persona a formato raw Dropbox
from authz.models import Persona
from django.db import transaction

def dropbox_to_raw(url):
    if url and url.startswith("https://www.dropbox.com/scl/fi/"):
        url = url.replace("https://www.dropbox.com/scl/fi/", "https://dl.dropboxusercontent.com/scl/fi/")
        url = url.replace("?dl=0", "")
        url = url.replace("?dl=1", "")
    return url

if __name__ == "__main__":
    with transaction.atomic():
        personas = Persona.objects.all()
        for persona in personas:
            original = persona.foto_perfil
            raw = dropbox_to_raw(original)
            if original != raw:
                persona.foto_perfil = raw
                persona.save()
                print(f"Actualizado: {persona.id} -> {raw}")
            else:
                print(f"Sin cambios: {persona.id}")
print("Proceso terminado.")
