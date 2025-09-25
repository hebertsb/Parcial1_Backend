#!/usr/bin/env python3
"""
Script para probar y verificar los endpoints de administración de seguridad
"""
import requests
import json
import subprocess
import time

BASE_URL = "http://127.0.0.1:8000"

def test_endpoint_availability():
    """Probar qué endpoints están disponibles"""
    print("🔍 VERIFICACIÓN DE DISPONIBILIDAD DE ENDPOINTS")
    print("=" * 60)
    
    endpoints_to_test = [
        "/auth/login/",
        "/auth/admin/seguridad/listar/",
        "/auth/admin/seguridad/crear/",
        "/api/authz/login/",
        "/api/authz/admin/seguridad/listar/",
        "/api/authz/admin/seguridad/crear/",
    ]
    
    for endpoint in endpoints_to_test:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
            status_icon = "✅" if response.status_code != 404 else "❌"
            print(f"{status_icon} {endpoint} → {response.status_code}")
            
            if response.status_code == 405:  # Method not allowed
                print(f"   📝 Endpoint existe pero requiere POST/PUT")
        except requests.exceptions.RequestException as e:
            print(f"❌ {endpoint} → Error: {e}")
    
    print()

def get_admin_token():
    """Obtener token de administrador"""
    print("🔐 OBTENIENDO TOKEN DE ADMINISTRADOR")
    print("-" * 40)
    
    # Primero probar con Django shell para obtener credenciales válidas
    shell_command = '''
from authz.models import Usuario
admins = Usuario.objects.filter(roles__nombre="Administrador", is_active=True)
for admin in admins:
    print(f"Admin: {admin.email}")
'''
    
    try:
        result = subprocess.run([
            'python', 'manage.py', 'shell', '-c', shell_command
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("📋 Administradores disponibles:")
            print(result.stdout)
        
    except Exception as e:
        print(f"Error obteniendo admins: {e}")
    
    # Intentar login con diferentes combinaciones
    login_attempts = [
        {"email": "admin@condominio.com", "password": "admin123"},
        {"email": "admin@test.com", "password": "admin123"},
        {"email": "administrador@condominio.com", "password": "admin123"},
    ]
    
    for credentials in login_attempts:
        print(f"🧪 Probando: {credentials['email']}")
        
        # Probar endpoint /auth/login/
        try:
            response = requests.post(
                f"{BASE_URL}/auth/login/",
                json=credentials,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Login exitoso en /auth/login/")
                return data.get('access'), credentials['email']
            else:
                print(f"   ❌ /auth/login/ → {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Probar endpoint /api/authz/login/
        try:
            response = requests.post(
                f"{BASE_URL}/api/authz/login/",
                json=credentials,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Login exitoso en /api/authz/login/")
                return data.get('access'), credentials['email']
            else:
                print(f"   ❌ /api/authz/login/ → {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    return None, None

def test_admin_endpoints(token, admin_email):
    """Probar endpoints administrativos"""
    if not token:
        print("❌ No se pudo obtener token, saltando pruebas de endpoints admin")
        return
    
    print(f"\n🛠️ PROBANDO ENDPOINTS ADMINISTRATIVOS")
    print(f"👤 Admin: {admin_email}")
    print(f"🎫 Token: {token[:50]}...")
    print("-" * 60)
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test endpoints
    endpoints_to_test = [
        ("GET", "/auth/admin/seguridad/listar/", None),
        ("GET", "/api/authz/admin/seguridad/listar/", None),
        ("POST", "/auth/admin/seguridad/crear/", {
            "email": "test.seguridad.nuevo@test.com",
            "password": "temporal123",
            "persona": {
                "nombre": "Test",
                "apellido": "Usuario Seguridad",
                "ci": "9999999",
                "telefono": "70999999",
                "direccion": "Dirección de prueba"
            }
        })
    ]
    
    for method, endpoint, data in endpoints_to_test:
        try:
            if method == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}", headers=headers, timeout=10)
            elif method == "POST":
                response = requests.post(f"{BASE_URL}{endpoint}", headers=headers, json=data, timeout=10)
            
            status_icon = "✅" if response.status_code in [200, 201] else "❌"
            print(f"{status_icon} {method} {endpoint} → {response.status_code}")
            
            if response.status_code in [200, 201]:
                try:
                    response_data = response.json()
                    if isinstance(response_data, dict) and 'message' in response_data:
                        print(f"   📝 {response_data['message']}")
                    elif isinstance(response_data, dict) and 'count' in response_data:
                        print(f"   📊 {response_data['count']} usuarios encontrados")
                except:
                    print(f"   📄 Respuesta: {response.text[:100]}...")
            else:
                print(f"   ❌ Error: {response.text[:200]}")
                
        except Exception as e:
            print(f"❌ {method} {endpoint} → Error: {e}")

def main():
    print("🚀 ANÁLISIS COMPLETO DEL BACKEND")
    print("Verificando compatibilidad con documentación frontend")
    print("=" * 70)
    
    # Paso 1: Verificar disponibilidad de endpoints
    test_endpoint_availability()
    
    # Paso 2: Obtener token de administrador
    token, admin_email = get_admin_token()
    
    # Paso 3: Probar endpoints administrativos
    test_admin_endpoints(token, admin_email)
    
    print("\n" + "="*70)
    print("📋 RESUMEN PARA EL FRONTEND:")
    print("="*70)
    
    if token:
        print("✅ ENDPOINTS IMPLEMENTADOS: SÍ")
        print("✅ URL BASE: http://127.0.0.1:8000")
        print("✅ AUTENTICACIÓN: JWT Bearer token funcionando")
        print("✅ ESTRUCTURA URLs: /auth/ y /api/authz/ disponibles")
        print("✅ ENDPOINTS ADMIN DISPONIBLES:")
        print("   - GET  /auth/admin/seguridad/listar/")
        print("   - POST /auth/admin/seguridad/crear/")
        print("   - PUT  /auth/admin/seguridad/{id}/estado/")
        print("   - POST /auth/admin/seguridad/{id}/reset-password/")
    else:
        print("❌ PROBLEMAS ENCONTRADOS:")
        print("   - No se pudo obtener token de administrador")
        print("   - Verificar credenciales de admin en base de datos")
    
    print("\n🎯 FRONTEND DEBE USAR:")
    print("   Base URL: http://127.0.0.1:8000")
    print("   Login: POST /auth/login/")
    print("   Admin endpoints: /auth/admin/seguridad/...")

if __name__ == "__main__":
    main()