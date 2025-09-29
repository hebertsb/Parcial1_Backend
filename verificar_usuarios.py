#!/usr/bin/env python
"""
Verificar usuarios del sistema
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from authz.models import Usuario

def verificar_usuarios():
    print("👥 USUARIOS EN EL SISTEMA")
    print("=" * 40)
    
    usuarios = Usuario.objects.all()
    print(f"Total de usuarios: {usuarios.count()}")
    
    if usuarios.exists():
        print("\nDetalles de usuarios:")
        for i, usuario in enumerate(usuarios[:5]):  # Solo primeros 5
            print(f"\n{i+1}. Usuario ID: {usuario.id}")
            print(f"   Email: {usuario.email}")
            print(f"   Nombre: {usuario.nombre} {usuario.apellido}")
            print(f"   Tipo: {usuario.tipo_usuario}")
            print(f"   Activo: {usuario.is_active}")
            
            # Verificar si es admin
            if hasattr(usuario, 'is_staff') and usuario.is_staff:
                print(f"   ⭐ Es administrador")
            
            # Intentar login con email
            print(f"   🔑 Para login usar: email='{usuario.email}'")
    else:
        print("❌ No hay usuarios en el sistema")
        print("💡 Crear un superusuario con: python manage.py createsuperuser")

def crear_usuario_prueba():
    """Crear usuario de prueba si no existe"""
    print("\n🛠️ CREAR USUARIO DE PRUEBA")
    print("=" * 40)
    
    email_prueba = "admin@test.com"
    
    # Verificar si existe
    if Usuario.objects.filter(email=email_prueba).exists():
        print(f"✅ Usuario {email_prueba} ya existe")
        return email_prueba
    
    try:
        # Crear usuario
        usuario = Usuario.objects.create_user(
            email=email_prueba,
            password="admin123",
            nombre="Admin",
            apellido="Prueba",
            tipo_usuario="administrador"
        )
        
        # Hacer superusuario si es posible
        if hasattr(usuario, 'is_staff'):
            usuario.is_staff = True
            usuario.is_superuser = True
            usuario.save()
        
        print(f"✅ Usuario {email_prueba} creado exitosamente")
        print(f"   Contraseña: admin123")
        return email_prueba
        
    except Exception as e:
        print(f"❌ Error creando usuario: {e}")
        return None

if __name__ == "__main__":
    verificar_usuarios()
    crear_usuario_prueba()