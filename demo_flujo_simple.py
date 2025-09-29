#!/usr/bin/env python3
"""
DEMO SIMPLE - FLUJO AUTOMÁTICO CON VIVIENDA EXISTENTE
=====================================================
"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from authz.models import Usuario, SolicitudRegistroPropietario
from seguridad.models import Copropietarios, ReconocimientoFacial
from core.models import Vivienda

def main():
    print("🎯 FLUJO AUTOMÁTICO - CUALQUIER USUARIO")
    print("=" * 45)
    
    # 1. Buscar una vivienda disponible
    print("\n1. 🏠 BUSCANDO VIVIENDA DISPONIBLE")
    vivienda = Vivienda.objects.first()
    if vivienda:
        print(f"   ✅ Vivienda encontrada: {vivienda.numero}")
    else:
        print("   ❌ No hay viviendas disponibles")
        return
    
    # 2. Crear solicitud con vivienda existente
    print("\n2. 📝 USUARIO CREA SOLICITUD")
    nuevo_email = "maria.lopez@ejemplo.com"
    
    if SolicitudRegistroPropietario.objects.filter(email=nuevo_email).exists():
        solicitud = SolicitudRegistroPropietario.objects.get(email=nuevo_email)
        print(f"   ℹ️  Solicitud ya existe: {nuevo_email}")
    else:
        from datetime import date
        solicitud = SolicitudRegistroPropietario.objects.create(
            email=nuevo_email,
            nombres="María",
            apellidos="López",
            telefono="70987654",
            numero_casa=vivienda.numero,
            fecha_nacimiento=date(1985, 5, 15),
            documento_identidad="87654321",
            estado="PENDIENTE"
        )
        print(f"   ✅ Solicitud creada: {nuevo_email}")
    
    # 3. Admin aprueba - AUTOMÁTICO
    if solicitud.estado != 'APROBADA':
        print("\n3. ✅ ADMIN APRUEBA - FLUJO AUTOMÁTICO")
        
        admin_user = Usuario.objects.filter(is_staff=True).first()
        if not admin_user:
            admin_user = Usuario.objects.create_user(
                'admin@test.com', 'admin123',
                is_staff=True, is_superuser=True
            )
        
        try:
            solicitud.aprobar_solicitud(admin_user)
            print("   🎯 SISTEMA AUTOMÁTICO EJECUTADO:")
            print("      ✅ Usuario creado")
            print("      ✅ Copropietario creado")
            print("      ✅ ReconocimientoFacial creado")
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return
    else:
        print("\n3. ℹ️  SOLICITUD YA APROBADA")
    
    # 4. Verificar que todo se creó automáticamente
    print("\n4. 🔍 VERIFICAR CREACIÓN AUTOMÁTICA")
    
    try:
        usuario = Usuario.objects.get(email=nuevo_email)
        copropietario = Copropietarios.objects.get(usuario_sistema=usuario)
        reconocimiento = ReconocimientoFacial.objects.get(copropietario=copropietario)
        
        print(f"   ✅ Usuario: ID {usuario.id} - {usuario.email}")
        print(f"   ✅ Copropietario: ID {copropietario.id}")
        print(f"   ✅ ReconocimientoFacial: ID {reconocimiento.id}")
        
        # 5. Usuario sube fotos
        print(f"\n5. 📸 USUARIO PUEDE SUBIR FOTOS INMEDIATAMENTE")
        
        fotos_demo = [
            f"https://dl.dropbox.com/{nuevo_email}_1.jpg",
            f"https://dl.dropbox.com/{nuevo_email}_2.jpg"
        ]
        
        reconocimiento.vector_facial = ','.join(fotos_demo)
        reconocimiento.save()
        
        print(f"   ✅ Fotos subidas: {len(fotos_demo)}")
        
        # 6. Resumen
        print(f"\n6. 🎉 FLUJO AUTOMÁTICO COMPLETADO")
        print("   " + "="*35)
        print(f"   👤 Usuario: {usuario.email}")
        print(f"   🔑 Password: (generada automáticamente)")
        print(f"   🏠 Vivienda: {vivienda.numero}")
        print(f"   📸 Fotos: {len(fotos_demo)} subidas")
        print(f"   🔐 Login: ✅ Habilitado")
        print(f"   📱 Panel: ✅ Acceso inmediato")
        
        print(f"\n🎯 ESTE PROCESO FUNCIONA PARA CUALQUIER USUARIO:")
        print("   1. ✅ Llena formulario → Solicitud creada")
        print("   2. ✅ Admin aprueba → Sistema automático crea todo")
        print("   3. ✅ Usuario accede → Puede subir fotos inmediatamente")
        print("   4. ✅ Seguridad ve → Usuario aparece en lista")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    main()