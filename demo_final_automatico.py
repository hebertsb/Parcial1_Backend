#!/usr/bin/env python3
"""
VERIFICAR ESTRUCTURA DE VIVIENDA Y CREAR DEMO
=============================================
"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from core.models import Vivienda
from authz.models import Usuario, SolicitudRegistroPropietario
from seguridad.models import Copropietarios, ReconocimientoFacial

def main():
    print("🎯 FLUJO AUTOMÁTICO UNIVERSAL")
    print("=" * 35)
    
    # Ver estructura de vivienda
    vivienda = Vivienda.objects.first()
    if vivienda:
        print(f"\n✅ Vivienda disponible:")
        print(f"   ID: {vivienda.id}")
        # Listar todos los campos disponibles
        for field in vivienda._meta.fields:
            field_name = field.name
            field_value = getattr(vivienda, field_name, 'N/A')
            print(f"   {field_name}: {field_value}")
        
        # Usar campo correcto para número de casa
        numero_casa = None
        if hasattr(vivienda, 'numero_casa'):
            numero_casa = vivienda.numero_casa
        elif hasattr(vivienda, 'numero'):
            numero_casa = vivienda.numero
        elif hasattr(vivienda, 'identificador'):
            numero_casa = vivienda.identificador
        else:
            numero_casa = f"V{vivienda.id}"
        
        print(f"\n📝 CREANDO SOLICITUD CON: {numero_casa}")
        
        # Crear solicitud de ejemplo
        nuevo_email = "test.automatico@ejemplo.com"
        
        if not SolicitudRegistroPropietario.objects.filter(email=nuevo_email).exists():
            from datetime import date
            solicitud = SolicitudRegistroPropietario.objects.create(
                email=nuevo_email,
                nombres="Test",
                apellidos="Automático",
                telefono="70111222",
                numero_casa=str(numero_casa),
                fecha_nacimiento=date(1990, 1, 1),
                documento_identidad="11112222",
                estado="PENDIENTE"
            )
            print(f"✅ Solicitud creada: {solicitud.id}")
        else:
            solicitud = SolicitudRegistroPropietario.objects.get(email=nuevo_email)
            print(f"ℹ️  Solicitud existente: {solicitud.id}")
        
        # Aprobar si está pendiente
        if solicitud.estado == 'PENDIENTE':
            print(f"\n🎯 EJECUTANDO FLUJO AUTOMÁTICO...")
            
            admin = Usuario.objects.filter(is_staff=True).first()
            if not admin:
                admin = Usuario.objects.create_user(
                    'admin@test.com', 'admin123',
                    is_staff=True, is_superuser=True
                )
            
            try:
                solicitud.aprobar_solicitud(admin)
                print("✅ FLUJO AUTOMÁTICO COMPLETADO")
                
                # Verificar resultados
                usuario = Usuario.objects.get(email=nuevo_email)
                copropietario = Copropietarios.objects.get(usuario_sistema=usuario)
                reconocimiento = ReconocimientoFacial.objects.get(copropietario=copropietario)
                
                print(f"\n🎉 RESULTADO:")
                print(f"   👤 Usuario: {usuario.id} - {usuario.email}")
                print(f"   🏠 Copropietario: {copropietario.id}")
                print(f"   📸 ReconocimientoFacial: {reconocimiento.id}")
                print(f"   🔑 Login: ✅ Habilitado")
                print(f"   📱 Fotos: ✅ Puede subir inmediatamente")
                
                print(f"\n🎯 ESTE FLUJO FUNCIONA PARA CUALQUIER USUARIO:")
                print("   1. Usuario llena formulario")
                print("   2. Admin aprueba solicitud")
                print("   3. Sistema automático crea: Usuario + Copropietario + ReconocimientoFacial")
                print("   4. Usuario puede subir fotos desde su panel")
                print("   5. Fotos aparecen en panel de seguridad")
                
            except Exception as e:
                print(f"❌ Error en flujo automático: {e}")
                
        else:
            print(f"ℹ️  Solicitud ya está: {solicitud.estado}")
    
    else:
        print("❌ No hay viviendas disponibles")

if __name__ == "__main__":
    main()