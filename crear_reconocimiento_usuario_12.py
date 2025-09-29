#!/usr/bin/env python
"""
Crear reconocimiento facial para usuario 12 directamente
"""

import os
import sys
import django

# Configurar Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.db import connection
from authz.models import Usuario
from seguridad.models import Copropietarios
from datetime import datetime
import json

def crear_reconocimiento_usuario_12():
    try:
        usuario = Usuario.objects.get(id=12)
        copropietario = Copropietarios.objects.get(usuario_sistema=usuario) 
        
        cursor = connection.cursor()
        
        fotos_urls = [
            'https://demo.com/foto1.jpg',
            'https://demo.com/foto2.jpg',
            'https://demo.com/foto3.jpg',
            'https://demo.com/foto4.jpg',
            'https://demo.com/foto5.jpg'
        ]
        
        now = datetime.now()
        
        # Verificar si ya existe
        cursor.execute('SELECT id FROM reconocimiento_facial WHERE copropietario_id = ?', [copropietario.id])
        existing = cursor.fetchone()
        
        if existing:
            print(f"Ya existe reconocimiento facial para copropietario {copropietario.id}")
            return
        
        # Insertar nuevo registro
        sql = '''
            INSERT INTO reconocimiento_facial 
            (copropietario_id, proveedor_ia, vector_facial, activo, 
             fecha_enrolamiento, fecha_modificacion, intentos_verificacion, 
             fotos_urls, fecha_actualizacion)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        
        params = [
            copropietario.id,
            'Local',
            'demo_vector_usuario_12',
            1,  # activo (boolean como integer)
            now,
            now,
            0,  # intentos_verificacion
            json.dumps(fotos_urls),
            now
        ]
        
        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            connection.commit()
        
        print(f'✅ ReconocimientoFacial creado exitosamente!')
        print(f'   Usuario ID: {usuario.id}')
        print(f'   Email: {usuario.email}')
        print(f'   Copropietario ID: {copropietario.id}')
        print(f'   Nombre: {copropietario.nombres} {copropietario.apellidos}')
        print(f'   Total fotos: {len(fotos_urls)}')
        
    except Exception as e:
        print(f'❌ Error: {e}')

if __name__ == "__main__":
    crear_reconocimiento_usuario_12()