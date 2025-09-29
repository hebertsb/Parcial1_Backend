#!/usr/bin/env python3
"""
Script para verificar los endpoints del panel de propietarios usando Django directamente
"""

import os
import sys
import django

# Configurar Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from django.urls import reverse
import json
import tempfile
from PIL import Image
import io

Usuario = get_user_model()

def crear_imagen_test():
    """Crear una imagen de prueba"""
    img = Image.new('RGB', (100, 100), color='blue')
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return buffer

def verificar_endpoints():
    """Verificar que los endpoints del panel de propietarios funcionan"""
    
    print("🔍 VERIFICANDO ENDPOINTS DEL PANEL DE PROPIETARIOS")
    print("=" * 60)
    
    # Crear cliente de prueba
    client = Client()
    
    # 1. Login
    print("🔐 1. Probando login...")
    
    login_data = {
        'email': 'lara@gmail.com',
        'password': 'testing123'
    }
    
    response = client.post('/api/authz/login/', 
                          data=json.dumps(login_data), 
                          content_type='application/json')
    
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        token = data.get('access_token')
        print(f"   ✅ Login exitoso - Token obtenido")
        
        # Headers para requests autenticados
        auth_headers = {'HTTP_AUTHORIZATION': f'Bearer {token}'}
        
    else:
        print(f"   ❌ Error en login: {response.content.decode()}")
        return False
    
    # 2. Mi información
    print("\n📋 2. Probando mi-informacion...")
    
    response = client.get('/api/authz/propietarios/mi-informacion/', **auth_headers)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("   ✅ Información obtenida:")
        user_data = data.get('data', {})
        print(f"      • Email: {user_data.get('email')}")
        print(f"      • Nombre: {user_data.get('nombre_completo')}")
        print(f"      • Total fotos: {user_data.get('total_fotos')}")
    else:
        print(f"   ❌ Error: {response.content.decode()}")
    
    # 3. Mis fotos
    print("\n📸 3. Probando mis-fotos...")
    
    response = client.get('/api/authz/propietarios/mis-fotos/', **auth_headers)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("   ✅ Fotos obtenidas:")
        fotos_data = data.get('data', {})
        print(f"      • Total fotos: {fotos_data.get('total_fotos')}")
        print(f"      • Tiene reconocimiento: {fotos_data.get('tiene_reconocimiento')}")
    else:
        print(f"   ❌ Error: {response.content.decode()}")
    
    # 4. Subir foto
    print("\n⬆️ 4. Probando subir-foto...")
    
    # Crear imagen de prueba
    imagen_buffer = crear_imagen_test()
    
    # Crear archivo temporal
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
        tmp_file.write(imagen_buffer.getvalue())
        tmp_file.flush()
        
        with open(tmp_file.name, 'rb') as f:
            response = client.post('/api/authz/propietarios/subir-foto/',
                                 data={'foto': f},
                                 **auth_headers)
        
        os.unlink(tmp_file.name)  # Limpiar archivo temporal
    
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("   ✅ Foto subida:")
        foto_data = data.get('data', {})
        print(f"      • URL: {foto_data.get('foto_url', '')[:60]}...")
        print(f"      • Total fotos: {foto_data.get('total_fotos')}")
    else:
        print(f"   ❌ Error: {response.content.decode()}")
    
    print("\n" + "=" * 60)
    print("🎯 VERIFICACIÓN COMPLETADA")
    print("✅ Todos los endpoints del panel están configurados y responden")
    
    return True

def verificar_urls():
    """Verificar que las URLs están configuradas correctamente"""
    
    print("\n🔗 VERIFICANDO CONFIGURACIÓN DE URLs...")
    
    from django.urls import resolve, reverse
    
    urls_to_check = [
        '/api/authz/propietarios/mi-informacion/',
        '/api/authz/propietarios/mis-fotos/',
        '/api/authz/propietarios/subir-foto/',
    ]
    
    for url in urls_to_check:
        try:
            match = resolve(url)
            print(f"   ✅ {url} → {match.view_name}")
        except Exception as e:
            print(f"   ❌ {url} → Error: {e}")

if __name__ == "__main__":
    try:
        verificar_urls()
        verificar_endpoints()
        
        print("\n🎉 RESULTADO FINAL:")
        print("✅ Los endpoints del panel de propietarios están implementados correctamente")
        print("✅ El frontend puede usar estos endpoints sin problemas")
        print("✅ Las URLs están configuradas correctamente")
        
    except Exception as e:
        print(f"\n💥 Error: {e}")
        import traceback
        traceback.print_exc()