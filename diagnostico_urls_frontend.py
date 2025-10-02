#!/usr/bin/env python3
"""
Script para verificar y diagnosticar el problema de URLs del frontend
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_urls():
    """Probar todas las combinaciones de URLs"""
    print("🔍 DIAGNÓSTICO DE URLs - Frontend vs Backend")
    print("="*60)
    
    # URLs que el frontend está intentando (INCORRECTAS)
    urls_frontend_incorrectas = [
        f"{BASE_URL}/viviendas/",
        f"{BASE_URL}/propiedades/", 
        f"{BASE_URL}/personas/inquilinos/"
    ]
    
    # URLs correctas del backend
    urls_backend_correctas = [
        f"{BASE_URL}/api/viviendas/",
        f"{BASE_URL}/api/propiedades/",
        f"{BASE_URL}/api/personas/inquilinos/"
    ]
    
    # URLs adicionales para probar
    urls_adicionales = [
        f"{BASE_URL}/api/viviendas/estadisticas-frontend/",
        f"{BASE_URL}/api/viviendas/estadisticas/",
        f"{BASE_URL}/api/auth/login/"
    ]
    
    print("\n❌ URLs que Frontend está usando (INCORRECTAS):")
    for url in urls_frontend_incorrectas:
        status = test_single_url(url, with_auth=False)
        print(f"  {url} -> {status}")
    
    print("\n✅ URLs correctas del Backend:")
    token = get_auth_token()
    for url in urls_backend_correctas:
        status = test_single_url(url, with_auth=True, token=token)
        print(f"  {url} -> {status}")
    
    print("\n🎯 URLs adicionales importantes:")
    for url in urls_adicionales:
        if 'login' in url:
            status = test_single_url(url, with_auth=False)
        else:
            status = test_single_url(url, with_auth=True, token=token)
        print(f"  {url} -> {status}")
    
    print("\n" + "="*60)
    print("🚨 PROBLEMA IDENTIFICADO:")
    print("   El frontend NO está usando el prefijo '/api/' en las URLs")
    print("   Frontend usa: http://127.0.0.1:8000/viviendas/")
    print("   Debe usar:    http://127.0.0.1:8000/api/viviendas/")
    print("\n💡 SOLUCIÓN:")
    print("   Verificar configuración de baseURL en el apiClient del frontend")
    print("   Debe ser: 'http://127.0.0.1:8000/api' (CON /api al final)")

def test_single_url(url, with_auth=False, token=None):
    """Probar una URL individual"""
    try:
        headers = {}
        if with_auth and token:
            headers['Authorization'] = f'Bearer {token}'
        
        response = requests.get(url, headers=headers, timeout=5)
        
        if response.status_code == 200:
            try:
                data = response.json()
                if isinstance(data, list):
                    return f"✅ 200 OK ({len(data)} elementos)"
                elif isinstance(data, dict):
                    return f"✅ 200 OK (objeto con {len(data)} campos)"
                else:
                    return "✅ 200 OK"
            except:
                return "✅ 200 OK (respuesta no JSON)"
        elif response.status_code == 401:
            return "🔐 401 Unauthorized (necesita autenticación)"
        elif response.status_code == 404:
            return "❌ 404 Not Found"
        else:
            return f"⚠️  {response.status_code} {response.reason}"
            
    except requests.exceptions.ConnectionError:
        return "💥 Connection Error (¿Django corriendo?)"
    except requests.exceptions.Timeout:
        return "⌛ Timeout"
    except Exception as e:
        return f"❌ Error: {str(e)}"

def get_auth_token():
    """Obtener token de autenticación"""
    try:
        login_url = f"{BASE_URL}/api/auth/login/"
        credentials = {
            "email": "admin@condominio.com", 
            "password": "temporal123"
        }
        
        response = requests.post(login_url, json=credentials, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get('access')
        else:
            print(f"⚠️  No se pudo obtener token: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error obteniendo token: {e}")
        return None

def check_django_running():
    """Verificar si Django está ejecutándose"""
    try:
        response = requests.get(f"{BASE_URL}/admin/", timeout=3)
        if response.status_code in [200, 302]:  # 302 es redirect a login
            return True
    except:
        pass
    return False

def main():
    print("🚀 DIAGNÓSTICO COMPLETO DEL PROBLEMA FRONTEND")
    print("Este script identificará exactamente por qué el frontend no funciona")
    print()
    
    # Verificar si Django está corriendo
    if not check_django_running():
        print("❌ Django no está ejecutándose en http://127.0.0.1:8000")
        print("   Ejecuta: python manage.py runserver")
        return
    
    print("✅ Django está ejecutándose")
    
    # Ejecutar pruebas
    test_urls()
    
    print("\n🔧 PRÓXIMOS PASOS:")
    print("1. Buscar archivo de configuración apiClient en el frontend")
    print("2. Cambiar baseURL de 'http://127.0.0.1:8000' a 'http://127.0.0.1:8000/api'")
    print("3. O verificar que las llamadas incluyan '/api/' en la ruta")

if __name__ == "__main__":
    main()