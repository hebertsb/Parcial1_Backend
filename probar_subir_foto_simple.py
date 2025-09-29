#!/usr/bin/env python3
"""
Script simple para probar solo el endpoint de subir foto
"""

import os
import sys
import django

# Configurar Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.test import Client
import json
from io import BytesIO
from PIL import Image

EMAIL_PROPIETARIO = "propietario.test@example.com"
PASSWORD_PROPIETARIO = "testing123"

def probar_subir_foto():
    """Probar solo el endpoint de subir foto"""
    
    print("📤 PROBANDO ENDPOINT SUBIR-FOTO")
    print("=" * 50)
    
    client = Client()
    
    # 1. Login
    print("🔐 Haciendo login...")
    login_response = client.post('/api/authz/login/', 
                                data=json.dumps({
                                    'email': EMAIL_PROPIETARIO,
                                    'password': PASSWORD_PROPIETARIO
                                }), 
                                content_type='application/json')
    
    if login_response.status_code != 200:
        print(f"❌ Error en login: {login_response.content.decode()}")
        return
    
    # Obtener token
    login_data = login_response.json()
    token = login_data.get('access')
    print(f"✅ Token obtenido")
    
    # Headers de autenticación
    auth_headers = {'HTTP_AUTHORIZATION': f'Bearer {token}'}
    
    # 2. Crear imagen de prueba simple
    print("🖼️ Creando imagen de prueba...")
    
    # Crear imagen en memoria
    img = Image.new('RGB', (50, 50), color='green')
    img_buffer = BytesIO()
    img.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    
    # 3. Subir foto
    print("⬆️ Subiendo foto...")
    
    try:
        # Usar SimpleUploadedFile para simular archivo
        from django.core.files.uploadedfile import SimpleUploadedFile
        
        uploaded_file = SimpleUploadedFile(
            name='test.png',
            content=img_buffer.getvalue(),
            content_type='image/png'
        )
        
        response = client.post('/api/authz/propietarios/subir-foto/',
                             data={'foto': uploaded_file},
                             **auth_headers)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Foto subida exitosamente:")
            foto_data = data.get('data', {})
            print(f"   • URL: {foto_data.get('foto_url', '')[:60]}...")
            print(f"   • Total fotos: {foto_data.get('total_fotos')}")
            print(f"   • ID reconocimiento: {foto_data.get('reconocimiento_id')}")
        else:
            print(f"❌ Error: {response.content.decode()}")
            
    except Exception as e:
        print(f"💥 Error en subida: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    probar_subir_foto()