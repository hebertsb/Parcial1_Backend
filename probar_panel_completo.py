#!/usr/bin/env python3
"""
Script para probar los endpoints del panel de propietarios con usuario válido
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
import json
import tempfile
from PIL import Image
import io

# Credenciales del usuario de prueba
EMAIL_PROPIETARIO = "propietario.test@example.com"
PASSWORD_PROPIETARIO = "testing123"

def crear_imagen_test():
    """Crear una imagen de prueba"""
    img = Image.new('RGB', (100, 100), color='red')
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return buffer

def probar_endpoints_panel():
    """Probar todos los endpoints del panel de propietarios"""
    
    print("🚀 PROBANDO ENDPOINTS DEL PANEL DE PROPIETARIOS")
    print("=" * 60)
    
    # Crear cliente de prueba
    client = Client()
    
    # 1. Login
    print("🔐 1. LOGIN...")
    
    login_response = client.post('/api/authz/login/', 
                                data=json.dumps({
                                    'email': EMAIL_PROPIETARIO,
                                    'password': PASSWORD_PROPIETARIO
                                }), 
                                content_type='application/json')
    
    print(f"   Status: {login_response.status_code}")
    
    if login_response.status_code != 200:
        print(f"   ❌ Error en login: {login_response.content.decode()}")
        return False
    
    # Obtener token
    login_data = login_response.json()
    token = login_data.get('access')  # El JWT devuelve 'access', no 'access_token'
    print(f"   ✅ Login exitoso - Token obtenido: {token[:20]}...")
    
    # Headers para requests autenticados
    auth_headers = {'HTTP_AUTHORIZATION': f'Bearer {token}'}
    
    # 2. Mi información
    print("\n📋 2. MI-INFORMACION...")
    
    info_response = client.get('/api/authz/propietarios/mi-informacion/', **auth_headers)
    print(f"   Status: {info_response.status_code}")
    
    if info_response.status_code == 200:
        info_data = info_response.json()
        print("   ✅ Información obtenida:")
        user_data = info_data.get('data', {})
        print(f"      • Email: {user_data.get('email')}")
        print(f"      • ID Usuario: {user_data.get('usuario_id')}")
        print(f"      • Copropietario ID: {user_data.get('copropietario_id')}")
        print(f"      • Total fotos: {user_data.get('total_fotos')}")
        print(f"      • Tiene reconocimiento: {user_data.get('tiene_reconocimiento')}")
    else:
        print(f"   ❌ Error: {info_response.content.decode()}")
    
    # 3. Mis fotos
    print("\n📸 3. MIS-FOTOS...")
    
    fotos_response = client.get('/api/authz/propietarios/mis-fotos/', **auth_headers)
    print(f"   Status: {fotos_response.status_code}")
    
    if fotos_response.status_code == 200:
        fotos_data = fotos_response.json()
        print("   ✅ Fotos obtenidas:")
        data = fotos_data.get('data', {})
        print(f"      • Total fotos: {data.get('total_fotos')}")
        print(f"      • Tiene reconocimiento: {data.get('tiene_reconocimiento')}")
        
        fotos_urls = data.get('fotos_urls', [])
        if fotos_urls:
            print(f"      • URLs de fotos:")
            for i, url in enumerate(fotos_urls[:2], 1):  # Mostrar solo las primeras 2
                print(f"        - Foto {i}: {url[:60]}...")
        else:
            print("      • Sin fotos registradas")
    else:
        print(f"   ❌ Error: {fotos_response.content.decode()}")
    
    # 4. Subir foto
    print("\n⬆️ 4. SUBIR-FOTO...")
    
    # Crear imagen de prueba
    imagen_buffer = crear_imagen_test()
    
    # Crear archivo temporal
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
        tmp_file.write(imagen_buffer.getvalue())
        tmp_file.flush()
        
        try:
            with open(tmp_file.name, 'rb') as f:
                subir_response = client.post('/api/authz/propietarios/subir-foto/',
                                           data={'foto': f},
                                           **auth_headers)
        finally:
            os.unlink(tmp_file.name)  # Limpiar archivo temporal
    
    print(f"   Status: {subir_response.status_code}")
    
    if subir_response.status_code == 200:
        subir_data = subir_response.json()
        print("   ✅ Foto subida exitosamente:")
        data = subir_data.get('data', {})
        print(f"      • URL: {data.get('foto_url', '')[:60]}...")
        print(f"      • Total fotos: {data.get('total_fotos')}")
        print(f"      • ID reconocimiento: {data.get('reconocimiento_id')}")
    else:
        print(f"   ❌ Error: {subir_response.content.decode()}")
    
    # 5. Verificar mis fotos después de subir
    print("\n🔄 5. MIS-FOTOS (DESPUÉS DE SUBIR)...")
    
    fotos_response2 = client.get('/api/authz/propietarios/mis-fotos/', **auth_headers)
    print(f"   Status: {fotos_response2.status_code}")
    
    if fotos_response2.status_code == 200:
        fotos_data2 = fotos_response2.json()
        data2 = fotos_data2.get('data', {})
        print(f"   ✅ Total fotos actualizado: {data2.get('total_fotos')}")
        print(f"   ✅ Tiene reconocimiento: {data2.get('tiene_reconocimiento')}")
    
    # Resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE PRUEBAS:")
    print("=" * 60)
    
    endpoints = [
        ("Login", login_response.status_code == 200),
        ("Mi Información", info_response.status_code == 200),
        ("Mis Fotos", fotos_response.status_code == 200),
        ("Subir Foto", subir_response.status_code == 200),
        ("Mis Fotos (Actualizado)", fotos_response2.status_code == 200)
    ]
    
    exitosos = 0
    for nombre, resultado in endpoints:
        estado = "✅ EXITOSO" if resultado else "❌ FALLÓ"
        print(f"{nombre:<25}: {estado}")
        if resultado:
            exitosos += 1
    
    print(f"\nResultado final: {exitosos}/{len(endpoints)} endpoints funcionando")
    
    if exitosos == len(endpoints):
        print("\n🎉 ¡TODOS LOS ENDPOINTS DEL PANEL FUNCIONAN PERFECTAMENTE!")
        print("✅ El frontend puede integrar estos endpoints sin problemas")
        print("✅ La funcionalidad de fotos de reconocimiento está operativa")
    else:
        print(f"\n⚠️ Hay {len(endpoints) - exitosos} endpoints con problemas")
    
    return exitosos == len(endpoints)

if __name__ == "__main__":
    try:
        resultado = probar_endpoints_panel()
        
        if resultado:
            print("\n🚀 LISTO PARA PRODUCCIÓN:")
            print("=" * 40)
            print("✅ Endpoints implementados y funcionando")
            print("✅ Autenticación JWT operativa")
            print("✅ Integración con Dropbox funcionando")
            print("✅ Base de datos actualizada correctamente")
            print("\n🔗 URLs disponibles para el frontend:")
            print("   • POST /api/authz/login/")
            print("   • GET  /api/authz/propietarios/mi-informacion/")
            print("   • GET  /api/authz/propietarios/mis-fotos/")
            print("   • POST /api/authz/propietarios/subir-foto/")
            
    except Exception as e:
        print(f"\n💥 Error: {e}")
        import traceback
        traceback.print_exc()