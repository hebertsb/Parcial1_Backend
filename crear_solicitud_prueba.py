#!/usr/bin/env python
import django
import os
import sys
from typing import cast

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from authz.models import SolicitudRegistroPropietario, FamiliarPropietario
from authz.email_service import EmailService
from django.utils import timezone
import uuid

print("=== CREAR SOLICITUD DE PRUEBA ===")

# Datos de la solicitud
solicitud_data = {
    'nombres': 'Ana María',
    'apellidos': 'García Silva',
    'documento_identidad': '7234567',
    'fecha_nacimiento': '1985-03-14',
    'email': 'ana.garcia@test.com',
    'telefono': '7234567',
    'numero_casa': 'A-101',
    'estado': 'PENDIENTE',
    'token_seguimiento': str(uuid.uuid4())[:8].upper(),
    'created_at': timezone.now(),
}

# Crear solicitud
try:
    solicitud = cast(SolicitudRegistroPropietario, SolicitudRegistroPropietario.objects.create(**solicitud_data))
    print(f"✅ Solicitud creada con ID: {solicitud.pk}")
    print(f"📝 Nombre: {solicitud.nombres} {solicitud.apellidos}")
    print(f"📧 Email: {solicitud.email}")
    print(f"🏠 Vivienda: {solicitud.numero_casa}")
    print(f"🎫 Token: {solicitud.token_seguimiento}")
    
    # Enviar email de confirmación
    print("\n📧 Enviando email de confirmación...")
    success = EmailService.enviar_confirmacion_solicitud(solicitud, familiares_count=0)
    
    if success:
        print("✅ Email de confirmación enviado exitosamente")
    else:
        print("❌ Error enviando email de confirmación")
        
    print(f"\n🎯 Para aprobar esta solicitud desde consola:")
    print(f"python manage.py gestionar_solicitudes --accion=aprobar --solicitud-id={solicitud.pk}")
    
    print(f"\n🎯 Para rechazar esta solicitud desde consola:")
    print(f"python manage.py gestionar_solicitudes --accion=rechazar --solicitud-id={solicitud.pk} --motivo='Motivo del rechazo'")
    
except Exception as e:
    print(f"❌ Error creando solicitud: {e}")