#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from authz.models import Usuario

print("=== USUARIOS REGISTRADOS ===")
usuarios = Usuario.objects.all()
if usuarios:
    for u in usuarios:
        print(f"Email: {u.email}")
        print(f"Estado: {u.estado}")
        print(f"Roles: {list(u.roles.values_list('nombre', flat=True))}")
        if hasattr(u, 'persona') and u.persona:
            print(f"Persona: {u.persona.nombre} {u.persona.apellido}")
        print("---")
else:
    print("No hay usuarios registrados")