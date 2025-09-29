#!/usr/bin/env python
"""
Script para crear/resetear credenciales de usuarios para pruebas
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from authz.models import Usuario, Persona, Rol
from seguridad.models import Copropietarios, ReconocimientoFacial
from django.contrib.auth.hashers import make_password

def crear_usuario_propietario_prueba():
    """Crear un usuario propietario de prueba"""
    print("🔧 Creando usuario propietario de prueba...")
    
    # Crear persona
    persona, created = Persona.objects.get_or_create(
        nombre="Juan Carlos",
        apellido="Pérez López",
        defaults={
            'fecha_nacimiento': '1990-01-15',
            'telefono': '70123456',
            'direccion': 'Av. Ejemplo 123'
        }
    )
    
    # Crear usuario del sistema
    usuario, created = Usuario.objects.get_or_create(
        username="propietario_prueba",
        defaults={
            'email': 'propietario.prueba@email.com',
            'persona': persona,
            'is_active': True
        }
    )
    
    if created:
        print(f"✅ Usuario creado: {usuario.username}")
    else:
        print(f"ℹ️ Usuario ya existe: {usuario.username}")
    
    # Establecer contraseña
    usuario.set_password('123456')
    usuario.save()
    print(f"🔑 Contraseña establecida: 123456")
    
    # Asignar rol de Propietario
    rol_propietario, _ = Rol.objects.get_or_create(
        nombre='Propietario',
        defaults={'descripcion': 'Propietario del condominio'}
    )
    usuario.roles.add(rol_propietario)
    
    # Crear copropietario
    copropietario, created = Copropietarios.objects.get_or_create(
        numero_documento="12345678",
        defaults={
            'nombres': persona.nombre,
            'apellidos': persona.apellido,
            'tipo_documento': 'CI',
            'unidad_residencial': 'A-101',
            'tipo_residente': 'Propietario',
            'telefono': persona.telefono,
            'email': usuario.email,
            'usuario_sistema': usuario,
            'activo': True
        }
    )
    
    if created:
        print(f"✅ Copropietario creado: {copropietario.nombres} {copropietario.apellidos}")
    else:
        print(f"ℹ️ Copropietario ya existe: {copropietario.nombres} {copropietario.apellidos}")
    
    return usuario, copropietario

def crear_usuario_seguridad_prueba():
    """Crear un usuario de seguridad de prueba"""
    print("🔧 Creando usuario de seguridad de prueba...")
    
    # Crear persona
    persona, created = Persona.objects.get_or_create(
        nombre="Carlos",
        apellido="Seguridad",
        defaults={
            'fecha_nacimiento': '1985-05-20',
            'telefono': '70987654',
            'direccion': 'Oficina Seguridad'
        }
    )
    
    # Crear usuario del sistema
    usuario, created = Usuario.objects.get_or_create(
        username="seguridad_prueba",
        defaults={
            'email': 'seguridad.prueba@email.com',
            'persona': persona,
            'is_active': True
        }
    )
    
    if created:
        print(f"✅ Usuario creado: {usuario.username}")
    else:
        print(f"ℹ️ Usuario ya existe: {usuario.username}")
    
    # Establecer contraseña
    usuario.set_password('seguridad123')
    usuario.save()
    print(f"🔑 Contraseña establecida: seguridad123")
    
    # Asignar rol de Seguridad
    rol_seguridad, _ = Rol.objects.get_or_create(
        nombre='Seguridad',
        defaults={'descripcion': 'Personal de seguridad del condominio'}
    )
    usuario.roles.add(rol_seguridad)
    
    return usuario

def resetear_contraseña_usuario(username, nueva_password):
    """Resetear contraseña de un usuario específico"""
    try:
        usuario = Usuario.objects.get(username=username)
        usuario.set_password(nueva_password)
        usuario.save()
        print(f"✅ Contraseña actualizada para {username}: {nueva_password}")
        return True
    except Usuario.DoesNotExist:
        print(f"❌ Usuario {username} no encontrado")
        return False

def listar_usuarios_existentes():
    """Listar todos los usuarios del sistema"""
    print("\n" + "=" * 60)
    print("👥 USUARIOS EXISTENTES EN EL SISTEMA")
    print("=" * 60)
    
    usuarios = Usuario.objects.filter(is_active=True).order_by('username')
    
    for usuario in usuarios:
        print(f"👤 {usuario.username}")
        print(f"   📧 Email: {usuario.email}")
        roles = [rol.nombre for rol in usuario.roles.all()]
        print(f"   🏷️ Roles: {', '.join(roles) if roles else 'Sin roles'}")
        
        # Verificar si es propietario
        try:
            copropietario = Copropietarios.objects.get(usuario_sistema=usuario)
            print(f"   🏠 Unidad: {copropietario.unidad_residencial}")
            print(f"   📋 Documento: {copropietario.numero_documento}")
        except Copropietarios.DoesNotExist:
            print(f"   ℹ️ No es copropietario")
        
        print()

def main():
    print("=" * 80)
    print("🔧 GESTIÓN DE CREDENCIALES PARA PRUEBAS")
    print("=" * 80)
    
    while True:
        print("\nOpciones disponibles:")
        print("1. Listar usuarios existentes")
        print("2. Crear usuario propietario de prueba")
        print("3. Crear usuario de seguridad de prueba")
        print("4. Resetear contraseña de usuario específico")
        print("5. Salir")
        
        opcion = input("\nSelecciona una opción (1-5): ").strip()
        
        if opcion == '1':
            listar_usuarios_existentes()
            
        elif opcion == '2':
            usuario, copropietario = crear_usuario_propietario_prueba()
            print(f"\n✅ Usuario propietario creado exitosamente!")
            print(f"   Username: {usuario.username}")
            print(f"   Password: 123456")
            print(f"   Email: {usuario.email}")
            print(f"   Unidad: {copropietario.unidad_residencial}")
            
        elif opcion == '3':
            usuario = crear_usuario_seguridad_prueba()
            print(f"\n✅ Usuario de seguridad creado exitosamente!")
            print(f"   Username: {usuario.username}")
            print(f"   Password: seguridad123")
            print(f"   Email: {usuario.email}")
            
        elif opcion == '4':
            username = input("Ingresa el username del usuario: ").strip()
            password = input("Ingresa la nueva contraseña: ").strip()
            resetear_contraseña_usuario(username, password)
            
        elif opcion == '5':
            print("👋 ¡Hasta luego!")
            break
            
        else:
            print("❌ Opción no válida")

if __name__ == '__main__':
    main()