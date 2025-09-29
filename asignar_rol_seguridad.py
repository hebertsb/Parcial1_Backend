#!/usr/bin/env python
"""
Script simplificado para asignar rol de seguridad al usuario existente
"""
import os
import sys
import django

# Setup Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from authz.models import Usuario, Rol

def asignar_rol_seguridad():
    """Asignar rol de seguridad al usuario existente"""
    print("🔐 ASIGNANDO ROL DE SEGURIDAD")
    print("=" * 40)
    
    try:
        # 1. Obtener usuario de seguridad
        usuario_seguridad = Usuario.objects.get(email='seguridad@facial.com')
        print(f"✅ Usuario encontrado: {usuario_seguridad.email}")
        
        # 2. Crear o obtener rol de seguridad
        rol_security, created = Rol.objects.get_or_create(
            nombre='security',
            defaults={'descripcion': 'Personal de seguridad del condominio'}
        )
        
        if created:
            print("✅ Rol 'security' creado")
        else:
            print("ℹ️  Rol 'security' ya existe")
        
        # 3. Asignar rol si no lo tiene
        if not usuario_seguridad.roles.filter(nombre='security').exists():
            usuario_seguridad.roles.add(rol_security)
            print("✅ Rol 'security' asignado al usuario")
        else:
            print("ℹ️  Usuario ya tiene rol 'security'")
        
        # 4. Mostrar información del usuario
        print(f"\n📋 INFORMACIÓN DEL USUARIO:")
        print(f"   ID: {usuario_seguridad.id}")
        print(f"   Email: {usuario_seguridad.email}")
        print(f"   Activo: {usuario_seguridad.is_active}")
        print(f"   Estado: {usuario_seguridad.estado}")
        if usuario_seguridad.persona:
            print(f"   Persona: {usuario_seguridad.persona.nombre} {usuario_seguridad.persona.apellido}")
        print(f"   Roles: {[rol.nombre for rol in usuario_seguridad.roles.all()]}")
        
        print(f"\n✅ CONFIGURACIÓN COMPLETA")
        print(f"El usuario seguridad@facial.com ahora tiene permisos para:")
        print(f"- Ver fotos de reconocimiento de TODOS los usuarios")
        print(f"- Acceder a todos los endpoints del dashboard de seguridad")
        
        return True
        
    except Usuario.DoesNotExist:
        print("❌ Usuario seguridad@facial.com no encontrado")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    asignar_rol_seguridad()