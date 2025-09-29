# 🔍 VERIFICACIÓN DIRECTA DE BASE DE DATOS

import os
import sys
import django

# Configurar Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.db import connection

def verificar_base_datos_directa():
    """🔍 Verificación directa con SQL"""
    print("=" * 60)
    print("🔍 VERIFICACIÓN DIRECTA DE BASE DE DATOS")
    print("=" * 60)
    
    with connection.cursor() as cursor:
        
        # 1. Verificar usuario ID 8
        print("1. VERIFICANDO USUARIO ID 8:")
        cursor.execute("""
            SELECT u.id, u.email, p.id as persona_id, p.nombre, p.apellido 
            FROM authz_usuario u 
            LEFT JOIN authz_persona p ON u.persona_id = p.id 
            WHERE u.id = 8
        """)
        resultado_usuario = cursor.fetchone()
        
        if resultado_usuario:
            user_id, email, persona_id, nombre, apellido = resultado_usuario
            print(f"   ✅ Usuario: ID {user_id}, Email: {email}")
            print(f"   ✅ Persona: ID {persona_id}, Nombre: {nombre} {apellido}")
        else:
            print("   ❌ Usuario ID 8 no encontrado")
            return
        
        # 2. Verificar rol propietario
        print("\n2. VERIFICANDO ROL PROPIETARIO:")
        cursor.execute("""
            SELECT r.nombre 
            FROM authz_usuario_roles ur 
            JOIN authz_rol r ON ur.rol_id = r.id 
            WHERE ur.usuario_id = 8 AND r.nombre = 'Propietario'
        """)
        rol_result = cursor.fetchone()
        
        if rol_result:
            print(f"   ✅ Tiene rol: {rol_result[0]}")
        else:
            print("   ❌ NO tiene rol Propietario")
        
        # 3. Verificar tabla ReconocimientoFacial - estructura
        print("\n3. VERIFICANDO ESTRUCTURA DE TABLA:")
        cursor.execute("PRAGMA table_info(reconocimiento_facial)")
        columnas = cursor.fetchall()
        
        print("   📋 Columnas en reconocimiento_facial:")
        for col in columnas:
            print(f"      - {col[1]} ({col[2]})")
        
        # 4. Buscar registros por persona_id
        print(f"\n4. BUSCANDO REGISTROS POR persona_id = {persona_id}:")
        cursor.execute("""
            SELECT id, persona_id, copropietario_id, fotos_urls, 
                   imagen_referencia_url, fecha_actualizacion
            FROM reconocimiento_facial 
            WHERE persona_id = ?
        """, [persona_id])
        
        registros_persona = cursor.fetchall()
        print(f"   📊 Registros encontrados: {len(registros_persona)}")
        
        for registro in registros_persona:
            reg_id, p_id, cop_id, fotos_urls, img_url, fecha = registro
            print(f"      📋 Registro ID {reg_id}:")
            print(f"         - persona_id: {p_id}")
            print(f"         - copropietario_id: {cop_id}")
            print(f"         - fotos_urls: {fotos_urls[:50] if fotos_urls else 'NULL'}...")
            print(f"         - imagen_referencia_url: {img_url[:50] if img_url else 'NULL'}...")
            print(f"         - fecha_actualizacion: {fecha}")
        
        # 5. Buscar TODOS los registros para debug
        print(f"\n5. TODOS LOS REGISTROS EN LA TABLA:")
        cursor.execute("""
            SELECT id, persona_id, copropietario_id, 
                   CASE 
                       WHEN fotos_urls IS NOT NULL THEN 'HAS_DATA' 
                       ELSE 'NULL' 
                   END as fotos_status
            FROM reconocimiento_facial
        """)
        
        todos_registros = cursor.fetchall()
        print(f"   📊 Total registros en tabla: {len(todos_registros)}")
        
        for registro in todos_registros:
            reg_id, p_id, cop_id, fotos_status = registro
            print(f"      - ID {reg_id}: persona_id={p_id}, coprop_id={cop_id}, fotos={fotos_status}")

if __name__ == '__main__':
    verificar_base_datos_directa()