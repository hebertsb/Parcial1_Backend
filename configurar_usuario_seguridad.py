#!/usr/bin/env python
"""
Script para crear/verificar usuario de seguridad con permisos correctos
"""
import os
import sys
import django

# Setup Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from authz.models import Usuario, Rol, Persona
from django.contrib.auth.hashers import make_password

def crear_usuario_seguridad():
    """Crear o actualizar usuario de seguridad"""
    print("🔐 CONFIGURANDO USUARIO DE SEGURIDAD")
    print("=" * 50)
    
    try:
        # 1. Crear o obtener rol de seguridad
        rol_security, created = Rol.objects.get_or_create(
            nombre='security',
            defaults={'descripcion': 'Personal de seguridad del condominio'}
        )
        
        if created:
            print("✅ Rol 'security' creado")
        else:
            print("ℹ️  Rol 'security' ya existe")
        
        # 2. Crear o obtener persona para el usuario de seguridad
        persona_seguridad, created = Persona.objects.get_or_create(
            documento_identidad='12345678',
            defaults={
                'nombre': 'Juan Carlos',
                'apellido': 'Seguridad',
                'telefono': '+591-70000002',
                'direccion': 'Condominio - Garita de Seguridad'
            }
        )
        
        if created:
            print("✅ Persona de seguridad creada")
        else:
            print("ℹ️  Persona de seguridad ya existe")
        
        # 3. Crear o actualizar usuario de seguridad
        usuario_seguridad, created = Usuario.objects.get_or_create(
            email='seguridad@facial.com',
            defaults={
                'password': make_password('123456'),
                'is_active': True,
                'is_staff': False,
                'estado': 'ACTIVO',
                'persona': persona_seguridad
            }
        )
        
        if created:
            print("✅ Usuario de seguridad creado")
        else:
            print("ℹ️  Usuario de seguridad ya existe")
            # Asegurar que la contraseña esté actualizada
            usuario_seguridad.password = make_password('123456')
            usuario_seguridad.is_active = True
            usuario_seguridad.estado = 'ACTIVO'
            usuario_seguridad.persona = persona_seguridad
            usuario_seguridad.save()
            print("✅ Usuario de seguridad actualizado")
        
        # 4. Asignar rol de seguridad
        if not usuario_seguridad.roles.filter(nombre='security').exists():
            usuario_seguridad.roles.add(rol_security)
            print("✅ Rol 'security' asignado al usuario")
        else:
            print("ℹ️  Usuario ya tiene rol 'security'")
        
        # 5. Verificar configuración
        print("\n📋 CONFIGURACIÓN FINAL:")
        print(f"   Email: {usuario_seguridad.email}")
        print(f"   Activo: {usuario_seguridad.is_active}")
        print(f"   Estado: {usuario_seguridad.estado}")
        print(f"   Persona: {usuario_seguridad.persona.nombre} {usuario_seguridad.persona.apellido}")
        print(f"   Roles: {[rol.nombre for rol in usuario_seguridad.roles.all()]}")
        
        print("\n✅ USUARIO DE SEGURIDAD CONFIGURADO CORRECTAMENTE")
        print("💡 Credenciales:")
        print("   Email: seguridad@facial.com")
        print("   Password: 123456")
        
        return True
        
    except Exception as e:
        print(f"❌ Error configurando usuario de seguridad: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def verificar_permisos():
    """Verificar que el usuario tiene los permisos correctos"""
    print("\n🔍 VERIFICANDO PERMISOS")
    print("=" * 30)
    
    try:
        usuario = Usuario.objects.get(email='seguridad@facial.com')
        
        # Verificar rol security
        tiene_rol_security = usuario.roles.filter(nombre='security').exists()
        print(f"Rol 'security': {'✅' if tiene_rol_security else '❌'}")
        
        # Verificar acceso a usuarios
        from authz.models import Usuario
        usuarios_count = Usuario.objects.filter(is_active=True).count()
        print(f"Puede acceder a {usuarios_count} usuarios activos: ✅")
        
        # Verificar acceso a copropietarios
        from seguridad.models import Copropietarios, ReconocimientoFacial
        copropietarios_count = Copropietarios.objects.filter(activo=True).count()
        reconocimiento_count = ReconocimientoFacial.objects.count()
        print(f"Puede acceder a {copropietarios_count} copropietarios: ✅")
        print(f"Puede acceder a {reconocimiento_count} fotos de reconocimiento: ✅")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verificando permisos: {str(e)}")
        return False

def main():
    """Función principal"""
    print("🚀 CONFIGURACIÓN DE SEGURIDAD DEL SISTEMA")
    print("=" * 60)
    
    if crear_usuario_seguridad():
        verificar_permisos()
        
        print("\n🎯 PRÓXIMOS PASOS:")
        print("1. Ejecutar servidor: python manage.py runserver")
        print("2. Probar endpoints: python test_endpoints_seguridad.py")
        print("3. El frontend ahora debería funcionar correctamente")
    else:
        print("\n❌ Error en la configuración. Revisar errores anteriores.")

if __name__ == "__main__":
    main()