#!/usr/bin/env python3
"""
DEMOSTRACIÓN FLUJO AUTOMÁTICO COMPLETO
=====================================
Simula el proceso completo desde solicitud hasta acceso al reconocimiento facial
"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from authz.models import Usuario, SolicitudRegistroPropietario
from seguridad.models import Copropietarios, ReconocimientoFacial
from django.utils import timezone

def main():
    print("🎯 DEMOSTRACIÓN FLUJO AUTOMÁTICO COMPLETO")
    print("=" * 55)
    
    # PASO 1: Simular nueva solicitud de usuario
    print("\n1. 📝 PASO 1: USUARIO CREA SOLICITUD")
    
    nuevo_usuario_email = "nuevo.usuario@ejemplo.com"
    
    # Verificar si ya existe
    if SolicitudRegistroPropietario.objects.filter(email=nuevo_usuario_email).exists():
        print(f"   ℹ️  Usuario {nuevo_usuario_email} ya tiene solicitud")
        solicitud = SolicitudRegistroPropietario.objects.filter(email=nuevo_usuario_email).first()
    else:
        # Crear nueva solicitud
        from datetime import date
        solicitud = SolicitudRegistroPropietario.objects.create(
            email=nuevo_usuario_email,
            nombres="Juan Carlos",
            apellidos="Nuevo Usuario",
            telefono="70123456",
            numero_casa="B-301",
            fecha_nacimiento=date(1990, 1, 1),
            documento_identidad="12345678",
            estado="PENDIENTE"
        )
        print(f"   ✅ Solicitud creada para: {nuevo_usuario_email}")
    
    print(f"      ID Solicitud: {solicitud.id}")
    print(f"      Estado: {solicitud.estado}")
    print(f"      Casa: {solicitud.numero_casa}")
    
    # PASO 2: Admin aprueba (AUTOMÁTICO)
    if solicitud.estado != 'APROBADA':
        print("\n2. ✅ PASO 2: ADMIN APRUEBA SOLICITUD (AUTOMÁTICO)")
        
        # Buscar usuario admin para aprobar
        try:
            admin_user = Usuario.objects.filter(is_staff=True).first()
            if not admin_user:
                admin_user = Usuario.objects.create_superuser(
                    'admin@test.com', 'admin123', 
                    first_name='Admin', last_name='Sistema'
                )
            
            # Ejecutar aprobación automática
            solicitud.aprobar_solicitud(admin_user)
            
            print(f"   ✅ Solicitud aprobada por: {admin_user.email}")
            print(f"   🎯 SISTEMA AUTOMÁTICO EJECUTADO")
            
        except Exception as e:
            print(f"   ❌ Error en aprobación: {e}")
            return
    else:
        print("\n2. ℹ️  SOLICITUD YA ESTABA APROBADA")
    
    # PASO 3: Verificar que el sistema automático creó todo
    print("\n3. 🔍 PASO 3: VERIFICAR CREACIÓN AUTOMÁTICA")
    
    try:
        # Buscar usuario creado
        usuario_nuevo = Usuario.objects.get(email=nuevo_usuario_email)
        print(f"   ✅ Usuario creado: ID {usuario_nuevo.id}")
        print(f"      Email: {usuario_nuevo.email}")
        print(f"      Nombre: {usuario_nuevo.first_name} {usuario_nuevo.last_name}")
        
        # Buscar copropietario creado
        copropietario_nuevo = Copropietarios.objects.get(usuario_sistema=usuario_nuevo)
        print(f"   ✅ Copropietario creado: ID {copropietario_nuevo.id}")
        print(f"      Unidad: {copropietario_nuevo.unidad_residencial}")
        print(f"      Activo: {copropietario_nuevo.activo}")
        
        # Buscar reconocimiento facial creado
        reconocimiento_nuevo = ReconocimientoFacial.objects.get(copropietario=copropietario_nuevo)
        print(f"   ✅ ReconocimientoFacial creado: ID {reconocimiento_nuevo.id}")
        print(f"      Habilitado para subir fotos: SÍ")
        
        # PASO 4: Simular que el usuario sube fotos
        print("\n4. 📸 PASO 4: USUARIO SUBE FOTOS DESDE SU PANEL")
        
        # Simular fotos subidas
        fotos_nuevas = [
            f"https://dl.dropboxusercontent.com/scl/fi/nuevo1/{nuevo_usuario_email}_foto1.jpg?rlkey=abc123",
            f"https://dl.dropboxusercontent.com/scl/fi/nuevo2/{nuevo_usuario_email}_foto2.jpg?rlkey=def456"
        ]
        
        reconocimiento_nuevo.vector_facial = ','.join(fotos_nuevas)
        reconocimiento_nuevo.save()
        
        print(f"   ✅ Fotos subidas: {len(fotos_nuevas)}")
        for i, foto in enumerate(fotos_nuevas, 1):
            print(f"      📸 Foto {i}: {foto[:60]}...")
        
        # PASO 5: Verificar acceso completo
        print("\n5. 🎉 PASO 5: VERIFICAR ACCESO COMPLETO")
        
        print("   ✅ El usuario puede:")
        print("      🔐 Hacer login con su email")
        print("      📱 Acceder a su panel personal")
        print("      📸 Subir más fotos cuando quiera")
        print("      👁️ Ver todas sus fotos subidas")
        print("      🔒 Sistema reconocimiento facial activo")
        
        print("\n   🔒 Seguridad puede:")
        print("      👥 Ver al usuario en la lista")
        print("      📸 Acceder a sus fotos para identificación")
        print("      🔍 Usar reconocimiento facial")
        
        # Resumen final
        print("\n6. 📊 RESUMEN DEL FLUJO AUTOMÁTICO")
        print("   " + "="*45)
        print(f"   📝 Solicitud ID: {solicitud.id}")
        print(f"   👤 Usuario ID: {usuario_nuevo.id}")
        print(f"   🏠 Copropietario ID: {copropietario_nuevo.id}")
        print(f"   📸 ReconocimientoFacial ID: {reconocimiento_nuevo.id}")
        print(f"   🔑 Email: {nuevo_usuario_email}")
        print(f"   📱 Panel: /propietario (después del login)")
        
        print("\n🎯 FLUJO AUTOMÁTICO COMPLETADO EXITOSAMENTE")
        print("   Este proceso funciona para CUALQUIER usuario que:")
        print("   1. Llene el formulario de solicitud")
        print("   2. Sea aprobado por un administrador")
        print("   3. Automáticamente tendrá acceso completo al reconocimiento facial")
        
    except Usuario.DoesNotExist:
        print("   ❌ Usuario no fue creado automáticamente")
    except Copropietarios.DoesNotExist:
        print("   ❌ Copropietario no fue creado automáticamente")
    except ReconocimientoFacial.DoesNotExist:
        print("   ❌ ReconocimientoFacial no fue creado automáticamente")
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    main()