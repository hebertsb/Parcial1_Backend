#!/usr/bin/env python
"""
Probar endpoint de diagnóstico
"""
import requests
import json

def probar_diagnostico():
    print("🔍 PROBANDO ENDPOINT DE DIAGNÓSTICO")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    diagnostico_url = f"{base_url}/api/authz/usuarios/diagnostico/"
    
    # Obtener token
    login_url = f"{base_url}/api/authz/login/"
    credentials = {"email": "test@facial.com", "password": "test123"}
    
    try:
        login_response = requests.post(login_url, json=credentials)
        if login_response.status_code != 200:
            print(f"❌ Error en login: {login_response.status_code}")
            return
        
        token = login_response.json().get('access')
        headers = {'Authorization': f'Bearer {token}'}
        
        print("🧪 1. PROBANDO GET:")
        get_response = requests.get(diagnostico_url, headers=headers)
        print(f"   Status: {get_response.status_code}")
        if get_response.status_code == 200:
            print(f"   ✅ GET funciona: {get_response.json()}")
        else:
            print(f"   ❌ GET falló: {get_response.text}")
        
        print("\n🧪 2. PROBANDO POST:")
        post_data = {'usuario_id': '8', 'test': 'data'}
        post_response = requests.post(diagnostico_url, headers=headers, json=post_data)
        print(f"   Status: {post_response.status_code}")
        if post_response.status_code == 200:
            print(f"   ✅ POST funciona: {post_response.json()}")
        else:
            print(f"   ❌ POST falló: {post_response.text}")
            
        # Ahora probar el endpoint original
        print("\n🧪 3. PROBANDO ENDPOINT ORIGINAL:")
        original_url = f"{base_url}/api/authz/usuarios/fotos-reconocimiento/"
        
        # Solo POST (el endpoint real solo acepta POST)
        files = {'fotos': ('test.jpg', b'fake_image_data', 'image/jpeg')}
        data = {'usuario_id': '8'}
        
        original_response = requests.post(original_url, headers=headers, data=data, files=files)
        print(f"   Status: {original_response.status_code}")
        if original_response.status_code == 405:
            print("   ❌ AÚN 405 - Hay problema de configuración")
        elif original_response.status_code == 200:
            print("   ✅ ¡FUNCIONA! El endpoint original está bien")
        elif original_response.status_code == 400:
            print("   ⚠️ Error de validación (normal con datos de prueba)")
        else:
            print(f"   ⚠️ Otro código: {original_response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    probar_diagnostico()