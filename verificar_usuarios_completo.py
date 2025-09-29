#!/usr/bin/env python3
"""
Script para verificar usuarios existentes y crear usuario de prueba
"""

import os
import sys
import django

# Configurar Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from authz.models import Usuario, Rol

def verificar_usuarios_existentes():
    """Verificar todos los usuarios existentes"""
    
    print("👥 USUARIOS EXISTENTES EN EL SISTEMA:")
    print("=" * 60)
    
    usuarios = Usuario.objects.all()
    
    for usuario in usuarios:
        print(f"📧 Email: {usuario.email}")
        print(f"   • ID: {usuario.id}")
        print(f"   • Activo: {usuario.is_active}")
        print(f"   • Estado: {usuario.estado}")
        
        # Ver roles
        roles = usuario.roles.all()
        if roles:
            print(f"   • Roles: {[rol.nombre for rol in roles]}")
        else:
            print("   • Sin roles asignados")
            
        # Ver si tiene persona asociada
        if usuario.persona:
            print(f"   • Persona: {usuario.persona.nombre} {usuario.persona.apellido}")
        else:
            print("   • Sin persona asociada")
        
        print()

def verificar_roles():
    """Verificar roles disponibles"""
    
    print("🎭 ROLES DISPONIBLES:")
    print("=" * 30)
    
    roles = Rol.objects.all()
    
    for rol in roles:
        print(f"• {rol.nombre}: {rol.descripcion or 'Sin descripción'}")

def probar_login(email, password):
    """Probar login con credenciales específicas"""
    
    print(f"\n🔐 PROBANDO LOGIN: {email}")
    print("=" * 40)
    
    try:
        usuario = Usuario.objects.get(email=email)
        print(f"✅ Usuario encontrado: {usuario.email}")
        
        if usuario.check_password(password):
            print(f"✅ Contraseña correcta")
            
            # Ver roles
            roles = usuario.roles.all()
            print(f"   • Roles: {[rol.nombre for rol in roles]}")
            
            return True
        else:
            print(f"❌ Contraseña incorrecta")
            return False
            
    except Usuario.DoesNotExist:
        print(f"❌ Usuario no existe: {email}")
        return False

def crear_usuario_test():
    """Crear usuario de prueba para panel propietarios"""
    
    email = "propietario.test@example.com"
    password = "testing123"
    
    print(f"\n🔧 CREANDO USUARIO DE PRUEBA: {email}")
    print("=" * 50)
    
    # Verificar si ya existe
    if Usuario.objects.filter(email=email).exists():
        usuario = Usuario.objects.get(email=email)
        print(f"✅ Usuario ya existe: {email}")
    else:
        # Crear usuario
        usuario = Usuario.objects.create_user(
            email=email,
            password=password,
            is_active=True
        )
        print(f"✅ Usuario creado: {email}")
    
    # Asegurar que tiene la contraseña correcta
    usuario.set_password(password)
    usuario.save()
    
    # Asignar rol de Propietario
    try:
        rol_propietario = Rol.objects.get(nombre='Propietario')
        usuario.roles.add(rol_propietario)
        print(f"✅ Rol 'Propietario' asignado")
    except Rol.DoesNotExist:
        # Crear rol si no existe
        rol_propietario = Rol.objects.create(
            nombre='Propietario',
            descripcion='Propietario de unidad habitacional'
        )
        usuario.roles.add(rol_propietario)
        print(f"✅ Rol 'Propietario' creado y asignado")
    
    return usuario, password

if __name__ == "__main__":
    print("🔍 DIAGNÓSTICO DE USUARIOS DEL SISTEMA")
    print("=" * 60)
    
    # Verificar usuarios existentes
    verificar_usuarios_existentes()
    
    # Verificar roles
    verificar_roles()
    
    # Probar algunos logins conocidos
    credenciales_conocidas = [
        ('seguridad@facial.com', 'testing123'),
        ('lara@gmail.com', 'testing123'),
        ('admin@sistema.com', 'admin123'),
    ]
    
    for email, password in credenciales_conocidas:
        resultado = probar_login(email, password)
    
    # Crear usuario de prueba
    usuario_test, password_test = crear_usuario_test()
    
    print(f"\n🎯 RESULTADO FINAL:")
    print("=" * 60)
    print(f"✅ Usuario para probar endpoints del panel:")
    print(f"   Email: {usuario_test.email}")
    print(f"   Password: {password_test}")
    print(f"   Roles: {[rol.nombre for rol in usuario_test.roles.all()]}")
    
    # Probar el login del usuario test
    probar_login(usuario_test.email, password_test)