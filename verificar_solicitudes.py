#!/usr/bin/env python
import django
import os
import sys

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from authz.models import SolicitudRegistroPropietario

print("=== VERIFICACIÓN DE SOLICITUDES ===")

# Verificar todas las solicitudes
total_solicitudes = SolicitudRegistroPropietario.objects.all().count()
print(f"📊 Total de solicitudes en el sistema: {total_solicitudes}")

# Verificar solicitudes por estado
for estado, descripcion in SolicitudRegistroPropietario.ESTADO_CHOICES:
    count = SolicitudRegistroPropietario.objects.filter(estado=estado).count()
    if count > 0:
        print(f"  {estado}: {count} solicitudes")

print("\n=== SOLICITUDES PENDIENTES ===")
pendientes = SolicitudRegistroPropietario.objects.filter(estado='PENDIENTE').order_by('-created_at')

if pendientes.count() == 0:
    print("❌ No hay solicitudes pendientes")
else:
    print(f"✅ {pendientes.count()} solicitudes pendientes:")
    for s in pendientes[:10]:  # Mostrar las últimas 10
        print(f"  📝 {s.nombres} {s.apellidos}")
        print(f"     📧 {s.email}")
        print(f"     🏠 {s.numero_casa}")
        print(f"     📅 {s.created_at}")
        print(f"     🆔 Token: {s.token_seguimiento}")
        print("     ---")

print("\n=== ÚLTIMAS 5 SOLICITUDES (cualquier estado) ===")
ultimas = SolicitudRegistroPropietario.objects.all().order_by('-created_at')[:5]
for s in ultimas:
    print(f"  📝 {s.nombres} {s.apellidos} - {s.estado} - {s.created_at}")