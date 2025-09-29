#!/usr/bin/env python
"""
Script para probar los endpoints de seguridad implementados
"""
import os
import sys
import django
import requests
import json
from datetime import datetime

# Setup Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# Base URL del servidor (ajustar según sea necesario)
BASE_URL = "http://localhost:8000"

def test_endpoint(url, headers=None, description=""):
    """Probar un endpoint específico"""
    print(f"\n🔍 PROBANDO: {description}")
    print(f"📍 URL: {url}")
    
    try:
        response = requests.get(url, headers=headers)
        print(f"✅ Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"📄 Respuesta: {json.dumps(data, indent=2)[:200]}...")
            except:
                print(f"📄 Respuesta: {response.text[:200]}...")
        else:
            print(f"❌ Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: No se puede conectar al servidor")
        print("💡 Asegúrate de que el servidor Django esté ejecutándose:")
        print("   python manage.py runserver")
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")

def get_auth_token():
    """Obtener token de autenticación para pruebas"""
    print("🔐 Obteniendo token de autenticación...")
    
    # Intentar con usuario de seguridad
    login_url = f"{BASE_URL}/api/auth/login/"
    credentials = {
        "email": "seguridad@facial.com",
        "password": "seguridad123"
    }
    
    try:
        response = requests.post(login_url, json=credentials)
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token') or data.get('access')
            if token:
                print("✅ Token obtenido exitosamente")
                return f"Bearer {token}"
        
        print("❌ No se pudo obtener token de autenticación")
        print(f"Respuesta: {response.text}")
        return None
        
    except Exception as e:
        print(f"❌ Error obteniendo token: {str(e)}")
        return None

def main():
    """Función principal de pruebas"""
    print("🚀 INICIANDO PRUEBAS DE ENDPOINTS DE SEGURIDAD")
    print("=" * 60)
    
    # Obtener token de autenticación
    auth_headers = None
    token = get_auth_token()
    if token:
        auth_headers = {"Authorization": token}
    
    # Lista de endpoints a probar
    endpoints = [
        {
            "url": f"{BASE_URL}/seguridad/api/usuarios-reconocimiento/",
            "description": "Lista de usuarios con reconocimiento facial",
            "auth_required": True
        },
        {
            "url": f"{BASE_URL}/api/authz/reconocimiento/fotos/8/",
            "description": "Fotos de reconocimiento del usuario ID 8",
            "auth_required": True
        },
        {
            "url": f"{BASE_URL}/seguridad/api/dashboard/",
            "description": "Dashboard de seguridad",
            "auth_required": True
        },
        {
            "url": f"{BASE_URL}/seguridad/api/incidentes/",
            "description": "Lista de incidentes",
            "auth_required": True
        },
        {
            "url": f"{BASE_URL}/seguridad/api/visitas/activas/",
            "description": "Visitas activas",
            "auth_required": True
        },
        {
            "url": f"{BASE_URL}/seguridad/api/alertas/activas/",
            "description": "Alertas activas",
            "auth_required": True
        },
        {
            "url": f"{BASE_URL}/seguridad/api/lista-usuarios-activos/",
            "description": "Lista de usuarios activos",
            "auth_required": True
        }
    ]
    
    # Probar cada endpoint
    for endpoint in endpoints:
        headers = auth_headers if endpoint["auth_required"] and auth_headers else None
        test_endpoint(endpoint["url"], headers, endpoint["description"])
    
    print("\n" + "=" * 60)
    print("🏁 PRUEBAS COMPLETADAS")
    
    if not auth_headers:
        print("\n⚠️  NOTA: Muchas pruebas fallaron por falta de autenticación")
        print("💡 Para probar con autenticación:")
        print("   1. Asegúrate de que el usuario 'seguridad@facial.com' existe")
        print("   2. Asigna el rol 'security' a este usuario")
        print("   3. Ejecuta el servidor: python manage.py runserver")

if __name__ == "__main__":
    main()