"""
MIGRACIÓN MANUAL DE EMERGENCIA
Usar solo si las migraciones automáticas fallan
"""

import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.db import transaction, connection
from django.contrib.auth import get_user_model


def reset_authz_migrations():
    """Resetea las migraciones de authz para empezar fresh"""
    print("🔄 Reseteando migraciones de authz...")
    
    with connection.cursor() as cursor:
        # Eliminar registros de migraciones de authz
        cursor.execute("DELETE FROM django_migrations WHERE app = 'authz'")
        print("✅ Registros de migración eliminados")


def crear_tablas_nuevas():
    """Crea las nuevas tablas manualmente si es necesario"""
    print("🔄 Verificando/creando nuevas tablas...")
    
    sql_commands = [
        """
        CREATE TABLE IF NOT EXISTS authz_persona (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre VARCHAR(100) NOT NULL,
            apellido VARCHAR(100) NOT NULL,
            documento_identidad VARCHAR(20) UNIQUE NOT NULL,
            telefono VARCHAR(20),
            email VARCHAR(254) NOT NULL,
            fecha_nacimiento DATE,
            genero VARCHAR(1),
            pais VARCHAR(50),
            tipo_persona VARCHAR(20) DEFAULT 'cliente',
            direccion TEXT,
            activo BOOLEAN DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS authz_rol (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre VARCHAR(50) UNIQUE NOT NULL,
            descripcion TEXT,
            activo BOOLEAN DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS authz_relaciones_propietario_inquilino (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            propietario_id INTEGER NOT NULL,
            inquilino_id INTEGER NOT NULL,
            vivienda_id INTEGER NOT NULL,
            fecha_inicio DATE NOT NULL,
            fecha_fin DATE,
            activo BOOLEAN DEFAULT 1,
            monto_alquiler DECIMAL(10,2),
            observaciones TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (propietario_id) REFERENCES auth_user (id),
            FOREIGN KEY (inquilino_id) REFERENCES auth_user (id)
        );
        """
    ]
    
    with connection.cursor() as cursor:
        for sql in sql_commands:
            try:
                cursor.execute(sql)
                print("✅ Tabla creada/verificada")
            except Exception as e:
                print(f"⚠️ Error creando tabla: {e}")


def migrar_usuarios_a_personas():
    """Migra usuarios existentes creando registros de persona"""
    print("🔄 Migrando usuarios existentes...")
    
    User = get_user_model()
    
    with transaction.atomic():
        # Obtener usuarios que no tienen persona asociada
        usuarios_sin_persona = User.objects.filter(persona__isnull=True)
        
        print(f"📊 Usuarios sin persona: {usuarios_sin_persona.count()}")
        
        for usuario in usuarios_sin_persona:
            try:
                # Crear persona para este usuario
                persona_data = {
                    'nombre': getattr(usuario, 'nombres', '') or 'Usuario',
                    'apellido': getattr(usuario, 'apellidos', '') or 'Sistema',
                    'documento_identidad': getattr(usuario, 'documento_identidad', '') or f"USR{usuario.id:04d}",
                    'telefono': getattr(usuario, 'telefono', '') or '',
                    'email': usuario.email,
                    'fecha_nacimiento': getattr(usuario, 'fecha_nacimiento', None),
                    'genero': getattr(usuario, 'genero', '') or '',
                    'pais': getattr(usuario, 'pais', '') or '',
                    'tipo_persona': 'cliente',
                    'direccion': '',
                    'activo': True
                }
                
                # Usar SQL directo para insertar persona
                with connection.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO authz_persona 
                        (nombre, apellido, documento_identidad, telefono, email, fecha_nacimiento, genero, pais, tipo_persona, direccion, activo, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
                    """, [
                        persona_data['nombre'],
                        persona_data['apellido'], 
                        persona_data['documento_identidad'],
                        persona_data['telefono'],
                        persona_data['email'],
                        persona_data['fecha_nacimiento'],
                        persona_data['genero'],
                        persona_data['pais'],
                        persona_data['tipo_persona'],
                        persona_data['direccion'],
                        persona_data['activo']
                    ])
                    
                    persona_id = cursor.lastrowid
                    
                    # Actualizar usuario para asociar persona
                    cursor.execute("""
                        UPDATE auth_user SET persona_id = ? WHERE id = ?
                    """, [persona_id, usuario.id])
                
                print(f"✅ Usuario migrado: {usuario.email}")
                
            except Exception as e:
                print(f"❌ Error migrando usuario {usuario.email}: {e}")


if __name__ == "__main__":
    print("🚨 MIGRACIÓN MANUAL DE EMERGENCIA")
    print("⚠️ Usar solo si las migraciones automáticas fallan")
    
    respuesta = input("¿Continuar? (sí/no): ")
    if respuesta.lower() not in ['sí', 'si', 'yes', 'y']:
        print("❌ Migración cancelada")
        sys.exit(0)
    
    try:
        reset_authz_migrations()
        crear_tablas_nuevas()
        migrar_usuarios_a_personas()
        print("\n✅ Migración manual completada!")
        
    except Exception as e:
        print(f"\n❌ Error durante migración manual: {e}")
        sys.exit(1)