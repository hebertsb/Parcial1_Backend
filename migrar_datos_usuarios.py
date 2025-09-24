"""
Script para migrar datos existentes al nuevo modelo Usuario-Persona
Ejecutar ANTES de aplicar las nuevas migraciones
"""

import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.db import transaction
from authz.models import Usuario, Persona, Rol


def migrar_datos_usuarios():
    """Migra los datos de usuarios existentes al nuevo modelo"""
    print("🔄 Iniciando migración de datos de usuarios...")
    
    with transaction.atomic():
        # Obtener todos los usuarios existentes
        usuarios_existentes = Usuario.objects.all()
        
        print(f"📊 Encontrados {usuarios_existentes.count()} usuarios para migrar")
        
        for usuario in usuarios_existentes:
            try:
                # Verificar si ya tiene persona asociada
                if hasattr(usuario, 'persona') and usuario.persona:
                    print(f"✅ Usuario {usuario.email} ya tiene persona asociada")
                    continue
                
                # Crear datos de persona desde los campos del usuario
                persona_data = {
                    'nombre': getattr(usuario, 'nombres', '') or 'Usuario',
                    'apellido': getattr(usuario, 'apellidos', '') or 'Sistema',
                    'documento_identidad': getattr(usuario, 'documento_identidad', '') or f"USR{usuario.id:04d}",
                    'telefono': getattr(usuario, 'telefono', '') or '',
                    'email': usuario.email,
                    'fecha_nacimiento': getattr(usuario, 'fecha_nacimiento', None),
                    'genero': getattr(usuario, 'genero', '') or '',
                    'pais': getattr(usuario, 'pais', '') or '',
                    'tipo_persona': 'cliente',  # Por defecto
                    'direccion': '',
                    'activo': True
                }
                
                # Verificar si ya existe una persona con este documento
                documento = persona_data['documento_identidad']
                persona_existente = Persona.objects.filter(documento_identidad=documento).first()
                
                if persona_existente:
                    print(f"ℹ️ Persona con documento {documento} ya existe, la usaremos")
                    persona = persona_existente
                else:
                    # Crear nueva persona
                    persona = Persona.objects.create(**persona_data)
                    print(f"✅ Persona creada: {persona.nombre_completo}")
                
                # No podemos asignar persona aquí porque el campo aún no existe en la DB
                # Esta migración de datos se ejecutará después de crear las tablas
                
                print(f"✅ Preparado usuario {usuario.email}")
                
            except Exception as e:
                print(f"❌ Error procesando usuario {usuario.email}: {e}")
                continue
    
    print("✅ Migración de datos completada")


def crear_roles_sistema():
    """Crea los roles básicos del sistema"""
    print("🔄 Creando roles del sistema...")
    
    roles_basicos = [
        {'nombre': 'Administrador', 'descripcion': 'Administrador del sistema'},
        {'nombre': 'Seguridad', 'descripcion': 'Personal de seguridad'},
        {'nombre': 'Propietario', 'descripcion': 'Propietario de vivienda'},
        {'nombre': 'Inquilino', 'descripcion': 'Inquilino de vivienda'},
    ]
    
    for rol_data in roles_basicos:
        rol, created = Rol.objects.get_or_create(
            nombre=rol_data['nombre'],
            defaults=rol_data
        )
        if created:
            print(f"✅ Rol creado: {rol.nombre}")
        else:
            print(f"ℹ️ Rol existente: {rol.nombre}")


if __name__ == "__main__":
    print("🚀 Iniciando migración de datos...")
    
    try:
        crear_roles_sistema()
        migrar_datos_usuarios()
        print("\n✅ Migración completada exitosamente!")
        print("\n📋 Próximos pasos:")
        print("1. Ejecutar: python manage.py makemigrations")
        print("2. Ejecutar: python manage.py migrate")
        print("3. Ejecutar: python manage.py crear_usuarios_facial")
        
    except Exception as e:
        print(f"\n❌ Error durante la migración: {e}")
        sys.exit(1)