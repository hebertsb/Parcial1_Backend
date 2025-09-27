#!/usr/bin/env python3
"""
Script para verificar si el usuario tiene persona asociada
"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from authz.models import Usuario

def verificar_persona():
    try:
        usuario = Usuario.objects.get(email="usuario_prueba@test.com")
        print(f"✅ Usuario: {usuario.email}")
        print(f"   Persona: {usuario.persona}")
        if usuario.persona:
            print(f"   Nombre: {usuario.persona.nombre}")
            print(f"   Apellido: {usuario.persona.apellido}")
            print(f"   Teléfono: {usuario.persona.telefono}")
        else:
            print("❌ Usuario no tiene persona asociada")
    except Usuario.DoesNotExist:
        print("❌ Usuario no encontrado")

if __name__ == "__main__":
    verificar_persona()