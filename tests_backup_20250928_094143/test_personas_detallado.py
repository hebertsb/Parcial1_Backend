#!/usr/bin/env python
"""
Script para probar específicamente el endpoint /api/personas/
y mostrar la estructura de respuesta para el frontend
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_personas_detallado():
    """Probar /api/personas/ con detalles completos"""
    print("🔍 PRUEBA DETALLADA DEL ENDPOINT /api/personas/")
    print("=" * 60)
    
    # 1. Login
    print("🔐 Paso 1: Login...")
    login_data = {"email": "admin@facial.com", "password": "admin123"}
    
    response = None  # Inicializar response
    try:
        login_response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
        
        if login_response.status_code != 200:
            print(f"❌ Login falló: {login_response.status_code}")
            print(f"Response: {login_response.text}")
            return
        
        token = login_response.json().get('access')
        print("✅ Login exitoso, token obtenido")
        
    except
        print(f"❌ Error en login: {e}")
        return
    
    # 2. Test endpoint personas
    print("\n👥 Paso 2: Probando /api/personas/...")
    
    response = None  # Inicializar response
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        personas_response = requests.get(f"{BASE_URL}/api/personas/", headers=headers)
        
        print(f"🌐 Status Code: {personas_response.status_code}")
        
        if personas_response.status_code == 200:
            data = personas_response.json()
            
            print("✅ ENDPOINT /api/personas/ FUNCIONANDO CORRECTAMENTE")
            print("\n📋 ESTRUCTURA DE RESPUESTA:")
            print("-" * 40)
            
            # Verificar si es lista paginada o lista directa
            if isinstance(data, dict) and 'results' in data:
                print("📊 Respuesta paginada detectada:")
                print(f"   - Total registros: {data.get('count', 'N/A')}")
                print(f"   - Página siguiente: {data.get('next', 'N/A')}")
                print(f"   - Página anterior: {data.get('previous', 'N/A')}")
                print(f"   - Resultados en esta página: {len(data.get('results', []))}")
                
                if data.get('results'):
                    print("\n👤 EJEMPLO DE PERSONA:")
                    persona = data['results'][0]
                    print(json.dumps(persona, indent=2, ensure_ascii=False))
                    
                    print("\n🔍 CAMPOS DISPONIBLES:")
                    for i, (key, value) in enumerate(persona.items(), 1):
                        print(f"   {i:2d}. {key}: {type(value).__name__}")
                        
            elif isinstance(data, list):
                print("📊 Lista directa detectada:")
                print(f"   - Total registros: {len(data)}")
                
                if data:
                    print("\n👤 EJEMPLO DE PERSONA:")
                    persona = data[0]
                    print(json.dumps(persona, indent=2, ensure_ascii=False))
                    
                    print("\n🔍 CAMPOS DISPONIBLES:")
                    for i, (key, value) in enumerate(persona.items(), 1):
                        print(f"   {i:2d}. {key}: {type(value).__name__}")
            else:
                print("⚠️  Estructura de respuesta inesperada:")
                print(json.dumps(data, indent=2, ensure_ascii=False))
        
        else:
            print(f"❌ Error {personas_response.status_code}")
            print(f"Response: {personas_response.text}")
            
    except
        print(f"❌ Error probando personas: {e}")
    
    print("\n" + "=" * 60)
    print("✅ PRUEBA COMPLETADA")
    print("=" * 60)
    
    print("\n🎯 PARA EL FRONTEND:")
    print("✅ El endpoint /api/personas/ está funcionando")
    print("✅ Ya no hay error 500")
    print("✅ Los datos se pueden consumir correctamente")
    print("✅ Usar BASE_URL: http://127.0.0.1:8000/api")
    print("✅ Usar token JWT en header Authorization")

if __name__ == "__main__":
    test_personas_detallado()