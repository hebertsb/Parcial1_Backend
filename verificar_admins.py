#!/usr/bin/env python
import django
import os
import sys
from typing import cast

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from authz.models import Usuario, Rol

print("=== VERIFICACIÓN DE ADMINISTRADORES ===")

# Verificar si existe el rol Administrador
try:
    rol_admin = cast(Rol, Rol.objects.get(nombre='Administrador'))
    print(f"✅ Rol 'Administrador' existe: ID {rol_admin.pk}")
except Rol.DoesNotExist:
    print("❌ ERROR: No existe el rol 'Administrador'")
    print("Roles disponibles:")
    for rol in Rol.objects.all():
        print(f"  - {rol.nombre}")
    exit(1)

# Verificar administradores
admins = Usuario.objects.filter(roles__nombre='Administrador')
print(f"\n📊 Total de usuarios con rol Administrador: {admins.count()}")

if admins.count() == 0:
    print("❌ ERROR: No hay usuarios con rol Administrador")
    print("\n🔧 Para crear un administrador, ejecuta:")
    print("python manage.py createsuperuser")
else:
    print("\n👥 Lista de administradores:")
    for admin in admins:
        estado_emoji = "✅" if admin.estado == 'ACTIVO' else "❌"
        print(f"  {estado_emoji} {admin.email} - Estado: {admin.estado}")

# Verificar administradores activos específicamente
admins_activos = Usuario.objects.filter(roles__nombre='Administrador', estado='ACTIVO')
print(f"\n📧 Administradores ACTIVOS (que recibirán emails): {admins_activos.count()}")

if admins_activos.count() == 0:
    print("❌ ERROR: No hay administradores ACTIVOS que puedan recibir notificaciones")
    print("Las solicitudes se crean pero los admins no reciben emails")
else:
    print("Emails de administradores activos:")
    for admin in admins_activos:
        print(f"  📧 {admin.email}")

print("\n=== CONFIGURACIÓN DE EMAIL ===")
from django.conf import settings

try:
    print(f"DEFAULT_FROM_EMAIL: {getattr(settings, 'DEFAULT_FROM_EMAIL', 'NO CONFIGURADO')}")
    print(f"EMAIL_BACKEND: {getattr(settings, 'EMAIL_BACKEND', 'NO CONFIGURADO')}")
    print(f"EMAIL_HOST: {getattr(settings, 'EMAIL_HOST', 'NO CONFIGURADO')}")
except Exception as e:
    print(f"Error verificando configuración email: {e}")