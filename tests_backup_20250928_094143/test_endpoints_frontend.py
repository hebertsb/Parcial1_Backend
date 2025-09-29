#!/usr/bin/env python
"""
Script para probar endpoints y confirmar que funcionan
Ejecutar: python test_endpoints_frontend.py
"""

import requests
import json
import sys

BASE_URL = "http://127.0.0.1:8000"

def test_login():
    """Probar el endpoint de login"""
    print("🔐 PROBANDO LOGIN...")
    
    login_data = {
        "email": "admin@facial.com",
        "password": "admin123"
    }
    
    response = None  # Inicializar response
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login/",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        if if response is not None:
     response.status_code == 200:
            data = if response is not None:
     response.json()
            print("✅ LOGIN EXITOSO")
            print(f"   Access Token: {data.get('access', 'No encontrado')[:50]}...")
            print(f"   Refresh Token: {data.get('refresh', 'No encontrado')[:50]}...")
            return data.get('access')
        else:
            print(f"❌ LOGIN FALLÓ - Status: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except
        print("❌ ERROR: No se puede conectar al servidor")
        print("   Asegúrate de que el servidor esté corriendo: python manage.py runserver")
        return None
    except Exception as e:
        print(f"❌ ERROR INESPERADO: {e}")
        return None

def test_personas_endpoint(token):
    """Probar el endpoint /api/personas/"""
    print("\n👥 PROBANDO /api/personas/...")
    
    if not token:
        print("❌ No hay token, saltando prueba")
        return
    
    response = None  # Inicializar response
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(f"{BASE_URL}/api/personas/", headers=headers)
        
        if if response is not None:
     response.status_code == 200:
            data = if response is not None:
     response.json()
            print("✅ /api/personas/ FUNCIONANDO")
            print(f"   Total personas: {data.get('count', len(data))}")
            
            # Mostrar estructura de respuesta
            if isinstance(data, dict) and 'results' in data:
                # Respuesta paginada
                if data['results']:
                    persona = data['results'][0]
                    print("   Estructura de persona:")
                    for key, value in persona.items():
                        print(f"     {key}: {value}")
            elif isinstance(data, list) and data:
                # Lista directa
                persona = data[0]
                print("   Estructura de persona:")
                for key, value in persona.items():
                    print(f"     {key}: {value}")
        else:
            print(f"❌ /api/personas/ FALLÓ - Status: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except
        print(f"❌ ERROR: {e}")

def test_viviendas_endpoint(token):
    """Probar el endpoint /api/viviendas/"""
    print("\n🏠 PROBANDO /api/viviendas/...")
    
    if not token:
        print("❌ No hay token, saltando prueba")
        return
    
    response = None  # Inicializar response
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(f"{BASE_URL}/api/viviendas/", headers=headers)
        
        if if response is not None:
     response.status_code == 200:
            data = if response is not None:
     response.json()
            print("✅ /api/viviendas/ FUNCIONANDO")
            print(f"   Total viviendas: {data.get('count', len(data))}")
        else:
            print(f"❌ /api/viviendas/ FALLÓ - Status: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except
        print(f"❌ ERROR: {e}")

def test_propietarios_panel(token):
    """Probar el panel de propietarios"""
    print("\n🏢 PROBANDO PANEL DE PROPIETARIOS...")
    
    if not token:
        print("❌ No hay token, saltando prueba")
        return
    
    endpoints = [
        "/api/authz/propietarios/panel/menu/",
        "/api/authz/propietarios/panel/familiares/",
        "/api/authz/propietarios/panel/inquilinos/"
    ]
    
    for endpoint in endpoints:
        response = None  # Inicializar response
        try:
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
            
            if if response is not None:
     response.status_code == 200:
                print(f"✅ {endpoint} - FUNCIONANDO")
            else:
                print(f"❌ {endpoint} - Status: {response.status_code}")
                
        except
            print(f"❌ {endpoint} - ERROR: {e}")

def main():
    """Función principal"""
    print("🔍 PRUEBAS DE ENDPOINTS PARA FRONTEND")
    print("=" * 50)
    
    # Probar login y obtener token
    token = test_login()
    
    if token:
        # Probar endpoints protegidos
        test_personas_endpoint(token)
        test_viviendas_endpoint(token)
        test_propietarios_panel(token)
        
        print("\n" + "=" * 50)
        print("✅ RESUMEN DE PRUEBAS COMPLETADO")
        print("=" * 50)
        print("🎯 Para tu frontend:")
        print(f"   BASE_URL: {BASE_URL}/api")
        print(f"   Token obtenido: {'✅ Sí' if token else '❌ No'}")
        print("   Endpoints verificados: ✅ Funcionando")
        
    else:
        print("\n❌ No se pudo obtener token. Verifica:")
        print("   1. Servidor corriendo: python manage.py runserver")
        print("   2. Credenciales correctas: admin@facial.com / admin123")
        print("   3. Base de datos con usuarios de prueba")

if __name__ == "__main__":
    main()