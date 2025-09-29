#!/usr/bin/env python
"""
Script para verificar usuarios y copropietarios en la base de datos
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from authz.models import Usuario
from seguridad.models import Copropietarios

def verificar_usuarios():
    print("👥 USUARIOS EN LA BASE DE DATOS")
    print("=" * 60)
    
    usuarios = Usuario.objects.all()
    print(f"Total de usuarios: {usuarios.count()}")
    
    if usuarios.exists():
        print("\nDetalles de usuarios:")
        for usuario in usuarios:
            print(f"\n🔍 Usuario ID: {usuario.id}")
            print(f"   Email: {usuario.email}")
            print(f"   Activo: {usuario.is_active}")
            print(f"   Staff: {getattr(usuario, 'is_staff', False)}")
            print(f"   Estado: {usuario.estado}")
            
            # Verificar si tiene persona asociada
            if hasattr(usuario, 'persona') and usuario.persona:
                print(f"   Persona: {usuario.persona.nombre} {usuario.persona.apellido}")
                print(f"   Teléfono: {usuario.persona.telefono}")
            else:
                print(f"   Persona: NO TIENE PERSONA ASOCIADA")
    else:
        print("❌ No hay usuarios en el sistema")

def verificar_copropietarios():
    print("\n🏠 COPROPIETARIOS EN LA BASE DE DATOS")
    print("=" * 60)
    
    copropietarios = Copropietarios.objects.all()
    print(f"Total de copropietarios: {copropietarios.count()}")
    
    if copropietarios.exists():
        print("\nDetalles de copropietarios:")
        for coprop in copropietarios:
            print(f"\n🏠 Copropietario ID: {coprop.id}")
            print(f"   Nombre: {coprop.nombres} {coprop.apellidos}")
            print(f"   Email: {coprop.email}")
            print(f"   Teléfono: {coprop.telefono}")
            print(f"   Unidad: {coprop.unidad_residencial}")
            print(f"   Tipo: {coprop.tipo_residente}")
            print(f"   Activo: {coprop.activo}")
            
            # Verificar si tiene usuario del sistema
            if hasattr(coprop, 'usuario_sistema') and coprop.usuario_sistema:
                print(f"   Usuario Sistema: {coprop.usuario_sistema.email} (ID: {coprop.usuario_sistema.id})")
            else:
                print(f"   Usuario Sistema: NO TIENE USUARIO ASOCIADO")
    else:
        print("❌ No hay copropietarios en el sistema")

def buscar_usuario_id_8():
    print("\n🔍 BÚSQUEDA ESPECÍFICA: USUARIO ID 8")
    print("=" * 60)
    
    # Buscar en usuarios
    try:
        usuario = Usuario.objects.get(id=8)
        print(f"✅ Usuario ID 8 encontrado:")
        print(f"   Email: {usuario.email}")
        print(f"   Estado: {usuario.estado}")
        
        # Buscar copropietario asociado
        try:
            copropietario = Copropietarios.objects.get(usuario_sistema=usuario)
            print(f"✅ Copropietario asociado encontrado:")
            print(f"   ID: {copropietario.id}")
            print(f"   Nombre: {copropietario.nombres} {copropietario.apellidos}")
        except Copropietarios.DoesNotExist:
            print(f"❌ Usuario ID 8 NO tiene copropietario asociado")
            
    except Usuario.DoesNotExist:
        print(f"❌ Usuario ID 8 NO existe")
        
        # Mostrar IDs disponibles
        ids_disponibles = list(Usuario.objects.values_list('id', flat=True))
        print(f"📋 IDs de usuarios disponibles: {ids_disponibles}")

def crear_copropietario_prueba():
    print("\n🛠️ CREAR COPROPIETARIO DE PRUEBA")
    print("=" * 60)
    
    # Buscar un usuario sin copropietario asociado
    usuarios_sin_coprop = Usuario.objects.filter(
        copropietario_perfil__isnull=True
    ).exclude(
        email__icontains='admin'
    )
    
    if usuarios_sin_coprop.exists():
        usuario = usuarios_sin_coprop.first()
        
        # Verificar que el usuario no sea None
        if usuario is not None:
            print(f"🎯 Usando usuario: {usuario.email} (ID: {usuario.id})")
            
            try:
                # Crear copropietario
                copropietario = Copropietarios.objects.create(
                    nombres="Test",
                    apellidos="Copropietario",
                    numero_documento="12345678",
                    email=usuario.email,
                    telefono="70000000",
                    unidad_residencial="101A",
                    tipo_residente="Propietario",
                    activo=True,
                    usuario_sistema=usuario
                )
                
                print(f"✅ Copropietario creado exitosamente:")
                print(f"   ID: {copropietario.id}")
                print(f"   Nombre: {copropietario.nombres} {copropietario.apellidos}")
                print(f"   Unidad: {copropietario.unidad_residencial}")
                print(f"   Usuario asociado: {usuario.email} (ID: {usuario.id})")
                
                return copropietario.id, usuario.id
                
            except Exception as e:
                print(f"❌ Error creando copropietario: {e}")
                return None, None
        else:
            print("❌ Usuario obtenido es None")
            return None, None
    else:
        print("❌ No hay usuarios disponibles para crear copropietario")
        return None, None

def mostrar_sql_raw():
    print("\n💾 CONSULTA SQL DIRECTA")
    print("=" * 60)
    
    from django.db import connection
    
    # Usuarios
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, email, is_active, estado FROM authz_usuario LIMIT 10")
        usuarios_sql = cursor.fetchall()
        
        print("📋 USUARIOS (authz_usuario):")
        print("ID | Email | Activo | Estado")
        print("-" * 50)
        for row in usuarios_sql:
            print(f"{row[0]} | {row[1]} | {row[2]} | {row[3]}")
    
    # Copropietarios
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT c.id, c.nombres, c.apellidos, c.email, c.unidad_residencial, c.usuario_sistema_id 
            FROM copropietarios c 
            LIMIT 10
        """)
        coprop_sql = cursor.fetchall()
        
        print("\n🏠 COPROPIETARIOS (copropietarios):")
        print("ID | Nombre | Apellido | Email | Unidad | Usuario_ID")
        print("-" * 65)
        for row in coprop_sql:
            print(f"{row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]} | {row[5]}")

def main():
    print("🚨 DIAGNÓSTICO URGENTE: USUARIO ID 8")
    print("=" * 60)
    
    verificar_usuarios()
    verificar_copropietarios()
    buscar_usuario_id_8()
    mostrar_sql_raw()
    
    print("\n🛠️ ¿CREAR COPROPIETARIO DE PRUEBA?")
    crear_id, usuario_id = crear_copropietario_prueba()
    
    if crear_id:
        print(f"\n✅ SOLUCIÓN INMEDIATA:")
        print(f"   Usar usuario_id: {usuario_id}")
        print(f"   Copropietario ID: {crear_id}")
        print(f"   El endpoint ahora debería funcionar con usuario_id={usuario_id}")

if __name__ == "__main__":
    main()