#!/usr/bin/env python3
"""
Script para verificar usuarios propietarios y sus contraseñas
"""

import os
import sys
import django

# Configurar Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from authz.models import Usuario

def verificar_usuarios_propietarios():
    """Verificar usuarios con rol propietario"""
    
    print("👥 USUARIOS CON ROL PROPIETARIO:")
    print("=" * 50)
    
    usuarios_propietarios = Usuario.objects.filter(rol='Propietario')
    
    if not usuarios_propietarios.exists():
        print("❌ No hay usuarios con rol 'Propietario'")
        return
    
    for usuario in usuarios_propietarios:
        print(f"📧 Email: {usuario.email}")
        print(f"   • ID: {usuario.id}")
        print(f"   • Activo: {usuario.is_active}")
        print(f"   • Rol: {usuario.rol}")
        print(f"   • Nombre: {getattr(usuario, 'first_name', 'N/A')}")
        
        # Verificar si tiene propietario asociado
        try:
            from authz.models import Propietario
            propietario = Propietario.objects.get(usuario=usuario)
            print(f"   • Propietario ID: {propietario.id}")
        except:
            print("   • Sin registro de propietario asociado")
        
        print()

def crear_usuario_propietario_test():
    """Crear usuario propietario de prueba"""
    
    email = "propietario.test@gmail.com"
    password = "testing123"
    
    # Verificar si ya existe
    if Usuario.objects.filter(email=email).exists():
        print(f"✅ Usuario {email} ya existe")
        usuario = Usuario.objects.get(email=email)
    else:
        print(f"🔧 Creando usuario propietario de prueba: {email}")
        
        usuario = Usuario.objects.create_user(
            email=email,
            password=password,
            rol='Propietario',
            is_active=True
        )
    
    # Verificar contraseña
    if usuario.check_password(password):
        print(f"✅ Contraseña correcta para {email}")
    else:
        print(f"❌ Contraseña incorrecta, estableciendo nueva...")
        usuario.set_password(password)
        usuario.save()
        print(f"✅ Contraseña actualizada para {email}")
    
    return usuario

if __name__ == "__main__":
    print("🔍 VERIFICANDO USUARIOS PROPIETARIOS")
    print("=" * 60)
    
    verificar_usuarios_propietarios()
    
    print("\n🔧 CREANDO/VERIFICANDO USUARIO DE PRUEBA")
    print("=" * 60)
    
    usuario_test = crear_usuario_propietario_test()
    
    print(f"\n✅ USUARIO PARA PRUEBAS:")
    print(f"   Email: {usuario_test.email}")
    print(f"   Password: testing123")
    print(f"   Rol: {usuario_test.rol}")
    print(f"\n🚀 Usa estas credenciales para probar los endpoints del panel")