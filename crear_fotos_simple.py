#!/usr/bin/env python3
"""
Script simplificado para crear fotos
"""

import os
import sys
import django
import json

# Setup Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.db import connection
from authz.models import Usuario
from seguridad.models import Copropietarios

def crear_fotos_simple():
    print('🔧 CREANDO FOTOS PARA USUARIO ID 8')
    print('=' * 50)
    
    # Obtener copropietario
    copropietario = Copropietarios.objects.filter(usuario_sistema_id=8).first()
    if not copropietario:
        print('❌ Copropietario no encontrado')
        return False
    
    print(f'✅ Copropietario: {copropietario.nombres} {copropietario.apellidos} (ID: {copropietario.id})')
    
    # URLs de fotos
    urls_fotos = [
        "https://dropbox.com/s/test1/tito_foto1.jpg",
        "https://dropbox.com/s/test2/tito_foto2.jpg", 
        "https://dropbox.com/s/test3/tito_foto3.jpg",
        "https://dropbox.com/s/test4/tito_foto4.jpg",
        "https://dropbox.com/s/test5/tito_foto5.jpg"
    ]
    
    # Usar raw SQL simple
    with connection.cursor() as cursor:
        # Eliminar existente
        cursor.execute("DELETE FROM reconocimiento_facial WHERE copropietario_id = %s", [copropietario.id])
        
        # Insertar nuevo
        cursor.execute("""
            INSERT INTO reconocimiento_facial (
                copropietario_id, proveedor_ia, vector_facial, imagen_referencia_url,
                activo, fecha_enrolamiento, fecha_modificacion, fecha_actualizacion,
                intentos_verificacion, fotos_urls
            ) VALUES (%s, %s, %s, %s, %s, datetime('now'), datetime('now'), datetime('now'), %s, %s)
        """, [
            copropietario.id,
            'Local',
            json.dumps(urls_fotos),
            urls_fotos[0],
            1,
            0,
            json.dumps(urls_fotos)
        ])
        
        # Verificar
        cursor.execute("SELECT id, fotos_urls FROM reconocimiento_facial WHERE copropietario_id = %s", [copropietario.id])
        result = cursor.fetchone()
        
        if result:
            rec_id, fotos_db = result
            fotos_count = len(json.loads(fotos_db)) if fotos_db else 0
            print(f'✅ Registro creado: ID {rec_id}, {fotos_count} fotos')
            return True
        else:
            print('❌ Error creando registro')
            return False

def probar_endpoint():
    print(f'\n🧪 PROBANDO ENDPOINT:')
    print('=' * 30)
    
    import requests
    
    try:
        # Token
        response = requests.post('http://127.0.0.1:8000/api/auth/login/', 
                               json={'email': 'seguridad@facial.com', 'password': 'seguridad123'})
        token = response.json()['access']
        headers = {'Authorization': f'Bearer {token}'}
        
        # Endpoint
        response = requests.get('http://127.0.0.1:8000/seguridad/api/usuarios-reconocimiento/', headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            total = len(data['data'])
            print(f'✅ Endpoint OK - Total usuarios: {total}')
            
            # Buscar usuario 8
            for user in data['data']:
                if user.get('usuario_id') == 8 or 'tito@gmail.com' in user.get('email', ''):
                    print(f'🎉 ¡Usuario ID 8 encontrado!')
                    print(f'   Email: {user.get("email")}')
                    print(f'   Nombre: {user.get("nombres_completos")}')
                    return True
            
            print('❌ Usuario ID 8 no encontrado en el endpoint')
            return False
        else:
            print(f'❌ Error: {response.status_code}')
            return False
            
    except Exception as e:
        print(f'❌ Error: {e}')
        return False

if __name__ == "__main__":
    if crear_fotos_simple():
        probar_endpoint()