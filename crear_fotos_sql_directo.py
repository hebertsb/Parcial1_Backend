#!/usr/bin/env python3
"""
Script para crear fotos usando SQL directo
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
from seguridad.models import Copropietarios, ReconocimientoFacial

def crear_fotos_sql_directo():
    print('🔧 CREANDO FOTOS USANDO SQL DIRECTO')
    print('=' * 60)
    
    # Obtener copropietario del usuario ID 8
    copropietario = Copropietarios.objects.filter(usuario_sistema_id=8).first()
    if not copropietario:
        print('❌ Copropietario para usuario ID 8 no encontrado')
        return
    
    print(f'✅ Copropietario: {copropietario.nombres} {copropietario.apellidos} (ID: {copropietario.id})')
    
    # URLs de fotos de ejemplo
    urls_fotos = [
        "https://dropbox.com/s/test1/tito_foto1.jpg",
        "https://dropbox.com/s/test2/tito_foto2.jpg", 
        "https://dropbox.com/s/test3/tito_foto3.jpg",
        "https://dropbox.com/s/test4/tito_foto4.jpg",
        "https://dropbox.com/s/test5/tito_foto5.jpg"
    ]
    
    cursor = connection.cursor()
    
    # Eliminar registro existente si existe
    cursor.execute("DELETE FROM reconocimiento_facial WHERE copropietario_id = ?", [copropietario.id])
    print('🗑️ Eliminado registro existente (si existía)')
    
    # Insertar nuevo registro con todos los campos requeridos
    from django.utils import timezone
    now = timezone.now().isoformat()
    
    cursor.execute("""
        INSERT INTO reconocimiento_facial (
            copropietario_id, 
            proveedor_ia, 
            vector_facial, 
            imagen_referencia_url,
            activo, 
            fecha_enrolamiento, 
            fecha_modificacion,
            fecha_actualizacion,
            intentos_verificacion,
            fotos_urls
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, [
        copropietario.id,
        'Local',
        json.dumps(urls_fotos),
        urls_fotos[0],
        1,  # activo = True
        now,
        now,
        now,  # fecha_actualizacion
        0,  # intentos_verificacion
        json.dumps(urls_fotos)  # fotos_urls
    ])
    
    print(f'✅ Registro creado exitosamente con {len(urls_fotos)} fotos')
    
    # Verificar inserción
    cursor.execute("SELECT id, fotos_urls FROM reconocimiento_facial WHERE copropietario_id = ?", [copropietario.id])
    result = cursor.fetchone()
    if result:
        reconocimiento_id, fotos_urls_db = result
        fotos_count = len(json.loads(fotos_urls_db)) if fotos_urls_db else 0
        print(f'✅ Verificación: ID {reconocimiento_id}, {fotos_count} fotos en fotos_urls')
    
    return True

def probar_endpoint_ahora():
    print(f'\n🧪 PROBANDO ENDPOINT usuarios-reconocimiento:')
    print('=' * 50)
    
    import requests
    
    # Obtener token
    response = requests.post('http://127.0.0.1:8000/api/auth/login/', json={
        'email': 'seguridad@facial.com', 
        'password': 'seguridad123'
    })
    
    if response.status_code != 200:
        print('❌ Error obteniendo token')
        return
    
    token = response.json()['access']
    headers = {'Authorization': f'Bearer {token}'}
    
    # Probar endpoint
    response = requests.get('http://127.0.0.1:8000/seguridad/api/usuarios-reconocimiento/', headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        total = len(data['data'])
        print(f'✅ Endpoint funcionando - Total usuarios: {total}')
        
        # Buscar usuario ID 8
        usuario_8_encontrado = False
        for user in data['data']:
            if user.get('usuario_id') == 8:
                usuario_8_encontrado = True
                print(f'🎉 ¡Usuario ID 8 encontrado!')
                print(f'   Email: {user.get("email")}')
                print(f'   Nombre: {user.get("nombres_completos")}')
                if 'reconocimiento_facial' in user:
                    fotos = user['reconocimiento_facial'].get('total_fotos', 0)
                    print(f'   Total fotos: {fotos}')
                break
        
        if not usuario_8_encontrado:
            print('❌ Usuario ID 8 aún no aparece en el endpoint')
            print(f'Usuarios que aparecen:')
            for user in data['data']:
                print(f'  - ID: {user.get("usuario_id", "N/A")}, Email: {user.get("email", "N/A")}')
    else:
        print(f'❌ Error en endpoint: {response.status_code} - {response.text[:200]}')

if __name__ == "__main__":
    if crear_fotos_sql_directo():
        probar_endpoint_ahora()