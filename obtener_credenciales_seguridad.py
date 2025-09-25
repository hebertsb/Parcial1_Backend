#!/usr/bin/env python
"""
Script para obtener credenciales de usuarios de seguridad
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from authz.models import Usuario, Persona, Rol

def mostrar_usuarios_seguridad():
    """Mostrar información de usuarios de seguridad existentes"""
    print("🔐 USUARIOS DE SEGURIDAD - INFORMACIÓN DE LOGIN")
    print("=" * 55)
    
    usuarios_seguridad = Usuario.objects.filter(roles__nombre='Seguridad')
    
    if not usuarios_seguridad.exists():
        print("❌ No hay usuarios de seguridad en el sistema")
        return
    
    print(f"📊 Total usuarios de seguridad: {usuarios_seguridad.count()}\n")
    
    for i, usuario in enumerate(usuarios_seguridad, 1):
        print(f"👤 USUARIO {i}:")
        print(f"   📧 Email: {usuario.email}")
        print(f"   👤 Nombre: {usuario.persona.nombre_completo if usuario.persona else 'Sin nombre'}")
        print(f"   📄 Documento: {usuario.persona.documento_identidad if usuario.persona else 'Sin documento'}")
        print(f"   🔘 Estado: {usuario.estado}")
        print(f"   📅 Creado: {usuario.date_joined.strftime('%Y-%m-%d %H:%M')}")
        print(f"   🕐 Último login: {usuario.last_login.strftime('%Y-%m-%d %H:%M') if usuario.last_login else 'Nunca'}")
        print(f"   🔑 Password: ❓ (Desconocido - ver opciones abajo)")
        print()
    
    print("=" * 55)
    print("🔑 POSIBLES PASSWORDS:")
    print("Los usuarios creados pueden tener estos patterns de password:")
    print()
    
    for usuario in usuarios_seguridad:
        doc = usuario.persona.documento_identidad if usuario.persona else ""
        print(f"📧 {usuario.email}:")
        
        # Patterns comunes que usamos
        if doc:
            print(f"   • seg{doc[:4]}2024")
            print(f"   • seg{doc}2024")
            print(f"   • seguridad{doc}")
        
        print(f"   • seguridad2024")
        print(f"   • seg2024")
        print(f"   • 123456 (default)")
        print()

def resetear_password_usuario():
    """Función para resetear password de un usuario específico"""
    print("\n🔧 RESETEAR PASSWORD DE USUARIO")
    print("=" * 35)
    
    usuarios = Usuario.objects.filter(roles__nombre='Seguridad')
    
    if not usuarios.exists():
        print("❌ No hay usuarios de seguridad")
        return
    
    print("Usuarios disponibles:")
    for i, usuario in enumerate(usuarios, 1):
        print(f"{i}. {usuario.email} - {usuario.persona.nombre_completo if usuario.persona else 'Sin nombre'}")
    
    print(f"\n📝 Para resetear password de un usuario específico:")
    print(f"python manage.py shell -c \"")
    print(f"from authz.models import Usuario")
    print(f"usuario = Usuario.objects.get(email='EMAIL_AQUI')")
    print(f"usuario.set_password('NUEVO_PASSWORD')")
    print(f"usuario.save()")
    print(f"print(f'Password actualizado para {{usuario.email}}')\"")
    
def crear_usuario_prueba():
    """Crear un usuario de pruebas con credenciales conocidas"""
    print("\n🧪 CREAR USUARIO DE PRUEBAS")
    print("=" * 30)
    
    email_prueba = "prueba.seguridad@test.com"
    password_prueba = "prueba123"
    
    # Verificar si ya existe
    if Usuario.objects.filter(email=email_prueba).exists():
        print(f"✅ Usuario de prueba ya existe:")
        print(f"📧 Email: {email_prueba}")
        print(f"🔑 Password: {password_prueba}")
        return
    
    try:
        # Crear persona
        persona = Persona.objects.create(
            nombre="Usuario",
            apellido="Pruebas Seguridad",
            documento_identidad="PRUEBA001",
            email=email_prueba,
            telefono="+591 70000000",
            tipo_persona='seguridad',
            activo=True
        )
        
        # Crear usuario
        usuario = Usuario.objects.create_user(
            email=email_prueba,
            password=password_prueba,
            persona=persona,
            estado='ACTIVO'
        )
        
        # Asignar rol
        rol_seguridad, _ = Rol.objects.get_or_create(
            nombre='Seguridad',
            defaults={'descripcion': 'Personal de seguridad del condominio'}
        )
        usuario.roles.add(rol_seguridad)
        
        print(f"✅ Usuario de prueba creado exitosamente!")
        print(f"📧 Email: {email_prueba}")
        print(f"🔑 Password: {password_prueba}")
        print(f"👤 Nombre: {persona.nombre_completo}")
        
    except Exception as e:
        print(f"❌ Error creando usuario de prueba: {str(e)}")

def main():
    """Función principal"""
    print("🔐 GESTIÓN DE CREDENCIALES DE SEGURIDAD")
    print("=" * 45)
    
    # Mostrar usuarios existentes
    mostrar_usuarios_seguridad()
    
    # Mostrar opciones para resetear passwords
    resetear_password_usuario()
    
    # Crear usuario de pruebas
    crear_usuario_prueba()
    
    print("\n" + "=" * 45)
    print("💡 OPCIONES DISPONIBLES:")
    print("1. Usar credenciales de usuario de prueba creado")
    print("2. Resetear password de usuario existente")
    print("3. Crear nuevo usuario con credenciales conocidas")
    print("\n🔗 ENDPOINT DE LOGIN:")
    print("POST /api/authz/auth/login/")
    print("Body: {\"email\": \"EMAIL\", \"password\": \"PASSWORD\"}")

if __name__ == "__main__":
    main()